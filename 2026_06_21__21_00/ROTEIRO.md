# 🎤 Roteiro do apresentador — Context Engineering, RAG & Memória

Notas de condução para Ruan Pato. O material canônico é o [`README.md`](./README.md);
os slides estão em [`slides/slides.md`](./slides/slides.md). Aqui ficam **tempos**,
**falas-chave**, **checkpoints** e **planos de recuperação de falha**.

> **Narrativa (decisão editorial):** **Context Engineering → Memória → RAG.** RAG não é
> o centro: é um **caso específico** de "que informação entra no contexto, de onde vem,
> quanto dura, quem pode ver, como é validada". O aprofundamento de RAG é a
> **[parte 2](./parte-2-rag-engineering/)** (possível 2º encontro).

> **Regra de ouro:** alternar teoria e prática. Nenhuma demo fica só para o fim — cada
> bloco conceitual termina com uma POC.

---

## Versão principal: 60 minutos

É a versão alvo: cabe a **abertura** (contexto > prompt), os dois pilares
(**Context Engineering** e **Memória**) com suas POCs, **RAG como extensão** em forma
compacta, um bloco curto de **falhas/segurança** e o gancho para a parte 2.

| Tempo | Bloco | Conteúdo | Prática |
|---:|---|---|---|
| 00–05 | Abertura | "O problema não é prompt, é contexto." Taxonomia em 1 slide. RAG vem depois. | — |
| 05–20 | **Context Engineering** | tipos de contexto; falhas (obsoleto/conflitante/excesso/lost-in-the-middle); orçamento, ordenação, proveniência | **POC1** ao vivo |
| 20–38 | **Memória** | tipos; ciclo de vida (escrever→recuperar→invalidar→expirar→esquecer→auditar); "recuperar tudo piora" | **POC3** ao vivo |
| 38–50 | **RAG como extensão** | query→retrieval→contexto→resposta; **fontes/grounding**; **filtro por tenant**; "RAG também falha"; pausa de 3–5 min "como saber se funciona?" | **POC2** compacta |
| 50–56 | **Falhas & segurança** | indirect prompt injection; cross-tenant leak; dado recuperado ≠ instrução confiável; mitigação parcial | **POC4** (ou saída pré-capturada) |
| 56–60 | Fechamento | 5 conclusões; "se quiserem continuar, a **parte 2** é RAG Engineering" | Perguntas |

**Buffer:** se atrasar, POC4 vira "mostrar a saída já capturada" (READMEs das POCs) e
a pausa de avaliação encolhe para 2 min. Nunca corte a **abertura** (taxonomia) nem a
**Memória** — são o eixo do encontro nesta nova ordem.

---

## Alternativa: 90 minutos (preservada)

Mesma ordem, com mais fôlego em cada pilar e RAG um pouco menos compacto.

| Tempo | Bloco | Prática |
|---:|---|---|
| 00–10 | Abertura + taxonomia (seção 1) | Checkpoint 1 |
| 10–28 | Context Engineering (seção 2) | POC1 |
| 28–50 | Memória (seções 3 e 5: contexto×estado×memória) | POC3 |
| 50–68 | RAG como extensão (seção 4) + pausa "como saber se funciona?" | POC2 (dense/lexical/híbrido + cross-tenant) |
| 68–82 | Segurança (seção 6) + avaliação (seção 7, gancho) | POC4 |
| 82–90 | Discussão arquitetural + conclusões + gancho parte 2 | Perguntas |

---

## Alternativa: 120 minutos (estendida)

Versão de 90 + **a parte 2 ao vivo** (ou parte dela):

- **+15 min** RAG profundo: dense × lexical × híbrido lado a lado, RRF, reranking
  didático × cross-encoder, `--include-adversarial` (obsolescência). Use o material de
  [`parte-2-rag-engineering/`](./parte-2-rag-engineering/).
- **+10 min** RAG evaluation em camadas (recall@k, context precision/recall,
  faithfulness, golden set, regressão).
- **+5 min** observabilidade de RAG (query/chunks/scores/fontes/versão do índice/top-k/
  latência/custo) e OWASP LLM08.

Sugestão: 0–10 abertura; 10–28 context+POC1; 28–50 memória+POC3; 50–80 RAG +
retrieval deep dive + POC2; 80–100 RAG eval + observabilidade; 100–112 segurança+POC4;
112–120 fechamento.

---

## Preparação (antes de começar)

1. `make setup` com antecedência; **baixe os modelos antes** (`ollama pull
   nomic-embed-text && ollama pull llama3.2:3b`). Não baixe na frente da plateia.
2. Deixe o `ollama serve` rodando. Confirme com `ollama list`.
3. Rode `make test` (deve passar 22, ou 21 + 1 skip sem Ollama) e `make demo` "a frio".
4. Plano B: `USE_MOCK=1` em tudo. As saídas MOCK são determinísticas e batem com os READMEs.
5. Terminal com fonte grande; janela larga (as tabelas de scores precisam caber).

---

## Falas-chave por bloco (o que NÃO pode faltar)

**Abertura.** "Todo mundo quer o prompt perfeito. O problema raramente é o prompt —
é o **contexto**: certo, suficiente, atualizado, autorizado, verificável e bem
posicionado. RAG é importante, mas é **uma técnica de recuperar contexto** — vamos
chegar nele depois de entender contexto e memória."

**Context Engineering.** "Prompt engineering pergunta *como pedir*; context engineering
pergunta *o que entra, em que ordem, com qual orçamento e de onde veio*." Rodar POC1:
ingênuo dá **7 dias** (obsoleto), orçado dá **30 dias** (vigente, citado). "A diferença
não foi o modelo — foi a montagem."

**Memória.** "Memória não é guardar tudo. É seleção, persistência, recuperação,
**invalidação, expiração, esquecimento** e auditoria." Rodar POC3: memória útil
recuperada; irrelevante ignorada; endereço antigo **invalidado**; e o `dump_all`
trazendo de volta o endereço **errado**. "Recuperar tudo **piora**."

**RAG como extensão.** "Agora sim: como recuperar contexto **externo**, sob as mesmas
regras — proveniência, autorização, atualização." Rodar POC2 compacta com
`--show-scores`. Mostrar as **fontes** e o **filtro por tenant**; `make leak` para o
vazamento cross-tenant. Pausa: "**como saber se o RAG está funcionando?**" — as três
camadas (retriever / contexto / resposta fiel). "Métrica formal e o resto do retrieval
ficam na parte 2."

**Falhas & segurança.** Rodar POC4. "Injeção indireta via documento recuperado é
obedecida no pipeline ingênuo; demarcar reduz, mas o documento envenenado **continua
sendo recuperado**. Dado recuperado **não é instrução confiável**. Não existe defesa
completa — limite o blast radius." Ponte para o próximo tema do grupo (Guardrails).

**Fechamento.** As 5 conclusões. "Se o grupo quiser continuar, a **parte 2 é RAG
Engineering** — embeddings, retrieval, avaliação, observabilidade e segurança de RAG."

---

## Checkpoints (parar e perguntar)

1. (abertura) "Cite um exemplo de contexto, estado, conhecimento e memória no seu sistema."
2. (após POC1) "Onde, no seu prompt atual, há informação obsoleta ou sem proveniência?"
3. (após POC3) "Seu sistema tem invalidação e esquecimento, ou só append?"
4. (após POC2) "Seu filtro de tenant está no storage ou no prompt? Tem certeza?"
5. (após POC4) "Qual é o blast radius se um documento do seu índice for malicioso?"

---

## Planos de recuperação de falha (ao vivo)

| Falha | Sintoma | Recuperação |
|---|---|---|
| Ollama não responde | log "caindo para MOCK" | siga em MOCK; as saídas batem com os READMEs |
| Modelo não baixado | `model not found` | `export USE_MOCK=1` e continue; baixe no intervalo |
| Demo lenta | 1ª inferência carregando RAM | fale enquanto carrega; use `llama3.2:1b` |
| Resposta real "fora do script" | LLM real varia | use a favor: "viram? não-determinismo, exatamente o ponto" |
| POC1 real acerta o ingênuo | modelo robusto demais | rode POC1 em **MOCK** para o contraste nítido (7 vs 30 dias) |
| Tempo estourando | atraso acumulado | mostre saída pré-capturada da POC e siga |

> **Honestidade ao vivo:** se a POC4 com modelo real **não** obedecer à injeção no caso
> ingênuo (acontece com payloads fracos), diga: "neste modelo/execução não obedeceu — e
> é por isso que a defesa não pode depender do comportamento do modelo." A variação **é**
> a lição. O payload disfarçado de "atualização oficial" costuma flipar o `llama3.2:3b`.
