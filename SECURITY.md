# Política de Segurança

Este é um repositório **educacional** de um grupo de estudos. Não é um produto com SLA,
mas levamos a sério problemas de segurança no conteúdo e no código.

## Reportar uma vulnerabilidade

Se você encontrar:

- um **segredo/credencial** commitado por engano (token, chave, `.env`, connection string);
- **dado pessoal** indevido;
- uma falha de segurança no código de alguma PoC;
- material de terceiros publicado sem autorização,

**não abra uma issue pública.** Em vez disso:

1. Use o **GitHub Security Advisory** (aba *Security* → *Report a vulnerability*), ou
2. Entre em contato em privado com o mantenedor: **Ruan Pato** — <https://ruanpato.com>.

Responderemos o mais rápido possível e creditaremos quem reportar, se desejar.

## Escopo

- **No escopo:** segredos vazados, dados pessoais, material de terceiros sem permissão,
  bugs de segurança no código das PoCs.
- **Fora do escopo:** o fato de PoCs serem propositalmente simplificadas ou
  "exploratórias" — isso é esperado e está documentado em [`DISCLAIMER.md`](./DISCLAIMER.md).

## PoCs de segurança

Algumas PoCs demonstram ataques (ex.: *prompt injection*) **para fins defensivos**, com
alvos fictícios e cargas inertes. Ver [`DISCLAIMER.md`](./DISCLAIMER.md).
