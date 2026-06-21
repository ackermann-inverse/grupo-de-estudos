# NOTICE — atribuições e materiais de terceiros

Este repositório é licenciado em **dois regimes** (ver [`LICENSE`](./LICENSE) e
[`LICENSE-CODE`](./LICENSE-CODE)):

- **Código** → MIT ([`LICENSE-CODE`](./LICENSE-CODE)).
- **Conteúdo próprio** (textos, documentação, slides, diagramas, corpora de exemplo) →
  CC BY 4.0 ([`LICENSE`](./LICENSE)).

O texto abaixo registra exceções e créditos.

## Materiais de terceiros

Alguns encontros do grupo foram apresentados por outras pessoas. **O material autoral
delas (slides, PDFs) NÃO é coberto pelas licenças acima** — os direitos permanecem com
os respectivos autores e qualquer uso depende de autorização deles.

- **Encontro "Harness Engineering para Agentes de IA"** (24/05/2026) — apresentado por
  **Maurício Antohaki** e **Henrique Muniz**. Os slides são de autoria dos
  apresentadores. **Não estão incluídos neste repositório**; serão disponibilizados
  pelos próprios autores, se e quando autorizarem. Crédito e agradecimento a eles.

## Pessoas creditadas

Os encontros listam apresentadores e participantes (presentes) com seus nomes e, quando
aplicável, links públicos de perfil. Esses nomes aparecem **com consentimento** das
pessoas. Se você é uma das pessoas citadas e deseja remover ou ajustar a sua menção,
abra uma issue ou entre em contato — atendemos prontamente.

## Dependências

As PoCs usam bibliotecas de código aberto (ex.: `requests`, `pytest`, e — opcional —
`sentence-transformers`/`torch`), além de modelos locais executados via
[Ollama](https://ollama.com) (ex.: `nomic-embed-text` sob Apache-2.0; `llama3.2` sob a
Llama Community License — *open weights*, com restrições). Cada dependência permanece
sob a sua própria licença. Antes de reutilizar um modelo "aberto", verifique a licença
dele — *open weights* não é o mesmo que *open source*.

## Dados de exemplo

Os corpora usados nas PoCs de RAG (loja fictícia "Mercânia", cliente "Atacado Norte")
são **fictícios e originais**, criados para fins didáticos. Não contêm dados pessoais
reais nem informação de clientes reais.
