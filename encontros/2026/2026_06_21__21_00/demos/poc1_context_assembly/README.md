# POC1 — Context Assembly (montagem de contexto)

**Tese:** *context engineering* não é "jogar tudo no prompt". É **seleção,
transformação, ordenação, isolamento, atualização e proveniência** sob um
**orçamento de tokens**.

## O que esta POC evidencia

A mesma pergunta — *"Qual é o prazo de reembolso?"* — é respondida com dois
contextos montados a partir das **mesmas fontes**:

- **Ingênuo:** concatena tudo na ordem de chegada, sem orçamento, com uma regra
  **obsoleta** (7 dias) antes da vigente (30 dias), e **sem proveniência**.
- **Com critérios:** resolve conflito (invalida o obsoleto por `status`/`data`),
  corta distratores de baixa relevância, respeita o orçamento, ordena em
  **bookend** (item forte no início e no fim, mitigando *lost in the middle*) e
  anexa rótulos `[fonte: ...]`.

## Como rodar

```bash
USE_MOCK=1 python demos/poc1_context_assembly/assemble.py   # sem modelo
python demos/poc1_context_assembly/assemble.py              # com Ollama
```

## Saída esperada (modo MOCK, determinística)

```
--- RESPOSTAS DO MODELO ---
  Ingênuo:        O prazo de reembolso é de 7 dias corridos.            (ERRADO: obsoleto)
  Com critérios:  O prazo de reembolso vigente é de 30 dias corridos... [politica-reembolso (v2)]
```

O relatório de decisões (`passo: conflito | relevancia | orcamento | ordenacao`)
mostra **por que** cada item entrou ou saiu — context engineering é auditável.

## Com modelo real

O efeito é o mesmo, porém mais sutil: um LLM real às vezes "concilia" as duas
regras ou escolhe a errada quando o contexto está poluído. O ponto não muda:
**ordem, recência e isolamento alteram a resposta** mesmo com o modelo perfeito.

## Limitações

- O MOCK é um QA extrativo lexical; ele torna o efeito **determinístico** para o
  teste, mas não é semântico.
- As "fontes" aqui são simuladas em código (não vêm do RAG) — de propósito, para
  isolar o conceito de *assembly* do conceito de *retrieval* (POC2).
