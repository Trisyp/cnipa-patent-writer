#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate generated patent docx text and Office Math boundaries.

Usage:
    python scripts/validate_patent_docx.py patent.docx [patent2.docx ...]

The script is intentionally lightweight: it reads word/document.xml directly and
checks for common patent-generation failures such as leftover LaTeX markers,
plain-text backslashes, Chinese text inside OMML formulas, internal draft terms,
and obvious Chinese/ASCII punctuation mixing.
"""

from __future__ import annotations

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

INTERNAL_TERMS = (
    "放弃",
    "本项目",
    "审查员",
    "抠船",
    "原合并",
    "方案B",
    "background.npz",
    "Let me",
    "TODO",
)


def _is_cjk(ch: str) -> bool:
    return "\u4e00" <= ch <= "\u9fff"


def _has_mixed_ascii_punct(text: str) -> bool:
    for idx, ch in enumerate(text[:-1]):
        nxt = text[idx + 1]
        if (_is_cjk(ch) and nxt in ",;:") or (ch in ",;:" and _is_cjk(nxt)):
            return True
    return "內" in text


def _extract_docx(path: Path) -> tuple[bytes, list[str], list[str]]:
    xml = zipfile.ZipFile(path).read("word/document.xml")
    tree = ET.fromstring(xml)
    paragraphs: list[str] = []
    formulas: list[str] = []

    for p in tree.iter(f"{{{W_NS}}}p"):
        p_text: list[str] = []
        for t in p.iter(f"{{{W_NS}}}t"):
            if t.text:
                p_text.append(t.text)
        if p_text:
            paragraphs.append("".join(p_text))

        for math in p.iter(f"{{{M_NS}}}oMath"):
            f_text: list[str] = []
            for elem in math.iter():
                if elem.tag.endswith("}t") and elem.text:
                    f_text.append(elem.text)
            formulas.append("".join(f_text))

    return xml, paragraphs, formulas


def validate(path: Path) -> int:
    xml, paragraphs, formulas = _extract_docx(path)
    formula_cjk = [
        (idx, f)
        for idx, f in enumerate(formulas, 1)
        if re.search(r"[\u4e00-\u9fff，。；：]", f)
    ]
    plain_backslash = [(idx, p) for idx, p in enumerate(paragraphs, 1) if "\\" in p]
    internal = [
        (idx, p)
        for idx, p in enumerate(paragraphs, 1)
        if any(term in p for term in INTERNAL_TERMS)
    ]
    mixed_punct = [
        (idx, p) for idx, p in enumerate(paragraphs, 1) if _has_mixed_ascii_punct(p)
    ]

    metrics = {
        "paragraphs": len(paragraphs),
        "formulas": len(formulas),
        "dollar_xml": xml.count(b"$"),
        "formula_cjk_or_cn_punct": len(formula_cjk),
        "plain_backslash": len(plain_backslash),
        "internal_terms": len(internal),
        "mixed_ascii_punct": len(mixed_punct),
    }

    print(f"\nDOC {path}")
    for key, value in metrics.items():
        print(f"{key}={value}")

    failures = []
    if metrics["dollar_xml"]:
        failures.append("leftover $ markers")
    if formula_cjk:
        failures.append("CJK text or Chinese punctuation inside formulas")
    if plain_backslash:
        failures.append("plain-text backslashes")
    if internal:
        failures.append("internal draft terms")
    if mixed_punct:
        failures.append("mixed ASCII punctuation near Chinese text")

    samples = {
        "formula_cjk_or_cn_punct": formula_cjk,
        "plain_backslash": plain_backslash,
        "internal_terms": internal,
        "mixed_ascii_punct": mixed_punct,
    }
    for name, hits in samples.items():
        if hits:
            print(f"-- {name} samples --")
            for idx, text in hits[:10]:
                print(f"{idx}: {text[:240]}")

    if failures:
        print("FAIL:", "; ".join(failures))
        return 1
    print("OK")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: validate_patent_docx.py patent.docx [patent2.docx ...]", file=sys.stderr)
        return 2

    status = 0
    for raw in argv:
        path = Path(raw)
        if not path.exists():
            print(f"Missing file: {path}", file=sys.stderr)
            status = 2
            continue
        status = max(status, validate(path))
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
