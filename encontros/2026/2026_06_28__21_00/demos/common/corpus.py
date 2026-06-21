"""Carrega o "vault" de Markdown como corpus de retrieval.

Decisão deliberada: tratamos um *vault* simplesmente como um diretório de arquivos
Markdown com frontmatter. Nenhuma dependência do app Obsidian, nenhum plugin. Ver
docs/obsidian-critico.md para a discussão.

Frontmatter: bloco YAML mínimo entre `---` no topo do arquivo. Parser próprio de
~20 linhas (apenas `chave: valor` e listas inline `[a, b]`), para não esconder o
conceito atrás de uma lib. Campos que usamos:
    fonte, versao, data, tenant, confidencialidade, status, tags
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .textutil import approx_tokens, chunk_text, tokenize


@dataclass
class Document:
    id: str
    path: str
    text: str
    meta: dict
    title: str = ""


@dataclass
class Chunk:
    id: str  # ex.: "politica-reembolso#2"
    doc_id: str
    ord: int
    text: str
    meta: dict
    tokens: list[str] = field(default_factory=list)
    n_tokens: int = 0


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Separa frontmatter (entre ---) do corpo. Parser mínimo e explícito."""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    header = raw[3:end].strip("\n")
    body = raw[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in header.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
            meta[key] = items
        else:
            meta[key] = value.strip("'\"")
    return meta, body


def load_corpus(corpus_dir: str, *, include_adversarial: bool = False) -> list[Document]:
    """Lê todos os .md do diretório (raiz). Os documentos adversariais ficam em
    `adversarial/` e só entram quando explicitamente pedido (POC4)."""
    docs: list[Document] = []
    for name in sorted(os.listdir(corpus_dir)):
        full = os.path.join(corpus_dir, name)
        if not (name.endswith(".md") and os.path.isfile(full)):
            continue
        if name.lower() == "readme.md":  # documentação, não é conteúdo do corpus
            continue
        with open(full, encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = _parse_frontmatter(raw)
        doc_id = os.path.splitext(name)[0]
        title = meta.get("titulo") or _first_heading(body) or doc_id
        docs.append(Document(id=doc_id, path=full, text=body, meta=meta, title=title))

    if include_adversarial:
        adv_dir = os.path.join(corpus_dir, "adversarial")
        if os.path.isdir(adv_dir):
            for name in sorted(os.listdir(adv_dir)):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(adv_dir, name)
                with open(full, encoding="utf-8") as fh:
                    raw = fh.read()
                meta, body = _parse_frontmatter(raw)
                meta.setdefault("origem", "adversarial")
                doc_id = os.path.splitext(name)[0]
                docs.append(
                    Document(
                        id=doc_id,
                        path=full,
                        text=body,
                        meta=meta,
                        title=meta.get("titulo") or doc_id,
                    )
                )
    return docs


def _first_heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def chunk_corpus(
    docs: list[Document], *, max_tokens: int = 120, overlap_tokens: int = 24
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        parts = chunk_text(doc.text, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
        for i, part in enumerate(parts):
            toks = tokenize(part)
            chunks.append(
                Chunk(
                    id=f"{doc.id}#{i}",
                    doc_id=doc.id,
                    ord=i,
                    text=part,
                    meta=dict(doc.meta),
                    tokens=toks,
                    n_tokens=approx_tokens(part),
                )
            )
    return chunks
