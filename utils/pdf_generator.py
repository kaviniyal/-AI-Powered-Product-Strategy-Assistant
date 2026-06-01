import re
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#1a3c6e")
BLUE      = colors.HexColor("#2e86de")
TEAL      = colors.HexColor("#0a9396")
DARK_TEAL = colors.HexColor("#005f73")
LIGHT_BG  = colors.HexColor("#f0f6ff")
MID_BG    = colors.HexColor("#e1eaf8")
TEXT      = colors.HexColor("#1c2b3a")
SUBTEXT   = colors.HexColor("#4a5568")
WHITE     = colors.white
GRAY      = colors.HexColor("#94a3b8")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm


# ── Styles ────────────────────────────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=26, textColor=WHITE, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=8, leading=32,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=12, textColor=colors.HexColor("#c8daf5"),
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4,
        ),
        "section_title": ParagraphStyle(
            "section_title", fontSize=14, textColor=WHITE, fontName="Helvetica-Bold",
            alignment=TA_LEFT, leftPadding=10,
        ),
        "h2": ParagraphStyle(
            "h2", fontSize=12, textColor=NAVY, fontName="Helvetica-Bold",
            spaceBefore=10, spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "h3", fontSize=10, textColor=TEAL, fontName="Helvetica-Bold",
            spaceBefore=6, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body", fontSize=9.5, textColor=TEXT, fontName="Helvetica",
            leading=15, spaceAfter=4, alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=9.5, textColor=TEXT, fontName="Helvetica",
            leading=14, spaceAfter=3, leftIndent=16, firstLineIndent=0,
            bulletIndent=4,
        ),
        "numbered": ParagraphStyle(
            "numbered", fontSize=9.5, textColor=TEXT, fontName="Helvetica",
            leading=14, spaceAfter=3, leftIndent=20, firstLineIndent=-14,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label", fontSize=8, textColor=SUBTEXT, fontName="Helvetica",
            alignment=TA_CENTER,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value", fontSize=17, textColor=NAVY, fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
    }


# ── Inline markdown → ReportLab XML ──────────────────────────────────────────
def _inline(text: str) -> str:
    """Convert **bold** and *italic* markdown to ReportLab XML tags."""
    parts = re.split(r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)', text)
    out = []
    for p in parts:
        if p.startswith("***") and p.endswith("***"):
            inner = _esc(p[3:-3])
            out.append(f"<b><i>{inner}</i></b>")
        elif p.startswith("**") and p.endswith("**"):
            inner = _esc(p[2:-2])
            out.append(f"<b>{inner}</b>")
        elif p.startswith("*") and p.endswith("*") and len(p) > 2:
            inner = _esc(p[1:-1])
            out.append(f"<i>{inner}</i>")
        else:
            out.append(_esc(p))
    return "".join(out)


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Section header flowable ───────────────────────────────────────────────────
def _section_header(title: str, styles: dict):
    tbl = Table(
        [[Paragraph(title, styles["section_title"])]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS",[5]),
    ]))
    return tbl


# ── KPI table ─────────────────────────────────────────────────────────────────
def _kpi_table(kpis: dict, styles: dict):
    labels = ["Total Revenue", "Total Profit", "Units Sold", "Avg Rating", "New Customers"]
    values = [
        f"${kpis['total_revenue']:,.0f}",
        f"${kpis['total_profit']:,.0f}",
        f"{kpis['total_units']:,}",
        f"{kpis['avg_rating']} / 5",
        f"{kpis['total_new_customers']:,}",
    ]
    header_row = [Paragraph(l, styles["kpi_label"]) for l in labels]
    value_row  = [Paragraph(v, styles["kpi_value"]) for v in values]

    col_w = (PAGE_W - 2 * MARGIN) / 5
    tbl = Table([header_row, value_row], colWidths=[col_w] * 5, rowHeights=[22, 36])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), MID_BG),
        ("BACKGROUND",    (0, 1), (-1, 1), LIGHT_BG),
        ("GRID",          (0, 0), (-1, -1), 0.5, WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.5, BLUE),
        ("ROUNDEDCORNERS",[4]),
    ]))
    return tbl


# ── Markdown → flowables ──────────────────────────────────────────────────────
def _parse(text: str, styles: dict) -> list:
    elements = []
    num_counter = [0]

    for raw_line in text.split("\n"):
        line = raw_line.strip()

        # blank line
        if not line:
            elements.append(Spacer(1, 4))
            continue

        # horizontal rule
        if line in ("---", "***", "___"):
            elements.append(HRFlowable(width="100%", thickness=0.5, color=GRAY, spaceAfter=6))
            continue

        # h1  → styled as h2 (agent outputs rarely use real #)
        if line.startswith("# ") and not line.startswith("## "):
            elements.append(Paragraph(_inline(line[2:]), styles["h2"]))
            continue

        # h2
        if line.startswith("## "):
            elements.append(Paragraph(_inline(line[3:]), styles["h2"]))
            continue

        # h3
        if line.startswith("### "):
            elements.append(Paragraph(_inline(line[4:]), styles["h3"]))
            continue

        # bold-only line used as subheading  e.g.  **Top Performers:**
        if re.match(r'^\*\*[^*]+\*\*:?\s*$', line):
            clean = line.replace("**", "").rstrip(":")
            elements.append(Paragraph(clean, styles["h3"]))
            continue

        # numbered list  1. 2. etc.
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            num = m.group(1)
            content = _inline(m.group(2))
            elements.append(Paragraph(f"<b>{num}.</b>  {content}", styles["numbered"]))
            continue

        # bullet  - or * or •
        if re.match(r'^[-*•]\s+', line):
            content = _inline(re.sub(r'^[-*•]\s+', '', line))
            elements.append(Paragraph(f"• &nbsp; {content}", styles["bullet"]))
            continue

        # subheading: short line ending with colon, no markdown
        if line.endswith(":") and len(line) < 70 and "**" not in line:
            elements.append(Paragraph(_esc(line), styles["h3"]))
            continue

        # body
        elements.append(Paragraph(_inline(line), styles["body"]))

    return elements


# ── Page number callback ──────────────────────────────────────────────────────
def _page_num(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(PAGE_W / 2, 1.0 * cm, f"Page {doc.page}")
    canvas.drawString(MARGIN, 1.0 * cm, "AI-Powered Product Strategy Assistant")
    canvas.restoreState()


# ── Main entry ────────────────────────────────────────────────────────────────
def generate_pdf(results: dict, kpis: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.8 * cm,
    )
    styles = _styles()
    story  = []

    # ── Cover ────────────────────────────────────────────────────────────────
    cover_tbl = Table(
        [[Paragraph("AI-Powered Product Strategy Report", styles["cover_title"])],
         [Paragraph("Comprehensive Business Analysis & Strategic Recommendations", styles["cover_sub"])],
         [Paragraph(f"Period: {kpis['date_range']}", styles["cover_sub"])]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
        ("ROUNDEDCORNERS",[8]),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.6 * cm))

    # ── KPI Dashboard ────────────────────────────────────────────────────────
    story.append(_section_header("Key Performance Indicators", styles))
    story.append(Spacer(1, 0.25 * cm))
    story.append(_kpi_table(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # ── Agent sections ────────────────────────────────────────────────────────
    sections = [
        ("Executive Summary",               results.get("executive_summary", "")),
        ("Customer Insights Report",         results.get("customer_insights", "")),
        ("Sales Performance Analysis",       results.get("sales_insights", "")),
        ("Market Research Summary",          results.get("market_insights", "")),
        ("SWOT Analysis",                    results.get("swot", "")),
        ("Feature Prioritization & Roadmap", results.get("feature_priorities", "")),
    ]

    for title, content in sections:
        story.append(_section_header(title, styles))
        story.append(Spacer(1, 0.2 * cm))
        story.extend(_parse(content, styles))
        story.append(Spacer(1, 0.4 * cm))

    doc.build(story, onFirstPage=_page_num, onLaterPages=_page_num)
    buffer.seek(0)
    return buffer.read()
