# 📚💡 Grupo de Estudos

Materiais dos encontros de um **grupo de estudos** técnico — backend, infraestrutura,
redes, concorrência, mensageria, observabilidade e **IA aplicada** (Context Engineering,
RAG, memória, avaliação e observabilidade de RAG). Cada encontro reúne notas, slides e
**provas de conceito (PoCs)** rodáveis em várias linguagens (Go, Node.js, Python).

> ⚠️ **Repositório educacional.** Isto **não** é software de produção. São experimentos
> e PoCs feitos para **aprender e discutir** — muitas vezes simplificados de propósito.
> Leia o [`DISCLAIMER.md`](./DISCLAIMER.md) antes de reutilizar qualquer coisa.

## 🧭 Sumário

- [👥 Encontros](#-encontros)
- [🗂️ Como o repositório é organizado](#️-como-o-repositório-é-organizado)
- [▶️ Como usar](#️-como-usar)
- [📜 Licença](#-licença)
- [🤝 Contribuindo e contato](#-contribuindo-e-contato)

## 👥 Encontros

> Horários em GMT-3.

| Data | Tema | Apresentador(es) |
|:-:|:--|:--|
| 12/10/2025 15:00 | 1. [📬 Azure Service Bus (tópicos e mensageria avançada)](./encontros/2025/2025_10_12__15_00/README.md) | [Ruan Pato](https://ruanpato.com) |
| 10/12/2025 19:00 | 2. [🧵 Concorrência vs Paralelismo](./encontros/2025/2025_12_10__19_00/README.md) | [Ruan Pato](https://ruanpato.com) |
| 29/01/2026 20:00 | 3. 👀 OpenTelemetry *(planejado)* | [Marcos Adamczuk](https://github.com/mtczuk) |
| 24/05/2026 21:00 | 4. [🛠️ Harness Engineering para Agentes de IA](./encontros/2026/2026_05_24__21_00/README.md) | Maurício Antohaki, [Henrique Muniz](https://www.linkedin.com/in/henriquemichelon/) |
| 21/06/2026 21:00 | 5. [🧠 Context Engineering, RAG & Memória](./encontros/2026/2026_06_21__21_00/README.md) | [Ruan Pato](https://ruanpato.com) |
| 28/06/2026 21:00 | 6. [🔎 RAG Engineering (parte 2)](./encontros/2026/2026_06_28__21_00/README.md) | [Ruan Pato](https://ruanpato.com) |

## 🗂️ Como o repositório é organizado

```
grupo-de-estudos/
├── encontros/
│   ├── 2025/
│   │   ├── 2025_10_12__15_00/   # Azure Service Bus
│   │   └── 2025_12_10__19_00/   # Concorrência vs Paralelismo
│   └── 2026/
│       ├── 2026_01_29__20_00/   # OpenTelemetry (planejado)
│       ├── 2026_05_24__21_00/   # Harness Engineering (slides dos autores)
│       ├── 2026_06_21__21_00/   # Context Engineering, RAG & Memória
│       └── 2026_06_28__21_00/   # RAG Engineering (parte 2)
├── LICENSE        # conteúdo: CC BY 4.0
├── LICENSE-CODE   # código: MIT
├── NOTICE.md      # créditos / materiais de terceiros
├── DISCLAIMER.md  CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md
```

Cada encontro é **autocontido**: tem seu próprio `README.md` (material canônico) e,
quando há prática, `demos/`, `tests/`, `scripts/`/`Makefile` e `.gitignore` próprio.

## ▶️ Como usar

Os encontros mais recentes (5 e 6) rodam **localmente, em CPU**, com modelos abertos via
[Ollama](https://ollama.com) **ou** em um modo *mock* determinístico que dispensa
download. Em geral:

```bash
cd encontros/2026/2026_06_21__21_00
make setup     # cria ambiente e instala dependências
make test      # roda os testes (modo mock, sem baixar modelo)
make demo      # roda a demonstração principal
```

Cada `README.md` de encontro traz os pré-requisitos, comandos e limitações específicos.

## 📜 Licença

Licença **dupla**, pela natureza mista do conteúdo:

- **Código** (`.py`, `.go`, `.js`, `.sh`, Dockerfiles, etc.) → **MIT** — ver [`LICENSE-CODE`](./LICENSE-CODE).
- **Conteúdo próprio** (textos, documentação, slides, diagramas, corpora de exemplo) →
  **CC BY 4.0** — ver [`LICENSE`](./LICENSE).
- **Materiais de terceiros** (ex.: slides de apresentadores convidados) **não** estão
  cobertos por essas licenças — ver [`NOTICE.md`](./NOTICE.md).

## 🤝 Contribuindo e contato

Veja [`CONTRIBUTING.md`](./CONTRIBUTING.md) e o [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
Para reportar segredos vazados, dados pessoais ou questões de segurança, siga o
[`SECURITY.md`](./SECURITY.md) (não abra issue pública nesses casos).

Mantenedor: [Ruan Pato](https://ruanpato.com) · Organização: [ackermann-inverse](https://github.com/ackermann-inverse).
