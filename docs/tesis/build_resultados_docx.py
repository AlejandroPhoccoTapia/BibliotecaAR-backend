"""Build a Word-ready thesis draft from the paired Markdown sources."""

from pathlib import Path
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).parent
OUTPUT = ROOT / "capitulo-iv-conclusiones-recomendaciones.docx"
SOURCES = [
    ROOT / "capitulo-iv-resultados.md",
    ROOT / "conclusiones-recomendaciones.md",
]


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def keep_row_together(row):
    tr_pr = row._tr.get_or_add_trPr()
    flag = OxmlElement("w:cantSplit")
    tr_pr.append(flag)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    flag = OxmlElement("w:tblHeader")
    flag.set(qn("w:val"), "true")
    tr_pr.append(flag)


def add_inline(paragraph, value):
    tokens = re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)", value)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(8.5)
        elif token.startswith("*") and token.endswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        else:
            paragraph.add_run(token)


def remove_paragraph_border(paragraph_or_style):
    element = paragraph_or_style._element
    p_pr = element.get_or_add_pPr()
    for border in p_pr.findall(qn("w:pBdr")):
        p_pr.remove(border)
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "nil")
    borders.append(bottom)
    p_pr.append(borders)


def table_rows(lines):
    parsed = []
    for line in lines:
        cells = [item.strip() for item in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]+", item or " ") for item in cells):
            continue
        parsed.append(cells)
    return parsed


def add_table(document, lines):
    rows = table_rows(lines)
    if not rows:
        return
    header = rows[0]
    if len(header) == 2:
        data = rows
    else:
        data = [[header[0], "Detalle"]]
        for row in rows[1:]:
            details = "\n".join(
                f"{label}: {content}" for label, content in zip(header[1:], row[1:])
            )
            data.append([row[0], details])

    table = document.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = (Cm(5.2), Cm(10.8)) if len(header) == 2 else (Cm(3.6), Cm(12.4))
    for index, row_data in enumerate(data):
        row = table.add_row()
        keep_row_together(row)
        if index == 0:
            repeat_header(row)
        for col, content in enumerate(row_data):
            cell = row.cells[col]
            cell.width = widths[col]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if index == 0:
                set_cell_shading(cell, "E8EDF0")
            elif index % 2 == 0:
                set_cell_shading(cell, "F7F9FA")
            paragraph = cell.paragraphs[0]
            paragraph.style = document.styles["Table Text"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for line_index, fragment in enumerate(content.split("\n")):
                if line_index:
                    paragraph.add_run("\n")
                add_inline(paragraph, fragment)
                if index == 0:
                    for run in paragraph.runs:
                        run.bold = True
    document.add_paragraph().paragraph_format.space_after = Pt(0)


def add_markdown(document, content, second=False):
    if second:
        document.add_page_break()
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            batch = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                batch.append(lines[i])
                i += 1
            add_table(document, batch)
            continue
        if line.startswith("# "):
            paragraph = document.add_paragraph(style="Title")
            remove_paragraph_border(paragraph)
            add_inline(paragraph, line[2:])
        elif line.startswith("## "):
            paragraph = document.add_paragraph(style="Heading 1")
            add_inline(paragraph, line[3:])
        elif line.startswith("### "):
            paragraph = document.add_paragraph(style="Heading 2")
            add_inline(paragraph, line[4:])
        elif line.startswith("> "):
            paragraph = document.add_paragraph(style="Note")
            add_inline(paragraph, line[2:])
        elif re.match(r"^\d+\.\s", line):
            paragraph = document.add_paragraph(style="Numbered Conclusion")
            add_inline(paragraph, line)
        elif line.startswith("*Tabla"):
            paragraph = document.add_paragraph(style="Caption")
            add_inline(paragraph, line)
        else:
            paragraph = document.add_paragraph(style="Normal")
            add_inline(paragraph, line)
        i += 1


def main():
    doc = Document()
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    title = styles["Title"]
    title.font.name = "Times New Roman"
    title.font.size = Pt(16)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title.paragraph_format.space_after = Pt(14)
    title.paragraph_format.keep_with_next = True
    remove_paragraph_border(title)

    for name, size, before, after in [("Heading 1", 13, 14, 7), ("Heading 2", 11, 10, 5)]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for name in ("Note", "Table Text", "Numbered Conclusion"):
        if name not in styles:
            styles.add_style(name, 1)
        style = styles[name]
        style.base_style = normal
    styles["Note"].font.size = Pt(9.5)
    styles["Note"].font.italic = True
    styles["Note"].paragraph_format.left_indent = Cm(0.4)
    styles["Table Text"].font.size = Pt(9)
    styles["Table Text"].paragraph_format.space_after = Pt(2)
    styles["Table Text"].paragraph_format.line_spacing = 1.05
    styles["Numbered Conclusion"].paragraph_format.left_indent = Cm(0.65)
    styles["Numbered Conclusion"].paragraph_format.first_line_indent = Cm(-0.65)
    styles["Numbered Conclusion"].paragraph_format.space_after = Pt(9)
    styles["Caption"].font.name = "Times New Roman"
    styles["Caption"].font.size = Pt(9)
    styles["Caption"].font.italic = True
    styles["Caption"].font.color.rgb = RGBColor(0, 0, 0)
    styles["Caption"].paragraph_format.space_after = Pt(9)

    for index, source in enumerate(SOURCES):
        add_markdown(doc, source.read_text(encoding="utf-8"), second=index > 0)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
