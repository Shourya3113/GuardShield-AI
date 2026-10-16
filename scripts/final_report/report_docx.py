"""
Word layout for the Amity NTCC report, following the ETMN100 guideline section 12:
A4; justified text; left/right margins 1.25 in, top/bottom 1.0 in; 1.5 line spacing; first line of every
paragraph indented 0.5 in; title page unnumbered; preliminary pages numbered ii, iii, ... centred at the
bottom; main text numbered 1, 2, ... at the top right; tables and figures numbered per chapter, listed in
the List of Tables / List of Figures; references with a 0.5 in hanging indent.
"""

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

FONT = "Times New Roman"
BLACK = RGBColor(0, 0, 0)


def _font(style, size, bold=False, italic=False):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = BLACK
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)


def _field(paragraph, code, placeholder=""):
    """Inserts a Word field (PAGE, TOC, ...) as begin / instruction / separate / result / end runs."""
    def fld(kind):
        r = paragraph.add_run()
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        if kind == "begin":
            el.set(qn("w:dirty"), "true")
        r._r.append(el)
    fld("begin")
    r = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {code} "
    r._r.append(instr)
    fld("separate")
    paragraph.add_run(placeholder)
    fld("end")


def _page_numbers(section, fmt, start):
    pg = section._sectPr.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        section._sectPr.append(pg)
    pg.set(qn("w:fmt"), fmt)
    pg.set(qn("w:start"), str(start))


class Report:
    def __init__(self):
        self.doc = Document()
        self.chapter = 0
        self.figures = 0
        self.tables = 0
        self.appendix = None
        s = self.doc.sections[0]
        s.page_width, s.page_height = Mm(210), Mm(297)
        s.left_margin = s.right_margin = Inches(1.25)
        s.top_margin = s.bottom_margin = Inches(1.0)
        st = self.doc.styles
        _font(st["Normal"], 12)
        pf = st["Normal"].paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.space_after = Pt(6)
        for name, size, align in (("Heading 1", 16, WD_ALIGN_PARAGRAPH.CENTER), ("Heading 2", 14, WD_ALIGN_PARAGRAPH.LEFT),
                                  ("Heading 3", 12, WD_ALIGN_PARAGRAPH.LEFT)):
            _font(st[name], size, bold=True)
            st[name].paragraph_format.alignment = align
            st[name].paragraph_format.first_line_indent = Inches(0)
            st[name].paragraph_format.space_before = Pt(12 if name != "Heading 1" else 0)
            st[name].paragraph_format.space_after = Pt(12 if name == "Heading 1" else 6)
            st[name].paragraph_format.keep_with_next = True
        for name in ("Figure Caption", "Table Caption"):
            cap = st.add_style(name, 1)
            cap.base_style = st["Normal"]
            _font(cap, 11, bold=name == "Table Caption")
            cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.first_line_indent = Inches(0)
            cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            cap.paragraph_format.space_after = Pt(10)
            cap.paragraph_format.keep_with_next = name == "Table Caption"
        _font(st["List Bullet"], 12)
        st["List Bullet"].paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        _font(st["List Number"], 12)
        self.cite_style = st.add_style("Reference", 1)
        self.cite_style.base_style = st["Normal"]
        self.cite_style.paragraph_format.left_indent = Inches(0.5)
        self.cite_style.paragraph_format.first_line_indent = Inches(-0.5)
        self.cite_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # ------------------------------------------------------------------ text
    def para(self, text, indent=True, align=None, bold=False, italic=False, size=None, space_after=None, style=None):
        p = self.doc.add_paragraph(style=style)
        if not indent:
            p.paragraph_format.first_line_indent = Inches(0)
        else:
            p.paragraph_format.first_line_indent = Inches(0.5)
        if align is not None:
            p.alignment = align
        if space_after is not None:
            p.paragraph_format.space_after = Pt(space_after)
        self._runs(p, text, bold=bold, italic=italic, size=size)
        return p

    def _runs(self, p, text, bold=False, italic=False, size=None):
        """**bold** and *italic* inline markup."""
        import re
        for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
            if not part:
                continue
            b, i, t = bold, italic, part
            if part.startswith("**") and part.endswith("**"):
                b, t = True, part[2:-2]
            elif part.startswith("*") and part.endswith("*"):
                i, t = True, part[1:-1]
            r = p.add_run(t)
            r.bold, r.italic = b, i
            if size:
                r.font.size = Pt(size)

    def bullets(self, items, numbered=False):
        for it in items:
            p = self.doc.add_paragraph(style="List Number" if numbered else "List Bullet")
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.left_indent = Inches(0.75)
            p.paragraph_format.space_after = Pt(3)
            self._runs(p, it)

    def heading(self, text, level):
        h = self.doc.add_heading(text, level=level)
        for r in h.runs:
            r.font.color.rgb = BLACK
            r.font.name = FONT
        return h

    def chapter_heading(self, title):
        self.chapter += 1
        self.figures = self.tables = 0
        if self.chapter > 1:  # chapter 1 opens the main-text section, which already starts a new page
            self.page_break()
        return self.heading(f"CHAPTER {self.chapter}\n{title.upper()}", 1)

    def appendix_heading(self, letter, title):
        self.appendix = letter
        self.figures = self.tables = 0
        self.page_break()
        return self.heading(f"APPENDIX {letter}. {title.upper()}", 1)

    def section(self, title):
        return self.heading(title, 2)

    def subsection(self, title):
        return self.heading(title, 3)

    def page_break(self):
        if len(self.doc.paragraphs) and not self.doc.paragraphs[-1].text and not self.doc.paragraphs[-1].runs:
            self.doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)
        else:
            self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ------------------------------------------------------------ figures/tables
    def _number(self, kind):
        prefix = self.appendix if self.appendix else str(self.chapter)
        if kind == "fig":
            self.figures += 1
            return f"{prefix}.{self.figures}"
        self.tables += 1
        return f"{prefix}.{self.tables}"

    def figure(self, path, caption, width=5.7):
        n = self._number("fig")
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(path), width=Inches(width))
        self.doc.add_paragraph(f"Figure {n}: {caption}", style="Figure Caption")
        return f"Figure {n}"

    def table(self, header, rows, caption, widths=None, size=10):
        n = self._number("tab")
        self.doc.add_paragraph(f"Table {n}: {caption}", style="Table Caption")
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate([header] + rows):
            for j, val in enumerate(row):
                cell = t.cell(i, j)
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                p.paragraph_format.space_after = Pt(0)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                self._runs(p, str(val), bold=i == 0, size=size)
                if i == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "D9E2F3")
                    cell._tc.get_or_add_tcPr().append(shd)
                if widths:
                    cell.width = Inches(widths[j])
        # header row repeats on page breaks
        trpr = t.rows[0]._tr.get_or_add_trPr()
        el = OxmlElement("w:tblHeader")
        el.set(qn("w:val"), "true")
        trpr.append(el)
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(4)
        return f"Table {n}"

    # ----------------------------------------------------------- fields/sections
    def toc(self, code="TOC \\o \"1-3\" \\h \\z \\u"):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        _field(p, code, "Right-click and choose Update Field to build this list.")

    def new_section(self, number_format, start, where):
        """number_format: lowerRoman | decimal; where: footer_center | header_right."""
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        _page_numbers(sec, number_format, start)
        for hf in (sec.header, sec.footer):
            hf.is_linked_to_previous = False
            for p in hf.paragraphs:
                p.text = ""
        target = sec.footer if where == "footer_center" else sec.header
        p = target.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if where == "footer_center" else WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.first_line_indent = Inches(0)
        _field(p, "PAGE", "1")
        return sec

    def save(self, path):
        self.doc.save(str(path))
