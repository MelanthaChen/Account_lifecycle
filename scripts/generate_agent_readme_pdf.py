from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
README_MD = ROOT / "packaging" / "Automation-Agent" / "README.md"
README_PDF = ROOT / "packaging" / "Automation-Agent" / "README.pdf"


def main() -> None:
    styles = get_styles()
    document = SimpleDocTemplate(
        str(README_PDF),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Automation Agent Setup Guide",
    )
    story = []
    in_code = False
    code_lines: list[str] = []

    for raw_line in README_MD.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["Code"]))
                story.append(Spacer(1, 0.08 * inch))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            story.append(Spacer(1, 0.07 * inch))
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
            story.append(Spacer(1, 0.12 * inch))
            continue
        if line.startswith("## "):
            if story:
                story.append(Spacer(1, 0.12 * inch))
            story.append(Paragraph(line[3:], styles["Heading2"]))
            continue
        if line.startswith("### "):
            story.append(Paragraph(line[4:], styles["Heading3"]))
            continue
        if line.startswith("- "):
            story.append(Paragraph(f"• {escape(line[2:])}", styles["Bullet"]))
            continue
        if line[:3].isdigit() and ". " in line[:5]:
            story.append(Paragraph(escape(line), styles["Body"]))
            continue
        story.append(Paragraph(escape(line), styles["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("Quick Reference", styles["Heading2"]))
    story.append(Paragraph("Double-click Install.command once. Then double-click Run.command whenever automation is needed.", styles["Body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Preformatted("Install.command -> installs dependencies\nRun.command -> starts the Automation Agent\nlogs/ -> stores local logs\nstorage/ -> stores browser sessions", styles["Code"]))

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {README_PDF}")


def get_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#111827"),
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=6,
            spaceAfter=6,
        ),
        "Heading3": ParagraphStyle(
            "Heading3",
            parent=sample["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceBefore=5,
            spaceAfter=4,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceAfter=3,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=12,
            textColor=colors.HexColor("#111827"),
            spaceAfter=2,
        ),
        "Code": ParagraphStyle(
            "Code",
            parent=sample["Code"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            leftIndent=10,
            rightIndent=10,
            backColor=colors.HexColor("#f3f4f6"),
            borderColor=colors.HexColor("#e5e7eb"),
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=6,
        ),
    }


def escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(document.leftMargin, 0.35 * inch, "Automation Agent Setup Guide")
    canvas.drawRightString(letter[0] - document.rightMargin, 0.35 * inch, f"Page {document.page}")
    canvas.restoreState()


if __name__ == "__main__":
    main()
