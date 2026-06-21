# Slides (Marp)

[`slides.md`](./slides.md) é um deck em **Markdown** no formato
[Marp](https://marp.app/) — versionável, sem depender de PowerPoint/Google Slides.

## Visualizar

- **VS Code:** instale a extensão *Marp for VS Code* e abra `slides.md` (preview).
- **CLI (sem instalar nada permanentemente):**

```bash
# servidor com hot-reload
npx @marp-team/marp-cli@latest -s slides/

# exportar para HTML
npx @marp-team/marp-cli@latest slides/slides.md -o slides/slides.html

# exportar para PDF (precisa de Chromium; em CI use --allow-local-files)
npx @marp-team/marp-cli@latest slides/slides.md --pdf
```

## Notas do apresentador

Os comentários `<!-- ... -->` no `slides.md` são **speaker notes** (aparecem no modo
apresentador do Marp e na exportação). O roteiro completo, com tempos e agendas de
60/90/120 min, está em [`../ROTEIRO.md`](../ROTEIRO.md).

## Por que Marp e não um PDF pronto

- **Diff-able:** mudanças aparecem no git como texto.
- **Sem lock-in:** exporta HTML/PDF/PPTX quando preciso.
- **Fonte única:** o deck espelha o `README.md`; não há duas verdades para manter.
