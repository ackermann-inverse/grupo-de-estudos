---
titulo: Política de reembolso (ANTIGA - descontinuada)
fonte: base-conhecimento-suporte
versao: v1
data: 2024-08-01
tenant: mercania
confidencialidade: interna
status: obsoleto
tags: [reembolso, financeiro]
---

# Política de reembolso (versão antiga)

> ATENÇÃO: esta é a versão v1, **descontinuada em março de 2026**. Foi substituída
> pela v2 (`politica-reembolso.md`). Está aqui de propósito para demonstrar o
> problema de obsolescência: o mesmo assunto, com regra diferente, ainda indexado.

Na política antiga, o reembolso de compras canceladas era feito em até **7 dias
corridos**. PIX em até 2 dias úteis; cartão em uma fatura.

Se um retriever ingênuo (sem filtro por `status`/`data`) trouxer este trecho, a
resposta ao cliente fica errada: dirá 7 dias quando o prazo vigente é 30 dias.
Recuperar por similaridade não é o mesmo que recuperar o que é verdadeiro agora.
