# Contribuindo

Obrigado pelo interesse! Este é um repositório **educacional** de um grupo de estudos.
Contribuições bem-vindas: novos encontros, novas PoCs, correções, melhorias de
documentação e discussões.

## Como o repositório é organizado

Cada encontro vive em `encontros/<ano>/<AAAA_MM_DD__HH_MM>/`. Um encontro típico tem:

```
encontros/2026/2026_06_21__21_00/
├── README.md          # material canônico (o que é, agenda, teoria, referências)
├── ROTEIRO.md         # roteiro do apresentador (opcional)
├── slides/            # slides (Marp ou outro formato versionável) (opcional)
├── demos/             # PoCs rodáveis
├── tests/             # testes (idealmente rodam sem baixar modelo/serviço)
├── scripts/ + Makefile
├── .gitignore         # ajustado à stack daquele encontro
└── docs/              # decisões, limitações, matriz de compatibilidade
```

## Padrão mínimo para uma nova PoC

- [ ] Tem um **README** explicando o que demonstra e **como rodar** (comandos exatos).
- [ ] **Não contém segredos** (use `.env.example`, nunca `.env`).
- [ ] Roda de forma **reprodutível** — idealmente com um modo *mock*/offline para testes.
- [ ] Declara **pré-requisitos** e versões de runtime.
- [ ] Declara **limitações** e separa "experimento" de "recomendação".
- [ ] Tem um **`.gitignore`** adequado à linguagem (Python: `__pycache__/`, `.venv/`;
      Node: `node_modules/`; Go: `bin/`; etc.).

## Checklist antes de abrir um PR

- [ ] Rodei os testes/demo localmente.
- [ ] Não incluí segredos, dados pessoais reais nem material de terceiros sem permissão.
- [ ] Conteúdo de terceiros (se houver) está creditado e autorizado — ver [`NOTICE.md`](./NOTICE.md).
- [ ] Atualizei links e o índice no `README.md` raiz, se criei/movi pastas.
- [ ] Mensagem de commit no padrão *Conventional Commits* (ex.: `feat(meetup): ...`,
      `fix:`, `docs:`).

## Licença das contribuições

Ao contribuir, você concorda em licenciar **código** sob MIT ([`LICENSE-CODE`](./LICENSE-CODE))
e **conteúdo** sob CC BY 4.0 ([`LICENSE`](./LICENSE)). Não envie material de terceiros
sem autorização.

## Conduta

Participe respeitando o [Código de Conduta](./CODE_OF_CONDUCT.md).
