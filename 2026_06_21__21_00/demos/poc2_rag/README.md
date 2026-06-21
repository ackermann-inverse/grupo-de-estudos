# POC2 — RAG local com pipeline visível

**Objetivo:** mostrar **cada etapa** do RAG, não só a resposta final. Você inspeciona
`query → candidatos (scores por método) → filtro por tenant → rerank → chunks
escolhidos → contexto final → resposta → fontes`.

## O que esta POC evidencia

- **Denso vs lexical vs híbrido (RRF):** três recuperações para a mesma query.
  O denso (cosseno de embeddings) brilha em paráfrase; o lexical (BM25) brilha em
  **termos literais** (ex.: `SKU-4471`, `ENTREGA-EXP-48`); o híbrido funde os dois.
- **Filtro obrigatório por `tenant` no storage:** `--no-tenant-filter` mostra o
  documento do cliente `atacado-norte` **vazando** para o contexto do varejo. O
  filtro é no retriever, **não** no prompt.
- **Obsolescência:** com `--include-adversarial`, a política v1 (7 dias) disputa
  com a v2 (30 dias) — similaridade não é o mesmo que verdade atual.

## Como rodar

```bash
# demo principal (também é o `make demo`)
python demos/poc2_rag/rag.py --query "qual é o prazo de reembolso?" --method hybrid

# vantagem do lexical em termo literal
python demos/poc2_rag/rag.py --query "garantia do SKU-4471" --method lexical

# vazamento cross-tenant (filtro desligado)
python demos/poc2_rag/rag.py --no-tenant-filter

# sem baixar modelo
USE_MOCK=1 python demos/poc2_rag/rag.py
```

Flags: `--method {dense,lexical,hybrid}`, `--k`, `--top`, `--tenant`,
`--no-tenant-filter`, `--include-adversarial`, `--show-scores`.

## Saída esperada (resumo)

- Query de reembolso (híbrido): top-1 = `politica-reembolso#0`, resposta com
  **30 dias** e citação da fonte.
- `--no-tenant-filter`: aparece `reembolso-atacado-norte#0` entre os candidatos.

## Com modelo real (Ollama)

Embeddings `nomic-embed-text` dão **similaridade semântica de verdade**: o contraste
denso × lexical fica mais nítido (o denso acerta paráfrases que o BM25 erra, e vice-
versa em códigos). No MOCK os dois colapsam em "sobreposição lexical".

## Limitações (honestas)

- O `rerank` aqui é um **stand-in** por sobreposição de termos — não é um
  cross-encoder de verdade (que lê query+doc juntos e é bem mais preciso, porém
  mais pesado; ex.: `bge-reranker`). Serve para mostrar a **etapa**, não para
  entregar a qualidade de produção.
- Index em memória, sem ANN/HNSW: corpus é pequeno de propósito. Em produção isso
  é um vector DB + search engine.
