#!/usr/bin/env python3
"""Generate a professionally styled executive CV PDF from structured YAML data."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import shutil

import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "cv_data.yaml"
OUTPUT_DIR = ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "executive_cv.pdf"
FONT_DIR = ROOT / "fonts"
ARCHIVE_DIR = OUTPUT_DIR / "archive"
LEFT_MARGIN = 1.9 * cm
RIGHT_MARGIN = 1.9 * cm
TOP_MARGIN = 1.6 * cm
BOTTOM_MARGIN = 1.6 * cm
PAGE_BACKGROUND = colors.HexColor("#FEFCF9")


def register_fonts() -> None:
    """Register serif font family to ensure a bespoke typographic feel."""
    font_files = {
        "EBGaramond-Regular": FONT_DIR / "EBGaramond-Regular.ttf",
        "EBGaramond-Semibold": FONT_DIR / "EBGaramond-SemiBold.ttf",
        "EBGaramond-Bold": FONT_DIR / "EBGaramond-Bold.ttf",
    }
    for font_name, path in font_files.items():
        if not path.exists():
            raise FileNotFoundError(f"Font file missing: {path}")
        pdfmetrics.registerFont(TTFont(font_name, str(path)))


def load_data(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def soften_pipes(text: str) -> str:
    """Render pipe separators in a lighter tone for visual subtlety."""
    return text.replace("|", '<font color="#B3B3B3">|</font>')


def build_styles() -> StyleSheet1:
    styles = getSampleStyleSheet()
    base_font = "EBGaramond-Regular"
    semi_font = "EBGaramond-Semibold"
    bold_font = "EBGaramond-Bold"
    styles["Normal"].fontName = base_font
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 13
    styles.add(
        ParagraphStyle(
            name="HeaderName",
            fontName=bold_font,
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#0F1C3F"),
            spaceAfter=6,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeaderRole",
            fontName=semi_font,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0F1C3F"),
            spaceAfter=6,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeaderContact",
            fontName=base_font,
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#444444"),
            alignment=1,
            spaceBefore=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            fontName=semi_font,
            fontSize=11,
            leading=14,
            textTransform="uppercase",
            textColor=colors.HexColor("#0F1C3F"),
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=0,
            firstLineIndent=0,
            alignment=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName=base_font,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1C1C1C"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExperienceRole",
            parent=styles["Body"],
            fontName=semi_font,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0F1C3F"),
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExperienceMeta",
            parent=styles["Body"],
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Tagline",
            parent=styles["Body"],
            fontSize=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SignatureTitle",
            parent=styles["Body"],
            fontName=semi_font,
            fontSize=10.5,
            textColor=colors.HexColor("#0F1C3F"),
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SignatureDetail",
            parent=styles["Body"],
            fontName=base_font,
            fontSize=9,
            textColor=colors.HexColor("#2F2F2F"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="EducationPeriod",
            parent=styles["Body"],
            fontName=base_font,
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceAfter=6,
        )
    )
    return styles


def header_block(data: Dict[str, Any], styles: StyleSheet1) -> Table:
    header_data = [
        [Paragraph(data["name"], styles["HeaderName"])],
        [Paragraph(data["role"], styles["HeaderRole"])],
    ]
    if data.get("positioning"):
        header_data.append(
            [Paragraph(soften_pipes(data["positioning"]), styles["HeaderContact"])]
        )
    contact_parts = [
        value
        for value in [
            data.get("location"),
            data["contact"].get("email"),
            data["contact"].get("phone"),
            data["contact"].get("linkedin"),
            data["contact"].get("website"),
        ]
        if value
    ]
    if contact_parts:
        header_data.append(
            [Paragraph(soften_pipes(" | ".join(contact_parts)), styles["HeaderContact"])]
        )
    table = Table(header_data, colWidths=[17.6 * cm])
    style_cmds = [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    role_row_index = 1
    contact_row_index = len(header_data) - 1
    style_cmds.append(("BOTTOMPADDING", (0, role_row_index), (0, role_row_index), 8))
    style_cmds.append(("TOPPADDING", (0, contact_row_index), (0, contact_row_index), 0))
    table.setStyle(TableStyle(style_cmds))
    return table


def signature_highlights(data: Dict[str, Any], styles: StyleSheet1) -> Table:
    highlights = data.get("signature_highlights", [])
    if not highlights:
        return Table([[]])

    cells: List[List[Any]] = []
    row: List[Any] = []
    for item in highlights:
        cell = [
            Paragraph(item["title"], styles["SignatureTitle"]),
            Paragraph(item["detail"], styles["SignatureDetail"]),
        ]
        row.append(cell)
        if len(row) == 2:
            cells.append(row)
            row = []
    if row:
        row.append("")
        cells.append(row)

    table = Table(
        cells,
        colWidths=[8.6 * cm, 8.6 * cm],
        style=TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        ),
    )
    return table


def bullet_list(items: List[str], styles: StyleSheet1) -> ListFlowable:
    paragraphs = [Paragraph(text, styles["Body"]) for text in items]
    return ListFlowable(
        paragraphs,
        bulletType="bullet",
        bulletFontName="EBGaramond-Regular",
        bulletFontSize=8.5,
        bulletColor=colors.HexColor("#4A4A4A"),
        leftIndent=14,
        spaceBefore=2,
    )


def subtle_divider() -> List[Any]:
    return [
        Spacer(1, 12),
        HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#E8E2D6")),
        Spacer(1, 12),
    ]


def experience_section(data: Dict[str, Any], styles: StyleSheet1) -> List[Any]:
    content: List[Any] = []
    for item in data.get("experience", []):
        title = f"{item['role']} | {item['company']}"
        meta = f"{item['period']}  •  {item['location']}"
        content.append(Paragraph(title, styles["ExperienceRole"]))
        content.append(Paragraph(meta, styles["ExperienceMeta"]))
        bullets = item.get("bullets", [])
        if bullets:
            content.append(
                ListFlowable(
                    [Paragraph(text, styles["Body"]) for text in bullets],
                    bulletType="bullet",
                    bulletFontName="EBGaramond-Regular",
                    bulletFontSize=8.5,
                    bulletColor=colors.HexColor("#4A4A4A"),
                    leftIndent=14,
                    spaceBefore=2,
                )
            )
        content.append(Spacer(1, 6))
    return content


def education_section(data: Dict[str, Any], styles: StyleSheet1) -> List[Any]:
    entries = data.get("education", [])
    if not entries:
        return []

    rows = []
    for item in entries:
        rows.append(
            [
                Paragraph(item["school"], styles["ExperienceRole"]),
                Paragraph(item["degree"], styles["Body"]),
                Paragraph(item["period"], styles["EducationPeriod"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[5.5 * cm, 7.5 * cm, 3.0 * cm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        ),
    )
    return [table]


def skill_tags(data: Dict[str, Any], styles: StyleSheet1) -> List[Any]:
    groups = data.get("skills", [])
    if not groups:
        return []

    rows = []
    for group in groups:
        rows.append(
            [
                Paragraph(group["category"], styles["ExperienceRole"]),
                Paragraph(", ".join(group["items"]), styles["Body"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[5.2 * cm, 10.8 * cm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        ),
    )
    return [table]


def compact_info_section(
    title: str, values: List[str], styles: StyleSheet1
) -> List[Any]:
    if not values:
        return []
    return [
        Paragraph(title, styles["ExperienceRole"]),
        Paragraph(", ".join(values), styles["Body"]),
        Spacer(1, 4),
    ]


def build_story(data: Dict[str, Any], styles: StyleSheet1) -> List[Any]:
    story: List[Any] = []
    story.append(header_block(data, styles))
    story.append(Spacer(1, 12))
    story.extend(subtle_divider())

    story.append(Paragraph("Executive Summary", styles["SectionTitle"]))
    story.append(bullet_list(data.get("summary", []), styles))
    story.append(Spacer(1, 10))
    story.extend(subtle_divider())

    story.append(Paragraph("Signature Highlights", styles["SectionTitle"]))
    story.append(signature_highlights(data, styles))
    story.append(Spacer(1, 10))
    story.extend(subtle_divider())

    story.append(Paragraph("Experience", styles["SectionTitle"]))
    story.extend(experience_section(data, styles))

    story.extend(subtle_divider())
    story.append(Paragraph("Education", styles["SectionTitle"]))
    story.extend(education_section(data, styles))

    story.append(Paragraph("Skills", styles["SectionTitle"]))
    story.extend(skill_tags(data, styles))

    if data.get("languages") or data.get("interests"):
        story.append(Paragraph("Additional", styles["SectionTitle"]))
        story.extend(compact_info_section("Languages", data.get("languages", []), styles))
        story.extend(compact_info_section("Interests", data.get("interests", []), styles))

    return story


def draw_background(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAGE_BACKGROUND)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.restoreState()


def main() -> None:
    data = load_data(DATA_PATH)
    register_fonts()
    styles = build_styles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_path = ARCHIVE_DIR / f"{timestamp}_{OUTPUT_FILE.name}"
        shutil.copy2(OUTPUT_FILE, archive_path)
    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )
    story = build_story(data, styles)
    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"CV written to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
