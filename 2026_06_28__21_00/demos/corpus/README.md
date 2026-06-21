# Corpus ("vault") do encontro

Conjunto **pequeno, original e versionado** de documentos Markdown sobre uma loja
fictícia, **Mercânia**. É o nosso "vault": um diretório de Markdown com frontmatter,
sem depender do app Obsidian (mesmo corpus do encontro 1; nota crítica sobre Obsidian em
[`../../../2026_06_21__21_00/docs/obsidian-critico.md`](../../../2026_06_21__21_00/docs/obsidian-critico.md)).
Aqui ele ganha um **golden set** ([`../golden/golden.jsonl`](../golden/golden.jsonl)) para avaliação.

## Por que este corpus é assim

Ele foi desenhado para **provocar erros reais de retrieval**, não para um happy path:

| Documento | Serve para demonstrar |
|---|---|
| `politica-reembolso.md` (v2, 30 dias) | Versão **vigente** do mesmo assunto |
| `adversarial/doc-obsoleto-v1.md` (v1, 7 dias) | **Obsolescência**: regra conflitante ainda indexada |
| `reembolso-atacado-norte.md` (tenant `atacado-norte`) | **Vazamento cross-tenant** se faltar filtro no storage |
| `prazo-entrega.md` (códigos `ENTREGA-EXP-48`, `SKU` etc.) | **Lexical vs semântico**: termo literal que o denso erra |
| `garantia.md` (`SKU-4471`) | Idem; correspondência exata importa |
| `politica-troca.md` | **Distrator**: parecido com reembolso, mas é outro assunto |
| `privacidade-lgpd.md` | **Direito ao esquecimento** que precisa se propagar à memória |
| `adversarial/doc-envenenado.md` | **Indirect prompt injection** via documento recuperado |

Os documentos em `adversarial/` **não** entram no índice por padrão; só quando a POC
pede explicitamente (`include_adversarial=True`).

## Licença e redistribuição

Conteúdo **100% original**, escrito para este encontro, sem dados pessoais reais.
Pode ser redistribuído junto com o repositório do grupo de estudos. Os nomes
("Mercânia", "Atacado Norte") são fictícios.

## Frontmatter

Cada arquivo começa com um bloco YAML mínimo:

```yaml
---
titulo: ...
fonte: ...
versao: v2
data: 2026-03-01
tenant: mercania
confidencialidade: interna   # publica | interna | restrita
status: vigente              # vigente | obsoleto | suspeito
tags: [reembolso, financeiro]
---
```

Esses metadados são o que torna possível **filtrar** (por tenant, status, data) em
vez de confiar só na similaridade. O parser está em
[`../common/corpus.py`](../common/corpus.py) — ~20 linhas, sem biblioteca externa.
