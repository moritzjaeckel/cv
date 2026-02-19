#!/usr/bin/env python3
"""Generate a professionally styled executive CV PDF from structured YAML data."""

from __future__ import annotations

from datetime import datetime
from math import atan2, cos, sin, pi
from pathlib import Path
from typing import Any, Dict, List
from xml.sax.saxutils import escape

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
    Flowable,
    ListFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "cv_data.yaml"
OUTPUT_DIR = ROOT / "output"
FONT_DIR = ROOT / "fonts"
ARCHIVE_DIR = OUTPUT_DIR / "archive"
LEFT_MARGIN = 1.9 * cm
RIGHT_MARGIN = 1.9 * cm
TOP_MARGIN = 1.6 * cm
BOTTOM_MARGIN = 1.6 * cm
PAGE_BACKGROUND = colors.HexColor("#FEFCF9")
CONTENT_WIDTH = A4[0] - LEFT_MARGIN - RIGHT_MARGIN
ACCENT_COLOR = colors.HexColor("#0F1C3F")


def output_path_for_today() -> Path:
    """Create dated output filename for uniqueness per run."""
    date_tag = datetime.now().strftime("%Y%m%d")
    base_name = f"executive_cv_{date_tag}.pdf"
    candidate = OUTPUT_DIR / base_name
    if not candidate.exists():
        return candidate
    suffix = 1
    while True:
        candidate = OUTPUT_DIR / f"executive_cv_{date_tag}_{suffix}.pdf"
        if not candidate.exists():
            return candidate
        suffix += 1


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
    styles.add(
        ParagraphStyle(
            name="DiagramInput",
            parent=styles["Body"],
            fontName=semi_font,
            fontSize=10,
            leading=12,
            textColor=ACCENT_COLOR,
            alignment=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DiagramLabel",
            parent=styles["Body"],
            fontName=semi_font,
            fontSize=10.5,
            leading=13,
            textColor=ACCENT_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DiagramBullet",
            parent=styles["Body"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1C1C1C"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="DiagramInputBullet",
            parent=styles["Body"],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#4A4A4A"),
            alignment=0,
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


class MergingArrowsFlowable(Flowable):
    """Draw a convergence diagram that joins prior experiences into focus areas."""

    def __init__(self, mapping: Dict[str, Any], styles: StyleSheet1):
        super().__init__()
        self.styles = styles
        self.inputs = self._normalize_inputs(mapping.get("inputs", []))
        self.outputs = mapping.get("outputs", [])
        self.width = CONTENT_WIDTH
        self.left_x = 0
        self.input_box_width = 152
        self.input_box_height = 32
        self.input_gap = 22
        self.input_bullet_gap = 6
        self.output_gap = 26
        self.output_left = self.input_box_width + 110
        self.output_box_width = self.width - self.output_left
        self.junction_x = self.output_left - 45
        self.output_padding_top = 8
        self.output_padding_bottom = 8
        self.bullet_spacing = 3
        self.input_padding = 8
        self.color = ACCENT_COLOR
        self.top_padding = 8
        self.bottom_padding = 8
        self.processed_inputs = self._prepare_inputs()
        self.processed_outputs = self._prepare_outputs()
        self.input_height_total = self._compute_input_height()
        self.output_height_total = self._compute_output_height()
        self.diagram_height = max(self.input_height_total, self.output_height_total)
        self.height = self.top_padding + self.diagram_height + self.bottom_padding

    def _normalize_inputs(self, entries: List[Any]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for entry in entries:
            if isinstance(entry, str):
                normalized.append({"label": entry, "key": entry, "bullets": []})
            else:
                key = entry.get("key") or entry.get("label", "")
                normalized.append(
                    {
                        "label": entry.get("label", ""),
                        "key": key,
                        "badge": entry.get("badge"),
                        "bullets": entry.get("bullets", []),
                    }
                )
        return normalized

    def _prepare_inputs(self) -> List[Dict[str, Any]]:
        processed: List[Dict[str, Any]] = []
        bullet_style = self.styles["DiagramInputBullet"]
        label_style = self.styles["DiagramInput"]
        content_width = self.input_box_width - 2 * self.input_padding
        for entry in self.inputs:
            placeholder_prefix = entry.get("badge") or "0"
            label_markup = f"{self._escape_text(str(placeholder_prefix))}. {self._escape_text(entry.get('label', ''))}"
            label_height = self._measure(label_markup, content_width, label_style)
            bullet_markups = [
                f"&bull;&nbsp;{self._escape_text(text)}" for text in entry.get("bullets", [])
            ]
            bullet_heights = [
                self._measure(markup, content_width, bullet_style) for markup in bullet_markups
            ]
            bullet_height_total = sum(bullet_heights)
            if bullet_heights:
                bullet_height_total += self.bullet_spacing * (len(bullet_heights) - 1)
            block_height = max(
                self.input_box_height,
                self.input_padding * 2
                + label_height
                + (self.input_bullet_gap + bullet_height_total if bullet_heights else 0),
            )
            processed.append(
                {
                    **entry,
                    "bullet_markups": bullet_markups,
                    "bullet_heights": bullet_heights,
                    "label_height": label_height,
                    "height": block_height,
                }
            )
        return processed

    def _prepare_outputs(self) -> List[Dict[str, Any]]:
        processed: List[Dict[str, Any]] = []
        label_style = self.styles["DiagramLabel"]
        bullet_style = self.styles["DiagramBullet"]
        label_width = self.output_box_width - 16
        bullet_width = self.output_box_width - 20
        for output in self.outputs:
            label_markup = self._label_markup(output)
            label_height = self._measure(label_markup, label_width, label_style)
            bullet_markups = [
                f"&bull;&nbsp;{self._escape_text(text)}" for text in output.get("bullets", [])
            ]
            bullet_heights = [
                self._measure(markup, bullet_width, bullet_style) for markup in bullet_markups
            ]
            bullet_height_total = sum(bullet_heights)
            if bullet_heights:
                bullet_height_total += self.bullet_spacing * (len(bullet_heights) - 1)
            total_height = (
                self.output_padding_top
                + label_height
                + (6 if bullet_heights else 0)
                + bullet_height_total
                + self.output_padding_bottom
            )
            total_height = max(total_height, 38)
            processed.append(
                {
                    "label_markup": label_markup,
                    "bullet_markups": bullet_markups,
                    "sources": output.get("sources", []),
                    "height": total_height,
                }
            )
        return processed

    def _compute_input_height(self) -> float:
        if not self.processed_inputs:
            return 0
        total = sum(item["height"] for item in self.processed_inputs)
        total += self.input_gap * (len(self.processed_inputs) - 1)
        return total

    def _compute_output_height(self) -> float:
        if not self.processed_outputs:
            return 0
        return sum(item["height"] for item in self.processed_outputs) + self.output_gap * (
            len(self.processed_outputs) - 1
        )

    def _label_markup(self, output: Dict[str, Any]) -> str:
        alias = output.get("alias")
        label = self._escape_text(output.get("label", ""))
        if alias:
            label = f"{label} {self._escape_text(alias)}"
        return label

    @staticmethod
    def _escape_text(text: str) -> str:
        return escape(text or "")

    def _measure(self, markup: str, width: float, style: ParagraphStyle) -> float:
        paragraph = Paragraph(markup, style)
        _, height = paragraph.wrap(width, 1000)
        return height

    def wrap(self, availWidth: float, availHeight: float) -> tuple[float, float]:
        return self.width, self.height

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()
        canvas.setStrokeColor(self.color)
        canvas.setLineWidth(1.1)
        input_nodes = self._build_input_nodes()
        output_nodes = self._build_output_nodes()
        self._draw_connections(canvas, input_nodes, output_nodes)
        self._draw_input_nodes(canvas, input_nodes)
        self._draw_output_nodes(canvas, output_nodes)
        canvas.restoreState()

    def _build_input_nodes(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        if not self.processed_inputs:
            return nodes
        start_top = self.height - self.top_padding - (self.diagram_height - self.input_height_total) / 2
        offset = 0.0
        for idx, entry in enumerate(self.processed_inputs):
            box_height = entry["height"]
            center_y = start_top - offset - box_height / 2
            nodes.append(
                {
                    "label": entry.get("label", ""),
                    "badge": entry.get("badge"),
                    "key": entry.get("key") or entry.get("label", ""),
                    "center": (self.left_x + self.input_box_width / 2, center_y),
                    "height": box_height,
                    "entry": entry,
                }
            )
            offset += entry["height"]
            if idx < len(self.processed_inputs) - 1:
                offset += self.input_gap
        return nodes

    def _build_output_nodes(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        if not self.processed_outputs:
            return nodes
        start_top = self.height - self.top_padding - (self.diagram_height - self.output_height_total) / 2
        offset = 0.0
        for idx, entry in enumerate(self.processed_outputs):
            center_y = start_top - offset - entry["height"] / 2
            nodes.append(
                {
                    "center": (self.output_left + self.output_box_width / 2, center_y),
                    "data": entry,
                }
            )
            offset += entry["height"]
            if idx < len(self.processed_outputs) - 1:
                offset += self.output_gap
        return nodes

    def _draw_input_nodes(self, canvas, nodes: List[Dict[str, Any]]) -> None:
        style = self.styles["DiagramInput"]
        bullet_style = self.styles["DiagramInputBullet"]
        for idx, node in enumerate(nodes):
            y_center = node["center"][1]
            box_height = node["height"]
            box_top = y_center + box_height / 2
            box_left = self.left_x
            canvas.roundRect(
                box_left,
                y_center - box_height / 2,
                self.input_box_width,
                box_height,
                6,
                stroke=1,
                fill=0,
            )
            prefix = node.get("badge") or str(idx + 1)
            label_markup = f"{self._escape_text(str(prefix))}. {self._escape_text(node.get('label', ''))}"
            paragraph = Paragraph(label_markup, style)
            available_width = self.input_box_width - 2 * self.input_padding
            _, label_height = paragraph.wrap(available_width, box_height)
            paragraph.drawOn(
                canvas,
                box_left + self.input_padding,
                box_top - self.input_padding - label_height,
            )
            entry = node["entry"]
            bullet_markups = entry.get("bullet_markups", [])
            bullet_heights = entry.get("bullet_heights", [])
            if bullet_markups:
                cursor_y = (
                    box_top
                    - self.input_padding
                    - label_height
                    - self.input_bullet_gap
                )
                bullet_width = available_width
                for markup, measured_height in zip(bullet_markups, bullet_heights):
                    bullet_para = Paragraph(markup, bullet_style)
                    _, para_height = bullet_para.wrap(bullet_width, measured_height)
                    bullet_para.drawOn(
                        canvas,
                        box_left + self.input_padding,
                        cursor_y - para_height,
                    )
                    cursor_y -= para_height
                    cursor_y -= self.bullet_spacing

    def _draw_output_nodes(self, canvas, nodes: List[Dict[str, Any]]) -> None:
        label_style = self.styles["DiagramLabel"]
        bullet_style = self.styles["DiagramBullet"]
        for node in nodes:
            entry = node["data"]
            y_center = node["center"][1]
            height = entry["height"]
            canvas.roundRect(
                self.output_left,
                y_center - height / 2,
                self.output_box_width,
                height,
                8,
                stroke=1,
                fill=0,
            )
            top_y = y_center + height / 2 - self.output_padding_top
            label_para = Paragraph(entry["label_markup"], label_style)
            _, label_height = label_para.wrap(self.output_box_width - 16, height)
            label_para.drawOn(canvas, self.output_left + 8, top_y - label_height)
            cursor_y = top_y - label_height - 6
            for markup in entry["bullet_markups"]:
                bullet_para = Paragraph(markup, bullet_style)
                _, bullet_height = bullet_para.wrap(self.output_box_width - 20, height)
                bullet_para.drawOn(canvas, self.output_left + 12, cursor_y - bullet_height)
                cursor_y -= bullet_height + self.bullet_spacing

    def _draw_connections(
        self, canvas, inputs: List[Dict[str, Any]], outputs: List[Dict[str, Any]]
    ) -> None:
        input_right = self.left_x + self.input_box_width
        input_map: Dict[str, tuple[float, float]] = {}
        for node in inputs:
            keys = [node.get("key"), node.get("label")]
            for key in keys:
                if not key:
                    continue
                input_map[key] = (input_right, node["center"][1])
        for node in outputs:
            entry = node["data"]
            dest = (self.junction_x, node["center"][1])
            for source_label in entry["sources"]:
                start = input_map.get(source_label)
                if not start:
                    continue
                self._draw_curve(canvas, start, dest)
            self._draw_arrow(canvas, dest, (self.output_left - 6, node["center"][1]))

    def _draw_curve(self, canvas, start: tuple[float, float], end: tuple[float, float]) -> None:
        ctrl_offset = max(18.0, (self.junction_x - (self.left_x + self.input_box_width)) * 0.6)
        canvas.bezier(
            start[0],
            start[1],
            start[0] + ctrl_offset,
            start[1],
            end[0] - ctrl_offset,
            end[1],
            end[0],
            end[1],
        )

    def _draw_arrow(
        self, canvas, start: tuple[float, float], end: tuple[float, float]
    ) -> None:
        canvas.line(start[0], start[1], end[0], end[1])
        angle = atan2(end[1] - start[1], end[0] - start[0])
        self._draw_arrowhead(canvas, end[0], end[1], angle)

    def _draw_arrowhead(self, canvas, tip_x: float, tip_y: float, angle: float) -> None:
        size = 6
        left_angle = angle + pi / 8
        right_angle = angle - pi / 8
        canvas.line(
            tip_x,
            tip_y,
            tip_x - size * cos(left_angle),
            tip_y - size * sin(left_angle),
        )
        canvas.line(
            tip_x,
            tip_y,
            tip_x - size * cos(right_angle),
            tip_y - size * sin(right_angle),
        )


def experience_fusion_section(data: Dict[str, Any], styles: StyleSheet1) -> List[Any]:
    mapping = data.get("experience_fusion")
    if not mapping:
        return []
    title = mapping.get("title", "Experience Fusion")
    section: List[Any] = [Paragraph(title, styles["SectionTitle"])]
    description = mapping.get("description")
    if description:
        section.append(Paragraph(description, styles["Body"]))
        section.append(Spacer(1, 6))
    section.append(MergingArrowsFlowable(mapping, styles))
    section.append(Spacer(1, 8))
    return section


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
    fusion_components = experience_fusion_section(data, styles)
    if fusion_components:
        story.extend(fusion_components)
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
    output_file = output_path_for_today()
    if output_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_path = ARCHIVE_DIR / f"{timestamp}_{output_file.name}"
        shutil.copy2(output_file, archive_path)
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )
    story = build_story(data, styles)
    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"CV written to {output_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
