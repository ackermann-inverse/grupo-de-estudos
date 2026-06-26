# Slides (Marp)

[`slides.md`](./slides.md) é um deck em **Markdown** no formato
[Marp](https://marp.app/) — versionável, sem depender de PowerPoint/Google Slides.

## Visualizar

- **VS Code:** instale a extensão *Marp for VS Code* e abra `slides.md` (preview).
- **CLI (sem instalar nada permanentemente):**

```bash
# gerar preview HTML em .generated/
make slides-html

# gerar PDF em .generated/ (precisa de Chromium)
make slides-pdf
```

O tema visual fica em [`../../../assets/marp/grupo-estudos.css`](../../../assets/marp/grupo-estudos.css).
O PDF é artefato gerado e não deve ser commitado.

## Notas do apresentador

Os comentários `<!-- ... -->` no `slides.md` são **speaker notes** (aparecem no modo
apresentador do Marp e na exportação). O roteiro completo, com tempos e agendas de
60/90/120 min, está em [`../ROTEIRO.md`](../ROTEIRO.md).

## Por que Marp e não um PDF pronto

- **Diff-able:** mudanças aparecem no git como texto.
- **Sem lock-in:** exporta HTML/PDF/PPTX quando preciso.
- **Fonte única:** o deck espelha o `README.md`; não há duas verdades para manter.
