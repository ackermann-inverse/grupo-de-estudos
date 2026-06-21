# Obsidian + IA: análise crítica (e por que não viramos uma palestra sobre Obsidian)

O tema do encontro frequentemente atrai a pergunta: *"e o Obsidian, com aqueles
plugins de IA?"*. Esta nota responde de forma crítica e explica a decisão de design.

## O que o Obsidian realmente é (para o nosso propósito)

Obsidian é um editor de **Markdown** sobre um diretório local (o *vault*). Para RAG,
o que importa é exatamente isso: **um vault é um diretório de arquivos `.md`**. Tudo o
que fizemos no [corpus](../demos/corpus/) trata o vault como o que ele é — pasta de
Markdown com frontmatter — **sem depender do app**.

## Como Obsidian costuma ser usado com IA (panorama honesto)

- **Plugins de chat/IA** (ex.: famílias "Copilot for Obsidian", "Smart Connections")
  que indexam as notas e oferecem busca semântica/RAG sobre o vault, às vezes com
  modelos locais (via Ollama) e às vezes com APIs pagas.
- **Embeddings locais** apontando para o vault, gerando um índice vetorial.
- **Agentes** que leem/escrevem notas.

## Critérios de avaliação (antes de adotar qualquer plugin)

| Critério | Pergunta |
|---|---|
| Manutenção | O plugin é mantido? Quantos mantenedores? Cadência de releases? |
| Licença | É open source de verdade? Há tier pago que trava recursos essenciais? |
| Privacidade | As notas saem da máquina? Vão para qual API? Há opção 100% local? |
| Transparência | Dá para ver como ele faz chunking/indexa/recupera, ou é caixa-preta? |
| Reprodutibilidade | O índice é versionável? Outra pessoa reproduz o resultado? |
| Lock-in | Se o plugin morrer, você perde o quê? |

## Decisão deste encontro

**Não** tornamos o Obsidian uma dependência, e **não** usamos um plugin "porque é
popular". Motivos:

1. **Pedagógico:** um plugin esconderia justamente o que queremos ensinar (chunking,
   embeddings, retrieval, montagem de contexto). Ver o pipeline à mão vale mais.
2. **Reprodutibilidade:** um diretório de Markdown + Python roda igual em qualquer
   máquina; um plugin depende da versão do app, do SO e da loja de plugins.
3. **Transparência e privacidade:** sabemos exatamente o que sai da máquina (nada, no
   caminho local com Ollama).

> **Quando o Obsidian agrega:** como **interface** de captura e navegação de notas
> pessoais. Se você já vive no Obsidian, usar um plugin de busca semântica local
> (com Ollama) é uma **conveniência de UI** legítima. Mas isso é *experiência de
> usuário*, não *arquitetura de RAG* — e não muda nada do que este encontro ensina.

## Reaproveitando o nosso corpus como "vault"

O [corpus](../demos/corpus/) já é um vault válido: abra a pasta no Obsidian e você verá
as notas com frontmatter. As POCs leem esses mesmos arquivos via
[`demos/common/corpus.py`](../demos/common/corpus.py) — **sem** o app. Essa é a prova
de que "vault" e "diretório de Markdown" são a mesma coisa para fins de RAG.

**Conclusão:** Obsidian é ótimo como editor; tratá-lo como *o* mecanismo de memória/RAG
seria confundir interface com arquitetura. Por isso ele fica como nota crítica, não
como demo obrigatória.
