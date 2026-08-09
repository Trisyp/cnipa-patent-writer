#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Office Math (OMML) helpers for python-docx patent equations.

CRITICAL (2026-08 踩坑):
  - m:sub / m:sup 里**不要**再包一层 m:e。错误结构会让 LibreOffice/WPS 把上下角标渲成空方框 ❑。
  - 正确: m:sSub > m:e(基) + m:sub(直接挂 m:r / 子结构)
  - nary 没有上下限时**省略**空的 m:sub/m:sup，不要留 <m:e/>。
  - 集合基数/绝对值优先用 Unicode ∣ (U+2223)，少用 ASCII |（LO 易渲成 ¿）。
  - 复杂 ∑ 不稳时，改用 msub(mr("∑"), [...]) 平铺写法。

详见 references/omml-equations.md。装配后必须 soffice→pdf 并检查 ❑ 计数为 0。
"""

from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _m(tag: str):
    return OxmlElement(f"m:{tag}")


def mr(text: str, italic: bool = True):
    """Math run."""
    r = _m("r")
    rPr = _m("rPr")
    sty = _m("sty")
    sty.set(qn("m:val"), "i" if italic else "p")
    rPr.append(sty)
    r.append(rPr)
    t = _m("t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    return r


def msub(base, sub):
    """Subscript. sub children go DIRECTLY under m:sub — never wrap in m:e."""
    node = _m("sSub")
    e = _m("e")
    for c in _as_list(base):
        e.append(c)
    node.append(e)
    s = _m("sub")
    for c in _as_list(sub):
        s.append(c)
    node.append(s)
    return node


def msup(base, sup):
    """Superscript. same rule: no nested m:e under m:sup."""
    node = _m("sSup")
    e = _m("e")
    for c in _as_list(base):
        e.append(c)
    node.append(e)
    s = _m("sup")
    for c in _as_list(sup):
        s.append(c)
    node.append(s)
    return node


def mfrac(num, den):
    f = _m("f")
    n = _m("num")
    for c in _as_list(num):
        n.append(c)
    d = _m("den")
    for c in _as_list(den):
        d.append(c)
    f.append(n)
    f.append(d)
    return f


def mdelim(content, beg="(", end=")"):
    d = _m("d")
    dPr = _m("dPr")
    b = _m("begChr")
    b.set(qn("m:val"), beg)
    dPr.append(b)
    e = _m("endChr")
    e.set(qn("m:val"), end)
    dPr.append(e)
    d.append(dPr)
    ee = _m("e")
    for c in _as_list(content):
        ee.append(c)
    d.append(ee)
    return d


def mnary(body, sub=None, sup=None, chr_="∑"):
    """N-ary. Omit empty limit nodes entirely when sub/sup is None/empty."""
    nary = _m("nary")
    naryPr = _m("naryPr")
    ch = _m("chr")
    ch.set(qn("m:val"), chr_)
    naryPr.append(ch)
    lim = _m("limLoc")
    lim.set(qn("m:val"), "undOvr")
    naryPr.append(lim)
    nary.append(naryPr)
    if sub:
        s = _m("sub")
        for c in _as_list(sub):
            s.append(c)
        nary.append(s)
    if sup:
        u = _m("sup")
        for c in _as_list(sup):
            u.append(c)
        nary.append(u)
    e = _m("e")
    for c in _as_list(body):
        e.append(c)
    nary.append(e)
    return nary


def momath(*children):
    om = _m("oMath")
    for c in children:
        om.append(c)
    return om


def _as_list(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]


def clear_para_keep_pPr(p):
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)


def add_text_run(p, text: str):
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    for tag, val in (("w:sz", "24"), ("w:szCs", "24")):
        el = OxmlElement(tag)
        el.set(qn("w:val"), val)
        rPr.append(el)
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), "Times New Roman")
    fonts.set(qn("w:hAnsi"), "Times New Roman")
    fonts.set(qn("w:eastAsia"), "宋体")
    rPr.append(fonts)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    p.append(r)


def fill_mixed(p, parts):
    """parts: str | oMath element. Clears paragraph body, keeps pPr."""
    clear_para_keep_pPr(p)
    for part in parts:
        if isinstance(part, str):
            if part:
                add_text_run(p, part)
        else:
            p.append(part)
