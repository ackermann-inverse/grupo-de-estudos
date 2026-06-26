"""POC3 - Memória com operações explícitas e governança mínima.

A palavra "memória" é vaga. Aqui ela é um SISTEMA com operações nomeadas, não
"um vector DB" e não "o histórico do chat":

    write / retrieve / update / invalidate / expire / forget / audit

E com política: o que merece ser memorizado, quem pode escrever, proveniência,
confiança, temporalidade, expiração, isolamento por usuário/tenant.

A POC mostra 4 casos que separam "persistir mensagens" de "ter memória":
  (1) uma memória útil é recuperada;
  (2) uma memória irrelevante é ignorada (abaixo do threshold);
  (3) uma memória antiga/conflitante é INVALIDADA e a nova prevalece;
  (4) recuperar TUDO produz uma resposta pior do que recuperar o que importa.

Rode:
    python demos/poc3_memory/memory.py
    USE_MOCK=1 python demos/poc3_memory/memory.py   # sem baixar modelo
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ollama_client import make_client  # noqa: E402
from common.textutil import approx_tokens, cosine  # noqa: E402
from common.tracing import banner, enabled, explain_card, set_output, span, traced  # noqa: E402

# "Agora" fixo para a demo ser determinística (recência reproduzível).
HOJE = date(2026, 6, 16)


def _dias(d: str) -> int:
    y, m, day = (int(x) for x in d.split("-"))
    return (HOJE - date(y, m, day)).days


@dataclass
class MemoryItem:
    id: str
    user: str
    tenant: str
    scope: str          # session | persistent
    kind: str           # fact | preference | episode
    text: str
    topic: str          # chave de conflito (ex.: "endereco_entrega")
    source: str         # user_confirmed | tool | model_guess
    confidence: float   # 0..1
    created: str        # AAAA-MM-DD
    importance: float = 0.5
    ttl_days: int | None = None
    status: str = "active"   # active | invalidated | expired
    embedding: list[float] = field(default_factory=list)

    def is_expired(self, today: date = HOJE) -> bool:
        if self.ttl_days is None:
            return False
        return _dias(self.created) > self.ttl_days


class Memory:
    """Memória de sessão + persistente com auditoria. Store em JSON é opcional;
    aqui mantemos em processo para a demo ser autocontida."""

    def __init__(self, client) -> None:
        self.client = client
        self.items: list[MemoryItem] = []
        self.audit: list[dict] = []
        self._seq = 0

    # ---- WRITE (com política de escrita) ---------------------------------- #
    def write(self, *, user: str, tenant: str, scope: str, kind: str, text: str,
              topic: str, source: str, confidence: float,
              created: str = "2026-06-16", importance: float = 0.5,
              ttl_days: int | None = None) -> MemoryItem | None:
        with span(
            f"memoria.write:{topic}", kind="CHAIN",
            inputs={"topic": topic, "source": source, "confidence": confidence, "text": text},
            attributes={"memory.scope": scope, "memory.kind": kind},
        ) as cur:
            # Política: não memorizar palpite do modelo nem baixa confiança.
            if source == "model_guess" or confidence < 0.5:
                self._log("write_rejected", topic=topic,
                          motivo="palpite do modelo ou confiança < 0.5", text=text)
                set_output(cur, {"decisao": "REJEITADO",
                                 "motivo": "palpite do modelo ou confiança < 0.5"})
                explain_card("MEMÓRIA — WRITE REJEITADO", {
                    "quem decidiu": "aplicação/política de escrita",
                    "motivo": "palpite do modelo ou confiança < 0.5",
                    "topico": topic,
                    "fonte": source,
                    "confianca": confidence,
                    "salvo onde": "não foi salvo em mem.items",
                })
                return None

            # Conflito: nova informação confirmada invalida a anterior do mesmo tópico.
            invalidadas: list[str] = []
            for it in self.items:
                if (it.user == user and it.tenant == tenant and it.topic == topic
                        and it.status == "active"):
                    it.status = "invalidated"
                    invalidadas.append(it.id)
                    self._log("invalidate", id=it.id, topic=topic,
                              motivo="substituída por informação mais recente")

            self._seq += 1
            item = MemoryItem(
                id=f"m{self._seq}", user=user, tenant=tenant, scope=scope, kind=kind,
                text=text, topic=topic, source=source, confidence=confidence,
                created=created, importance=importance, ttl_days=ttl_days,
                embedding=self.client.embed([text])[0],
            )
            self.items.append(item)
            self._log("write", id=item.id, topic=topic, scope=scope, source=source)
            set_output(cur, {"decisao": "GRAVADO", "id": item.id,
                             "invalidou": invalidadas or None})
            explain_card("MEMÓRIA — WRITE", {
                "quem gravou": "aplicação/política de memória",
                "id": item.id,
                "tipo": f"{scope}/{kind}",
                "topico": topic,
                "fonte": source,
                "confianca": confidence,
                "invalidou": invalidadas or "nada",
                "salvo onde": "mem.items em RAM; audit em mem.audit; Phoenix se ligado",
            })
            return item

    # ---- RETRIEVE (com política de recuperação) --------------------------- #
    def retrieve(self, *, query: str, user: str, tenant: str, k: int = 3,
                 threshold: float = 0.15, sim_min: float | None = None,
                 budget_tokens: int = 60, strategy: str = "selective"
                 ) -> list[MemoryItem]:
        # O corte de similaridade é ESPECÍFICO do modelo de embedding: nomic tem
        # baseline de cosseno alto (textos curtos ficam ~0.4-0.6 mesmo sem relação),
        # enquanto o MOCK por hashing fica perto de 0. Calibrar threshold sem olhar o
        # modelo de embedding é um erro clássico (ver README, seção Avaliação).
        if sim_min is None:
            sim_min = 0.62 if getattr(self.client, "mode", "mock") == "ollama" else 0.20

        with span(
            f"memoria.retrieve:{strategy}", kind="RETRIEVER",
            inputs={"query": query, "strategy": strategy},
            attributes={"memory.sim_min": sim_min, "memory.k": k},
        ) as cur:
            if strategy == "dump_all":
                # Caso (4): recupera TUDO do usuário/tenant - inclusive memórias
                # invalidadas e expiradas. É o "joga tudo no contexto". Costuma piorar:
                # contradições e ruído entram junto.
                tudo = [it for it in self.items
                        if it.user == user and it.tenant == tenant]
                self._log("retrieve_dump_all", n=len(tudo), user=user)
                set_output(cur, {"estrategia": "dump_all (tudo, sem filtro)",
                                 "recuperadas": [i.id for i in tudo],
                                 "inclui_invalidadas": True})
                explain_card("MEMÓRIA — RETRIEVE DUMP_ALL", {
                    "quem recuperou": "aplicação sem política seletiva",
                    "estratégia": "pegar tudo do usuário/tenant",
                    "recuperadas": [i.id for i in tudo],
                    "risco": "inclui ruído, expiradas e invalidada(s)",
                    "salvo onde": "nada novo; apenas leitura de mem.items",
                })
                return tudo

            q = self.client.embed([query])[0]
            # 1) Autorização + ciclo de vida: só do usuário/tenant, ativas e não expiradas.
            for it in self.items:
                if it.status == "active" and it.is_expired():
                    it.status = "expired"
                    self._log("expire", id=it.id, topic=it.topic)
            viaveis = [
                it for it in self.items
                if it.user == user and it.tenant == tenant
                and it.status == "active" and not it.is_expired()
            ]

            # 2) Score combinando similaridade + recência + importância.
            #    Gate por similaridade mínima: relevância não pode vir só de recência.
            scored: list[tuple[float, MemoryItem]] = []
            for it in viaveis:
                sim = cosine(q, it.embedding)
                if sim < sim_min:
                    continue
                # clamp defensivo: idade negativa (data futura) conta como 0, evitando
                # divisão por zero e recência > 1 para memórias mal-datadas.
                idade = max(0, _dias(it.created))
                rec = 1.0 / (1.0 + idade / 30.0)  # decai ~mensal
                score = 0.6 * sim + 0.2 * rec + 0.2 * it.importance
                scored.append((score, it))
            scored.sort(key=lambda s: s[0], reverse=True)

            # 3) Threshold + orçamento de tokens. Fallback: nada confiável -> vazio.
            out: list[MemoryItem] = []
            used = 0
            for score, it in scored:
                if score < threshold:
                    continue
                t = approx_tokens(it.text)
                if used + t > budget_tokens:
                    break
                out.append(it)
                used += t
                if len(out) >= k:
                    break
            self._log("retrieve", user=user, query=query, recuperadas=[i.id for i in out])
            set_output(cur, {"estrategia": "seletiva (similaridade+recência+importância)",
                             "recuperadas": [i.id for i in out],
                             "scores_top": [round(s, 3) for s, _ in scored[:5]]})
            explain_card("MEMÓRIA — RETRIEVE SELETIVO", {
                "quem recuperou": "aplicação/política de recuperação",
                "query": query,
                "candidatas": len(viaveis),
                "sim_min": sim_min,
                "budget": f"{budget_tokens} tokens aprox.",
                "recuperadas": [i.id for i in out] or "nenhuma confiável",
                "salvo onde": "nada novo; decisão aparece no terminal/Phoenix",
            })
            return out

    # ---- FORGET (direito ao esquecimento) --------------------------------- #
    def forget_user(self, user: str) -> int:
        with span(f"memoria.forget:{user}", kind="CHAIN", inputs={"user": user}) as cur:
            antes = len(self.items)
            self.items = [it for it in self.items if it.user != user]
            removidas = antes - len(self.items)
            self._log("forget_user", user=user, removidas=removidas)
            set_output(cur, {"removidas": removidas})
            explain_card("MEMÓRIA — FORGET", {
                "quem apagou": "aplicação/operação explícita",
                "usuário": user,
                "removidas": removidas,
                "salvo onde": "mem.items foi reescrito em RAM; mem.audit registra a operação",
            })
            return removidas

    def _log(self, op: str, **kw) -> None:
        self.audit.append({"op": op, **kw})


# --------------------------------------------------------------------------- #
# Cenário demonstrativo                                                        #
# --------------------------------------------------------------------------- #
SISTEMA = (
    "Você é um assistente da loja Mercânia. Use APENAS as MEMÓRIAS fornecidas para "
    "personalizar a resposta. Não invente preferências. Cite a memória usada."
)


def _responder(client, mem_items: list[MemoryItem], pergunta: str) -> str:
    if not mem_items:
        ctx = "(nenhuma memória recuperada)"
    else:
        ctx = "\n".join(f"[fonte: {m.id}/{m.topic}] {m.text}" for m in mem_items)
    prompt = f"MEMÓRIAS:\n{ctx}\n\nPERGUNTA: {pergunta}\nRESPOSTA:"
    return client.generate(SISTEMA, prompt)


@traced("poc3.memory_lifecycle")
def main() -> None:
    client = make_client()
    mem = Memory(client)
    print(f"== POC3 Memória ==  (modo do modelo: {client.mode})")
    print(banner())
    print("\nONDE ISTO É SALVO: as memórias vivem em memória do processo (RAM), em "
          "`mem.items` — esta POC NÃO persiste em disco. A trilha de auditoria fica em "
          "`mem.audit`. Cada operação (write/retrieve/forget) também vira um span no "
          "Phoenix quando o tracing está ligado.\n")

    U, T = "cliente-42", "mercania"

    # Escritas iniciais (memória persistente, fatos/preferências confirmados).
    mem.write(user=U, tenant=T, scope="persistent", kind="preference",
              text="Prefere receber notificações pelo canal de e-mail, não por SMS.",
              topic="canal_notificacao", source="user_confirmed", confidence=0.9,
              created="2026-01-10", importance=0.7)
    mem.write(user=U, tenant=T, scope="persistent", kind="fact",
              text="Endereço de entrega: Rua das Acácias, 100, São Paulo.",
              topic="endereco_entrega", source="user_confirmed", confidence=0.95,
              created="2026-02-01", importance=0.8)
    # Episódio antigo e pouco relevante (vai virar ruído no caso 4).
    mem.write(user=U, tenant=T, scope="persistent", kind="episode",
              text="Em 2026-03, perguntou sobre uma promoção de cafeteiras.",
              topic="episodio_promo", source="tool", confidence=0.8,
              created="2026-03-05", importance=0.2)
    # Tentativa de escrever um PALPITE do modelo -> deve ser REJEITADA.
    rej = mem.write(user=U, tenant=T, scope="persistent", kind="fact",
                    text="Provavelmente o cliente tem um cachorro.",
                    topic="pet", source="model_guess", confidence=0.4)
    print(f"[política de escrita] palpite do modelo memorizado? {'sim' if rej else 'NÃO'}\n")

    # CASO 1 — memória útil recuperada.
    print("CASO 1 — pergunta relevante a uma preferência salva:")
    p1 = "Por qual canal devo enviar notificações ao cliente?"
    r1 = mem.retrieve(query=p1, user=U, tenant=T)
    print(f"  ENTRADA  (pergunta) : {p1!r}")
    print(f"  MEMÓRIA  (recuperadas): {[m.id for m in r1]}")
    print(f"  RESPOSTA            : {_responder(client, r1, p1)}\n")

    # CASO 2 — memória irrelevante ignorada (threshold).
    print("CASO 2 — pergunta sem relação com as memórias:")
    p2 = "qual a política de garantia da geladeira?"
    r2 = mem.retrieve(query=p2, user=U, tenant=T)
    print(f"  ENTRADA  (pergunta) : {p2!r}")
    print(f"  MEMÓRIA  (recuperadas): {[m.id for m in r2]}  (esperado: poucas/nenhuma)\n")

    # CASO 3 — conflito: cliente muda de endereço; o antigo é invalidado.
    print("CASO 3 — atualização conflitante (mudança de endereço):")
    p3 = "qual o endereço de entrega do cliente?"
    print(f"  ENTRADA  (escrita)  : novo endereço 'Avenida Central, 900, Campinas'")
    mem.write(user=U, tenant=T, scope="persistent", kind="fact",
              text="Endereço de entrega: Avenida Central, 900, Campinas.",
              topic="endereco_entrega", source="user_confirmed", confidence=0.95,
              created="2026-06-10", importance=0.8)
    r3 = mem.retrieve(query=p3, user=U, tenant=T)
    print(f"  ENTRADA  (pergunta) : {p3!r}")
    print(f"  MEMÓRIA  (recuperadas): {[m.id for m in r3]}  (o endereço antigo virou 'invalidated')")
    print(f"  RESPOSTA            : {_responder(client, r3, 'Qual o endereço de entrega?')}\n")

    # CASO 4 — recuperar tudo piora.
    print("CASO 4 — 'dump_all' vs seletivo para a mesma pergunta:")
    p4 = "Qual o endereço de entrega do cliente?"
    dump = mem.retrieve(query=p4, user=U, tenant=T, strategy="dump_all")
    seletivo = mem.retrieve(query=p4, user=U, tenant=T, strategy="selective")
    print(f"  dump_all recupera {len(dump)} memórias (inclui INVALIDADAS/ruído): "
          f"{[(m.id, m.status) for m in dump]}")
    print(f"  seletivo recupera {len(seletivo)}: {[(m.id, m.topic) for m in seletivo]}")
    print(f"  resposta (dump_all): {_responder(client, dump, p4)}")
    print(f"  resposta (seletivo): {_responder(client, seletivo, p4)}")
    print("  -> dump_all reintroduz o endereço ANTIGO (invalidado) e a resposta pode "
          "voltar a ficar errada; o seletivo entrega o endereço vigente.\n")

    # FORGET — direito ao esquecimento.
    n = mem.forget_user(U)
    print(f"FORGET — direito ao esquecimento: {n} memórias removidas do usuário {U}.")
    print()
    print("RESUMO — o que ficou salvo e onde:")
    print(f"  • memórias ativas em RAM (mem.items): {len(mem.items)} (após o forget)")
    print(f"  • trilha de auditoria (mem.audit): {len(mem.audit)} operações "
          f"({', '.join(sorted({e['op'] for e in mem.audit}))})")
    print("  • nada foi gravado em disco por esta POC (memória é do processo)")
    if enabled():
        print("  • cada operação acima também está no Phoenix (./.phoenix/) como um span")


if __name__ == "__main__":
    main()
