"""
Word version of Paper 1 (the mentor asked for a .docx), built from main.tex so the two never disagree.

    python paper1/paper/make_docx.py            # build the .docx; Word then adds footnotes and hyphenation and exports a check PDF

Covers the LaTeX that main.tex uses: the IEEEtran author block, sections, subsections, run-in \\paragraph headings,
lists, booktabs tables (\\multicolumn, \\cmidrule), figures, footnotes, inline math and natbib citations. Macros come
from generated/numbers*.tex, citations are numbered in order of first use and formatted like IEEEtranN, and
\\ref is resolved to IEEE numbering (Section III-A, Table II, Fig. 1). Layout follows the IEEE conference
template for US letter: 10 pt Times New Roman in two columns, wide floats in single-column blocks.
"""

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT_DIR = ROOT / "docs" / "01 Reports" / "Research Paper"
OUT = OUT_DIR / "Guards That Reject the Unfamiliar (IEEE).docx"
BUILD = HERE / "generated" / "docx_build"

FONT = "Times New Roman"
TEXT_WIDTH = 8.5 - 2 * 0.625          # inches, US letter with IEEE margins
COLUMN_WIDTH = (TEXT_WIDTH - 0.25) / 2
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
FN_MARK = "\u27e6FN{}\u27e7"            # placeholder that Word replaces with a real footnote


# ----------------------------------------------------------------------------- source and macros
def read_source():
    tex = (HERE / "main.tex").read_text(encoding="utf-8")
    macros = {}
    sources = [tex] + [p.read_text(encoding="utf-8") for p in sorted((HERE / "generated").glob("numbers*.tex"))]
    for src in sources:
        for m in re.finditer(r"\\newcommand\{\\([A-Za-z]+)\}\{", src):
            body, _ = braced(src, m.end() - 1)
            macros[m.group(1)] = body
    for name in ("todo", "fam", "linebreakand"):   # macros with arguments, handled by the parser
        macros.pop(name, None)
    macros["fam"] = None
    return tex, {k: v for k, v in macros.items() if v is not None}


def braced(s, i):
    """s[i] == '{'; returns (content, index after the closing brace)."""
    assert s[i] == "{", s[i:i + 30]
    depth, j = 0, i
    while True:
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1


def expand(s, macros):
    s = re.sub(r"\\fam\{([^}]*)\}", r"\\texttt{\1}", s)
    for _ in range(5):
        before = s
        for name in sorted(macros, key=len, reverse=True):
            s = re.sub(r"\\" + name + r"(?![A-Za-z])(\{\})?", lambda _m, v=macros[name]: v, s)
        if s == before:
            break
    return s


def strip_comments(s):
    out = []
    for line in s.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        if m:
            line = line[:m.start()]
            if not line.strip():
                continue
        out.append(line)
    return "\n".join(out)


# ----------------------------------------------------------------------------- bibliography
ACCENTS = {'"': "\u0308", "'": "\u0301", "`": "\u0300", "^": "\u0302", "~": "\u0303", "c": "\u0327", "k": "\u0328"}


def detex(s):
    import unicodedata
    s = re.sub(r"\{\\l\}|\\l(?![a-z])", "\u0142", s)
    s = re.sub(r"\\url\{([^}]*)\}", r"\1", s)
    def acc(m):
        return unicodedata.normalize("NFC", m.group(2) + ACCENTS[m.group(1)])
    s = re.sub(r"\{?\\([\"'`^~ck])\{?([A-Za-z])\}?\}?", acc, s)
    s = s.replace("\\_", "_").replace("\\%", "%").replace("\\&", "&").replace("--", "\u2013")
    s = s.replace("``", "\u201c").replace("''", "\u201d").replace("'", "\u2019")
    return s.replace("{", "").replace("}", "")


def read_bib():
    src = (HERE / "refs.bib").read_text(encoding="utf-8")
    entries = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),", src):
        i, fields = m.end(), {}
        while True:
            f = re.match(r"\s*(\w+)\s*=\s*", src[i:])
            if not f:
                break
            i += f.end()
            val, i = braced(src, i)
            fields[f.group(1).lower()] = val
            c = re.match(r"\s*,?", src[i:])
            i += c.end()
        fields["type"] = m.group(1).lower()
        entries[m.group(2).strip()] = fields
    return entries


def sentence_case(title):
    """IEEEtran's change.case$ "t": lower-case everything outside braces except the first letter and after a colon."""
    out, depth, first = [], 0, True
    i = 0
    while i < len(title):
        c = title[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0 and c.isalpha():
            out.append(c if first else c.lower())
            first = False
            i += 1
            continue
        elif c.isalpha():
            first = False
        elif depth == 0 and c == ":":
            out.append(c)
            j = i + 1
            while j < len(title) and title[j] == " ":
                out.append(" ")
                j += 1
            i, first = j, True
            continue
        if c not in "{}":
            out.append(c)
        i += 1
    return detex("".join(out))


def names(author_field):
    people = [a.strip() for a in re.split(r"\s+and\s+", author_field)]
    out, etal = [], False
    for p in people:
        if p == "others":
            etal = True
            continue
        if p.startswith("{") and p.endswith("}"):
            out.append((detex(p[1:-1]), detex(p[1:-1])))
            continue
        last, first = [x.strip() for x in p.split(",", 1)] if "," in p else (p.split()[-1], " ".join(p.split()[:-1]))
        last, first = detex(last).strip("{}"), detex(first).strip("{}")
        inits = []
        for part in first.split():
            inits.append("-".join(h[0] + "." for h in part.split("-") if h))
        out.append((last, " ".join(inits) + " " + last if inits else last))
    return out, etal


def author_list(field):
    ppl, etal = names(field)
    full = [f for _, f in ppl]
    if etal:
        return ", ".join(full) + " et al."
    if len(full) == 1:
        return full[0]
    if len(full) == 2:
        return f"{full[0]} and {full[1]}"
    return ", ".join(full[:-1]) + ", and " + full[-1]


def cite_name(entry):
    ppl, etal = names(entry["author"])
    if len(ppl) == 1 and not etal:
        return ppl[0][0]
    if len(ppl) == 2 and not etal:
        return f"{ppl[0][0]} and {ppl[1][0]}"
    return f"{ppl[0][0]} et al."


def format_reference(e):
    """List of (text, italic) segments in IEEEtranN style."""
    seg = [(author_list(e["author"]) + ", ", False), ("\u201c" + sentence_case(e["title"]) + ",\u201d ", False)]
    t, tail = e["type"], []
    pages = e.get("pages", "").replace("--", "\u2013")
    if t == "article":
        seg.append((detex(e["journal"]), True))
        if "volume" in e:
            tail.append(f"vol. {e['volume']}")
        if "number" in e:
            tail.append(f"no. {e['number']}")
        if pages:
            tail.append(("pp. " if "\u2013" in pages else "p. ") + pages)
        tail.append(e["year"])
    elif t == "inproceedings":
        seg.append(("in ", False))
        seg.append((detex(e["booktitle"]), True))
        if "address" in e:
            tail.append(detex(e["address"]) + (": " + detex(e["publisher"]) if "publisher" in e else ""))
        tail.append(e["year"])
        if pages:
            tail.append("pp. " + pages)
    else:
        if "howpublished" in e:
            tail.append(detex(e["howpublished"]))
        tail.append(e["year"])
    if "note" in e:
        tail.append(detex(e["note"]))
    seg.append(((", " if t in ("article", "inproceedings") else "") + ", ".join(tail) + ".", False))
    return seg


# ----------------------------------------------------------------------------- numbering pre-pass
def number_things(body):
    """IEEE numbers for \\label targets, and citation numbers in order of first use."""
    labels, cites = {}, {}
    sec = sub = tab = fig = 0
    appendix, current = False, None
    for m in re.finditer(r"\\(section|subsection|appendix|caption|label|cite[pt]?)\b(\*?)|\\begin\{(table\*?|figure\*?)\}", body):
        kind = m.group(1)
        if m.group(3):
            kind = "float"
            env = m.group(3)
            if env.startswith("table"):
                tab += 1
                current = ROMAN[tab]
            else:
                fig += 1
                current = str(fig)
        elif kind == "section":
            sec, sub = sec + 1, 0
            current = ("A" if appendix else ROMAN[sec])
        elif kind == "subsection":
            sub += 1
            current = f"{ROMAN[sec]}-{chr(64 + sub)}"
        elif kind == "appendix":
            appendix, sec = True, 0
        elif kind == "label":
            key, _ = braced(body, m.end())
            labels[key] = current
        elif kind.startswith("cite"):
            keys, _ = braced(body, m.end())
            for k in keys.split(","):
                cites.setdefault(k.strip(), len(cites) + 1)
        if kind == "float" or kind in ("section", "subsection"):
            pass
    return labels, cites


# ----------------------------------------------------------------------------- inline LaTeX -> runs
class Ctx:
    def __init__(self, labels, cites, bib):
        self.labels, self.cites, self.bib = labels, cites, bib
        self.footnotes = []


GREEK = {"tau": "\u03c4", "rho": "\u03c1", "geq": "\u2265", "leq": "\u2264", "times": "\u00d7", "to": "\u2192", "pm": "\u00b1",
         "dagger": "\u2020", "circ": "\u00b0", "ldots": "\u2026", "cdot": "\u00b7", "alpha": "\u03b1", "approx": "\u2248"}


def run(text, **fmt):
    return [text, fmt]


def merge(runs):
    out = []
    for t, f in runs:
        if t == "":
            continue
        if out and out[-1][1] == f:
            out[-1][0] += t
        else:
            out.append([t, dict(f)])
    return out


def read_arg(s, i):
    while i < len(s) and s[i] in " \n":
        i += 1
    if i < len(s) and s[i] == "[":
        j = s.index("]", i)
        i = j + 1
    while i < len(s) and s[i] in " \n":
        i += 1
    if i < len(s) and s[i] == "{":
        return braced(s, i)
    return s[i], i + 1  # single-token argument


def cite_numbers(keys, ctx):
    nums = sorted(ctx.cites[k.strip()] for k in keys.split(","))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(f"{nums[i]}\u2013{nums[j]}" if j - i >= 2 else ", ".join(str(n) for n in nums[i:j + 1]))
        i = j + 1
    return "[" + ", ".join(parts) + "]"


def inline(s, ctx, fmt=None):
    fmt = dict(fmt or {})
    runs, i, buf = [], 0, []

    def flush():
        if buf:
            runs.append(run("".join(buf), **fmt))
            buf.clear()

    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if not m:
                nxt = s[i + 1] if i + 1 < len(s) else ""
                i += 2
                if nxt == "\\":
                    buf.append("\n")
                elif nxt == ",":
                    buf.append("\u2009")
                elif nxt in " \n":
                    buf.append(" ")
                elif nxt == "-":
                    pass
                else:
                    buf.append(nxt)
                continue
            name, i = m.group(1), i + m.end()
            if name in ("emph", "textit", "textbf", "texttt", "textsc", "url", "mathrm", "text"):
                arg, i = read_arg(s, i)
                flush()
                f = dict(fmt)
                if name == "emph":
                    f["italic"] = not fmt.get("italic", False)
                elif name == "textit":
                    f["italic"] = True
                elif name == "textbf":
                    f["bold"] = True
                elif name == "texttt":
                    f["mono"] = True
                elif name == "url":
                    f["link"] = True        # a clickable hyperlink in the body font (Courier is too wide for a column)
                elif name == "textsc":
                    f["smallcaps"] = True
                runs += inline(arg, ctx, f)
            elif name in ("citep", "cite", "citet"):
                arg, i = read_arg(s, i)
                flush()
                if name == "citet":
                    key = arg.split(",")[0].strip()
                    runs.append(run(cite_name(ctx.bib[key]) + "\u00a0" + cite_numbers(arg, ctx), **fmt))
                else:
                    runs.append(run(cite_numbers(arg, ctx), **fmt))
            elif name == "ref":
                arg, i = read_arg(s, i)
                buf.append(ctx.labels[arg])
            elif name == "footnote":
                arg, i = read_arg(s, i)
                ctx.footnotes.append(arg)
                buf.append(FN_MARK.format(len(ctx.footnotes)))
            elif name == "todo":
                arg, i = read_arg(s, i)
                flush()
                runs += inline("[TODO: " + arg + "]", ctx, dict(fmt, red=True))
            elif name == "S":
                buf.append("\u00a7")
            elif name == "ldots":
                buf.append("\u2026")
            elif name == "quad":
                buf.append("\u2003")
            elif name in GREEK:
                buf.append(GREEK[name])
            elif name in ("small", "scriptsize", "centering", "footnotesize", "noindent"):
                pass
            else:
                print(f"warning: unhandled \\{name}", file=sys.stderr)
            if name in ("S", "ldots", "quad", "small", "scriptsize", "centering") or name in GREEK:
                while i < len(s) and s[i] in " \n":   # control words swallow the spaces after them
                    i += 1
            continue
        if c == "$":
            j = s.index("$", i + 1)
            flush()
            runs += math(s[i + 1:j], ctx, fmt)
            i = j + 1
            continue
        if c == "{":
            content, i = braced(s, i)
            flush()
            runs += inline(content, ctx, fmt)
            continue
        if c == "}":
            i += 1
            continue
        if c == "~":
            buf.append("\u00a0")
        elif s.startswith("``", i):
            buf.append("\u201c")
            i += 1
        elif s.startswith("''", i):
            buf.append("\u201d")
            i += 1
        elif c == "`":
            buf.append("\u2018")
        elif c == "'":
            buf.append("\u2019")
        elif s.startswith("---", i):
            buf.append("\u2014")
            i += 2
        elif s.startswith("--", i):
            buf.append("\u2013")
            i += 1
        elif c in " \n\t":
            if not (buf and buf[-1] in (" ", "\u00a0")):
                buf.append(" ")
        else:
            buf.append(c)
        i += 1
    flush()
    return merge(runs)


def math(s, ctx, fmt):
    """Inline math as Unicode text: italic letters, upright digits and names, spaced relations."""
    runs, i = [], 0
    upright = dict(fmt)
    italic = dict(fmt, italic=True)
    prev_operand = False
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            i += m.end()
            if name in ("mathrm", "text"):
                arg, i = read_arg(s, i)
                runs += inline(arg, ctx, upright)
                prev_operand = True
            elif name in ("geq", "leq", "to", "approx"):
                runs.append(run(" " + GREEK[name] + " ", **upright))
                prev_operand = False
            elif name in ("times", "pm"):
                runs.append(run("\u2009" + GREEK[name] + "\u2009" if name == "pm" else " " + GREEK[name] + " ", **upright))
                prev_operand = False
            elif name in ("tau", "rho", "alpha"):
                runs.append(run(GREEK[name], **italic))
                prev_operand = True
            elif name in GREEK:
                runs.append(run(GREEK[name], **upright))
            elif name == ",":
                runs.append(run("\u2009", **upright))
            elif name == "%":
                runs.append(run("%", **upright))
            else:
                print(f"warning: unhandled math \\{name}", file=sys.stderr)
            continue
        if c in "^_":
            i += 1
            if s[i] == "{":
                arg, i = braced(s, i)
            elif s[i] == "\\":
                m = re.match(r"\\([A-Za-z]+)", s[i:])
                arg, i = s[i:i + m.end()], i + m.end()
            else:
                arg, i = s[i], i + 1
            for t, f in math(arg, ctx, fmt):
                runs.append(run(t, **dict(f, **({"sup": True} if c == "^" else {"sub": True}))))
            continue
        if c == "{":
            arg, i = braced(s, i)
            runs += math(arg, ctx, fmt)
            prev_operand = True
            continue
        if c in "=<>":
            runs.append(run(f" {c} ", **upright))
            prev_operand = False
        elif c == "-":
            runs.append(run(" \u2212 " if prev_operand else "\u2212", **upright))
            prev_operand = False
        elif c.isalpha():
            runs.append(run(c, **italic))
            prev_operand = True
        elif c == " ":
            pass
        else:
            runs.append(run(c, **upright))
            prev_operand = c not in "(["
        i += 1
    return merge(runs)


# ----------------------------------------------------------------------------- document
class Paper:
    def __init__(self):
        self.doc = Document()
        st = self.doc.styles
        normal = st["Normal"]
        self._font(normal, 10)
        pf = normal.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.space_before = pf.space_after = Pt(0)
        pf.first_line_indent = Inches(0.14)
        pf.widow_control = True
        for name, size in (("Heading 1", 10), ("Heading 2", 10)):
            h = st[name]
            self._font(h, size)
            h.font.bold = False
            h.font.small_caps = name == "Heading 1"
            h.font.italic = name == "Heading 2"
            h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if name == "Heading 1" else WD_ALIGN_PARAGRAPH.LEFT
            h.paragraph_format.first_line_indent = Inches(0)
            h.paragraph_format.space_before = Pt(8 if name == "Heading 1" else 6)
            h.paragraph_format.space_after = Pt(4 if name == "Heading 1" else 3)
            h.paragraph_format.keep_with_next = True
            h.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        sec.left_margin = sec.right_margin = Inches(0.625)
        sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
        self.columns = 1

    @staticmethod
    def _font(style, size):
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        rpr = style.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = OxmlElement("w:rFonts")
            rpr.append(fonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fonts.set(qn(a), FONT)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if fonts.get(qn(a)) is not None:
                del fonts.attrib[qn(a)]

    # -- runs
    def add_runs(self, p, runs, size=None, bold=None, italic=None, smallcaps=None):
        for text, f in runs:
            parts = text.split("\n")
            for k, part in enumerate(parts):
                if k:
                    p.add_run().add_break(WD_BREAK.LINE)
                if not part:
                    continue
                r = p.add_run(part)
                it = f.get("italic", False) if italic is None else (italic != f.get("italic", False))
                r.italic = True if it else None
                r.bold = True if (bold or f.get("bold")) else None
                if f.get("mono"):
                    r.font.name = "Courier New"
                if f.get("smallcaps") or smallcaps:
                    r.font.small_caps = True
                if f.get("sup"):
                    r.font.superscript = True
                if f.get("sub"):
                    r.font.subscript = True
                if f.get("red"):
                    r.font.color.rgb = RGBColor(0xC0, 0, 0)
                if size:
                    r.font.size = Pt(size)
                if f.get("link"):
                    from docx.opc.constants import RELATIONSHIP_TYPE as RT
                    link = OxmlElement("w:hyperlink")
                    link.set(qn("r:id"), p.part.relate_to(part, RT.HYPERLINK, is_external=True))
                    r._r.addprevious(link)
                    link.append(r._r)
        return p

    def para(self, runs, indent=True, align=None, size=None, space_after=None, bold=None, italic=None, style=None):
        p = self.doc.add_paragraph(style=style)
        if not indent:
            p.paragraph_format.first_line_indent = Inches(0)
        if align is not None:
            p.alignment = align
        if space_after is not None:
            p.paragraph_format.space_after = Pt(space_after)
        return self.add_runs(p, runs, size=size, bold=bold, italic=italic)

    # -- sections and columns
    def set_columns(self, n):
        if n == self.columns:
            return
        sec = self.doc.add_section(WD_SECTION.CONTINUOUS)
        cols = sec._sectPr.find(qn("w:cols"))
        if cols is None:
            cols = OxmlElement("w:cols")
            sec._sectPr.append(cols)
        cols.set(qn("w:num"), str(n))
        cols.set(qn("w:space"), str(int(0.25 * 1440)))
        self.columns = n

    # -- floats
    def table(self, number, caption_runs, header_rows, body_rows, aligns, rules, size=8, wrap_cols=None):
        wrap_cols = wrap_cols or {}
        cap = self.para([[f"TABLE {number}", {}]], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, size=8)
        cap.paragraph_format.keep_with_next = True
        cap.paragraph_format.space_before = Pt(6)
        cap2 = self.para(caption_runs, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, size=8, space_after=4)
        for r in cap2.runs:
            r.font.small_caps = True
        cap2.paragraph_format.keep_with_next = True
        rows = header_rows + body_rows
        ncols = len(aligns)
        cells_text = [[] for _ in rows]
        t = self.doc.add_table(rows=len(rows), cols=ncols)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ri, row in enumerate(rows):
            ci = 0
            for content, span, align in row:
                cell = t.cell(ri, ci)
                if span > 1:
                    cell = cell.merge(t.cell(ri, ci + span - 1))
                p = cell.paragraphs[0]
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.keep_with_next = ri < len(rows) - 1
                p.alignment = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER,
                               "r": WD_ALIGN_PARAGRAPH.RIGHT}[align or aligns[ci]]
                self.add_runs(p, content, size=size)
                borders = {}
                if ri == 0:
                    borders["top"] = 8
                if ri == len(header_rows) - 1:
                    borders["bottom"] = 4
                if ri == len(rows) - 1:
                    borders["bottom"] = 8
                for (rr, c0, c1) in rules:
                    if rr == ri and c0 <= ci <= c1:
                        borders["bottom"] = 4
                if borders:
                    tcpr = cell._tc.get_or_add_tcPr()
                    tb = OxmlElement("w:tcBorders")
                    for side, sz in borders.items():
                        el = OxmlElement(f"w:{side}")
                        el.set(qn("w:val"), "single")
                        el.set(qn("w:sz"), str(sz))
                        el.set(qn("w:space"), "0")
                        el.set(qn("w:color"), "000000")
                        tb.append(el)
                    tcpr.append(tb)
                cells_text[ri].append(("".join(x for x, _ in content), ci, span))
                ci += span
        # header rows repeat if a table breaks across pages
        for ri in range(len(header_rows)):
            trpr = t.rows[ri]._tr.get_or_add_trPr()
            el = OxmlElement("w:tblHeader")
            el.set(qn("w:val"), "true")
            trpr.append(el)
        tblpr = t._tbl.tblPr
        mar = OxmlElement("w:tblCellMar")
        for side in ("left", "right"):
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:w"), "60")
            el.set(qn("w:type"), "dxa")
            mar.append(el)
        tblpr.append(mar)
        self._widths(t, cells_text, ncols, size, wrap_cols)
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(4)
        spacer.paragraph_format.first_line_indent = Inches(0)
        r = spacer.add_run()
        r.font.size = Pt(4)
        return t

    def _widths(self, t, cells_text, ncols, size, wrap_cols):
        """Column widths from the longest entry (Word's auto-fit mishandles merged header cells)."""
        char = size * 0.56 / 72                      # average Times character width in inches
        pad = 0.13
        avail = TEXT_WIDTH if self.columns == 1 else COLUMN_WIDTH
        w = [0.3] * ncols
        for row in cells_text:
            for text, ci, span in row:
                if span == 1:
                    need = len(text) * char + pad
                    if ci in wrap_cols:
                        need = min(need, wrap_cols[ci])
                    w[ci] = max(w[ci], need)
        for row in cells_text:
            for text, ci, span in row:
                if span > 1:
                    need, have = len(text) * char + pad, sum(w[ci:ci + span])
                    if need > have:
                        for k in range(ci, ci + span):
                            w[k] += (need - have) / span
        if sum(w) > avail:
            w = [x * avail / sum(w) for x in w]
        t.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(layout)
        for k, col in enumerate(t.columns):
            col.width = Inches(w[k])
        for ri, row in enumerate(cells_text):
            for text, ci, span in row:
                t.cell(ri, ci).width = Inches(sum(w[ci:ci + span]))

    def figure(self, number, image, width_in, caption_runs):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(6)
        p.add_run().add_picture(str(image), width=Inches(width_in))
        cap = self.para([[f"Fig. {number}. ", {}]] + caption_runs, indent=False, size=8, space_after=8)
        cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


# ----------------------------------------------------------------------------- tables
def split_top(s, sep):
    parts, depth, cur, i = [], 0, [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            if s.startswith(sep, i) and depth == 0:
                parts.append("".join(cur))
                cur, i = [], i + len(sep)
                continue
            cur.append(s[i:i + 2])
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0 and s.startswith(sep, i):
            parts.append("".join(cur))
            cur, i = [], i + len(sep)
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts


def colspec(spec):
    spec = re.sub(r"@\{[^}]*\}", "", spec)
    spec = re.sub(r"p\{[^}]*\}", "l", spec)
    return [c for c in spec if c in "lcr"]


def parse_tabular(body, ctx, macros):
    body = expand(body, macros)
    m = re.search(r"\\begin\{tabular\}", body)
    spec, i = braced(body, m.end())
    end = body.index("\\end{tabular}")
    inner = body[i:end]
    inner = re.sub(r"\\input\{([^}]*)\}", lambda mm: strip_comments((HERE / mm.group(1)).read_text(encoding="utf-8")), inner)
    inner = strip_comments(expand(inner, macros))
    aligns = colspec(spec)
    header, rows, rules, seen_mid = [], [], [], False
    for raw in split_top(inner, "\\\\"):
        raw = raw.strip()
        while True:
            mm = re.match(r"\s*\\(toprule|midrule|bottomrule|cmidrule(\([lr]+\))?\{(\d+)-(\d+)\})", raw)
            if not mm:
                break
            if mm.group(1) == "midrule":
                seen_mid = True
            elif mm.group(1).startswith("cmidrule"):
                target = len(header) - 1
                rules.append((target, int(mm.group(3)) - 1, int(mm.group(4)) - 1))
            raw = raw[mm.end():].strip()
        if not raw:
            continue
        cells = []
        for cell in split_top(raw, "&"):
            cell = cell.strip()
            mc = re.match(r"\\multicolumn\{(\d+)\}", cell)
            if mc:
                spec, j = braced(cell, mc.end())
                content, _ = braced(cell, j)
                al = colspec(spec)
                cells.append((inline(content, ctx), int(mc.group(1)), al[0] if al else "c"))
            else:
                cells.append((inline(cell, ctx), 1, None))
        (rows if seen_mid else header).append(cells)
    return header, rows, aligns, rules


# ----------------------------------------------------------------------------- body walker
def build():
    tex, macros = read_source()
    bib = read_bib()
    pre, body = tex.split("\\begin{document}", 1)
    body = body.split("\\end{document}", 1)[0]
    body = strip_comments(body)
    labels, cites = number_things(body)
    ctx = Ctx(labels, cites, bib)
    BUILD.mkdir(parents=True, exist_ok=True)
    paper = Paper()

    # title and authors (single column)
    title, _ = braced(pre, pre.index("\\title{") + 6)
    paper.para(inline(expand(title, macros), ctx), indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, size=24, space_after=12)
    author_src, _ = braced(pre, pre.index("\\author{") + 7)
    author_src = strip_comments(author_src)
    rows = [r for r in re.split(r"\\linebreakand", author_src)]
    blocks = [[b for b in re.split(r"\\and(?![A-Za-z])", r)] for r in rows]
    ncols = max(len(b) for b in blocks)
    at = paper.doc.add_table(rows=len(blocks), cols=ncols)
    at.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(blocks):
        if len(row) == 1 and ncols > 1:
            at.cell(ri, 0).merge(at.cell(ri, ncols - 1))
        start = 0 if len(row) == 1 else (ncols - len(row)) // 2
        for k, b in enumerate(row):
            name, _ = braced(b, b.index("\\IEEEauthorblockN{") + len("\\IEEEauthorblockN"))
            aff, _ = braced(b, b.index("\\IEEEauthorblockA{") + len("\\IEEEauthorblockA"))
            lines = [ln.strip() for ln in re.split(r"\\\\", aff) if ln.strip()]
            cell = at.cell(ri, start + k)
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Inches(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paper.add_runs(p, inline(name, ctx), size=11)
            for ln in lines:
                q = cell.add_paragraph()
                q.paragraph_format.first_line_indent = Inches(0)
                q.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paper.add_runs(q, inline(ln, ctx), size=10)
            cell.paragraphs[-1].paragraph_format.space_after = Pt(10)
    gap = paper.doc.add_paragraph()
    gap.paragraph_format.first_line_indent = Inches(0)
    paper.set_columns(2)

    tokens = re.compile(
        r"\\maketitle|\\begin\{abstract\}(.*?)\\end\{abstract\}|\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}"
        r"|\\section\*?\{|\\subsection\*?\{|\\paragraph\{|\\label\{[^}]*\}|\\appendix"
        r"|\\begin\{(enumerate|itemize)\}(.*?)\\end\{\3\}"
        r"|\\begin\{(table\*?|figure\*?)\}(?:\[[a-z]*\])?(.*?)\\end\{\5\}"
        r"|\\bibliographystyle\{[^}]*\}|\\bibliography\{[^}]*\}|\n\s*\n", re.S)

    sec_no, sub_no, para_no = 0, 0, 0
    appendix = False
    pending = []          # text of the paragraph being collected
    run_in = None          # run-in heading for the next paragraph
    floats = {"table": 0, "figure": 0}

    def flush_para():
        nonlocal pending, run_in
        text = " ".join(pending).strip()
        pending = []
        if not text and not run_in:
            return
        runs = inline(expand(text, macros), ctx)
        if run_in:
            runs = [[run_in, {"italic": True}]] + runs
            run_in = None
        if runs:
            paper.para(runs)

    pos = 0
    for m in tokens.finditer(body):
        pending.append(body[pos:m.start()])
        tok = m.group(0)
        pos = m.end()
        if tok.startswith("\\maketitle") or tok.startswith("\\label") or tok.startswith("\\bibliographystyle"):
            continue
        if m.group(1) is not None:          # abstract
            p = paper.para([["Abstract", {"italic": True}], ["\u2014", {}]] + inline(expand(m.group(1).strip(), macros), ctx),
                           size=9, bold=True)
            p.paragraph_format.first_line_indent = Inches(0.14)
            continue
        if m.group(2) is not None:          # index terms
            p = paper.para([["Index Terms", {"italic": True}], ["\u2014", {}]] + inline(m.group(2).strip(), ctx), size=9, bold=True,
                           space_after=6)
            continue
        if tok.strip() == "":
            flush_para()
            continue
        flush_para()
        if tok.startswith("\\section"):
            arg, pos = braced(body, m.end() - 1)
            sec_no, sub_no, para_no = sec_no + 1, 0, 0
            if appendix:
                text = "Appendix"
            else:
                text = f"{ROMAN[sec_no]}. {arg}"
            h = paper.doc.add_heading(level=1)
            paper.add_runs(h, inline(text, ctx))
        elif tok.startswith("\\subsection"):
            arg, pos = braced(body, m.end() - 1)
            sub_no, para_no = sub_no + 1, 0
            h = paper.doc.add_heading(level=2)
            paper.add_runs(h, inline(f"{chr(64 + sub_no)}. {arg}", ctx))
        elif tok.startswith("\\paragraph"):
            arg, pos = braced(body, m.end() - 1)
            para_no += 1
            heading = "".join(t for t, _ in inline(expand(arg, macros), ctx))
            run_in = f"{chr(96 + para_no)}) {heading}: "
        elif tok == "\\appendix":
            appendix = True
            sec_no = 0
            paper.set_columns(1)
        elif m.group(3):                    # lists
            items = [it.strip() for it in re.split(r"\\item\s", m.group(4)) if it.strip()]
            for k, it in enumerate(items, 1):
                label = f"{k})" if m.group(3) == "enumerate" else "\u2022"
                p = paper.para([[label + "\t", {}]] + inline(expand(it, macros), ctx))
                pf = p.paragraph_format
                pf.left_indent, pf.first_line_indent = Inches(0.3), Inches(-0.2)
                pf.tab_stops.add_tab_stop(Inches(0.3))
        elif m.group(5):                    # floats
            env, content = m.group(5), m.group(6)
            wide = env.endswith("*")
            cap_i = content.index("\\caption")
            caption, _ = braced(content, cap_i + len("\\caption"))
            caption_runs = inline(expand(caption, macros), ctx)
            if wide and not appendix:
                paper.set_columns(1)
            if env.startswith("table"):
                floats["table"] += 1
                header, rows, aligns, rules = parse_tabular(content, ctx, macros)
                size = 7 if "\\scriptsize" in content else 8
                spec, _ = braced(content, content.index("\\begin{tabular}") + len("\\begin{tabular}"))
                cols = re.findall(r"p\{([\d.]+)cm\}|[lcr]", re.sub(r"@\{[^}]*\}", "", spec))
                wrap = {k: float(cm) / 2.54 for k, cm in enumerate(cols) if cm}
                paper.table(ROMAN[floats["table"]], caption_runs, header, rows, aligns, rules, size=size, wrap_cols=wrap)
            else:
                floats["figure"] += 1
                g = re.search(r"\\includegraphics\[width=([\d.]+)\\textwidth\]\{([^}]*)\}", content)
                img = render_figure(HERE / g.group(2))
                paper.figure(floats["figure"], img, float(g.group(1)) * TEXT_WIDTH, caption_runs)
            if wide and not appendix:
                paper.set_columns(2)
        elif tok.startswith("\\bibliography{"):
            h = paper.doc.add_heading(level=1)
            paper.add_runs(h, [["References", {}]])
            for key, n in sorted(cites.items(), key=lambda kv: kv[1]):
                p = paper.doc.add_paragraph()
                pf = p.paragraph_format
                pf.left_indent, pf.first_line_indent = Inches(0.3), Inches(-0.3)
                pf.tab_stops.add_tab_stop(Inches(0.3))
                pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
                pf.space_after = Pt(1)
                segs = [[f"[{n}]\t", {}]] + [[t, {"italic": True} if it else {}] for t, it in format_reference(bib[key])]
                paper.add_runs(p, segs, size=8)
    pending.append(body[pos:])
    flush_para()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    props = paper.doc.core_properties
    props.title = "".join(t for t, _ in inline(expand(title, macros), ctx)).replace("\n", " ")
    props.author = "Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh, Abhishek Kaushal"
    paper.doc.save(str(OUT))
    print(f"wrote {OUT} ({len(cites)} references, {floats['table']} tables, {floats['figure']} figures)")
    return ctx.footnotes


def render_figure(pdf_path):
    """Figures are vector PDFs; Word needs a bitmap, so render them at 300 dpi."""
    import pymupdf
    out = BUILD / (pdf_path.stem + ".png")
    if not out.exists() or out.stat().st_mtime < pdf_path.stat().st_mtime:
        pymupdf.open(str(pdf_path))[0].get_pixmap(dpi=300).save(str(out))
    return out


# ----------------------------------------------------------------------------- Word finishing
def finish_with_word(footnotes):
    """Word fits the tables to their contents, inserts the footnotes and exports a PDF for checking."""
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(OUT))
        for idx in range(1, doc.Tables.Count + 1):
            t = doc.Tables(idx)
            if idx == 1:
                t.AutoFitBehavior(2)    # the author block spans the page; data tables keep their computed widths
            t.Rows.Alignment = 1
        doc.AutoHyphenation = True      # as LaTeX does, so justified columns have no wide gaps
        for k, note in enumerate(footnotes, 1):
            rng = doc.Content
            f = rng.Find
            if f.Execute(FN_MARK.format(k)):
                rng.Text = ""
                fn = doc.Footnotes.Add(rng)
                fn.Range.Text = "".join(t for t, _ in inline(note, Ctx({}, {}, {})))
                fn.Range.Font.Size = 8
                fn.Range.Font.Name = FONT
        doc.Save()
        pdf = BUILD / (OUT.stem + ".pdf")      # for checking the layout; not a deliverable
        doc.ExportAsFixedFormat(str(pdf), 17)
        pages = doc.ComputeStatistics(2)
        doc.Close(False)
        print(f"Word: tables fitted, {len(footnotes)} footnote(s), {pages} pages; wrote {pdf.name}")
    finally:
        word.Quit()


if __name__ == "__main__":
    notes = build()
    if "--no-word" not in sys.argv:
        finish_with_word(notes)
