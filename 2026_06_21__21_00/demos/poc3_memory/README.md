# POC3 — Memória com operações explícitas

**Tese:** "memória" não é "um vector DB" nem "o histórico do chat". É um **sistema**
com operações nomeadas e governança:

```
write · retrieve · update · invalidate · expire · forget · audit
```

## O que esta POC evidencia (4 casos)

1. **Memória útil recuperada** — a preferência de canal (e-mail) é encontrada.
2. **Memória irrelevante ignorada** — pergunta sobre garantia não recupera nada
   (gate por similaridade mínima; relevância não pode vir só de recência).
3. **Conflito → invalidação** — o cliente muda de endereço; o antigo é marcado
   `invalidated` e **deixa de ser recuperado**; a versão vigente prevalece.
4. **Recuperar tudo piora** — `dump_all` reintroduz a memória **invalidada** e a
   resposta volta a ficar **errada**; o modo seletivo entrega o endereço vigente.

Além disso: **política de escrita** rejeita *palpite do modelo* (`model_guess`) e
baixa confiança; **forget** implementa direito ao esquecimento; tudo vai para uma
**trilha de auditoria**.

## Como rodar

```bash
USE_MOCK=1 python demos/poc3_memory/memory.py   # determinístico, sem modelo
python demos/poc3_memory/memory.py              # com Ollama
```

## Saída esperada (modo MOCK)

```
[política de escrita] palpite do modelo memorizado? NÃO
CASO 1  recuperadas: ['m1']  -> preferência de e-mail
CASO 2  recuperadas: []      -> irrelevante ignorada
CASO 3  recuperadas: ['m4']  -> endereço vigente (antigo invalidado)
CASO 4  dump_all -> endereço ANTIGO (errado); seletivo -> endereço vigente
FORGET  4 memórias removidas; auditoria registrada
```

## Modelo de dados (cada memória carrega)

`scope` (session/persistent) · `kind` (fact/preference/episode) · `topic` (chave de
conflito) · `source`/proveniência · `confidence` · `created` (timestamp) ·
`importance` · `ttl_days` (expiração) · `status` (active/invalidated/expired).

## Limitações

- Store em processo (não persiste em disco nesta POC, para ser autocontida). O
  caminho de produção seria SQL/document/vector + auditoria externa.
- A "consolidação" (resumir episódios em fatos) é citada no README principal, mas
  **não** implementada aqui — fica como exercício/encontro futuro.
