import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def generate_pdf_report(
    owner_info: dict,
    score_data: dict,
    pnl: dict,
    narrative: str,
) -> io.BytesIO:
    """Generate a PDF Business Performance Report."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#1a56db"),
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1a56db"),
        spaceBefore=12, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6,
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey,
    )

    elements = []

    # Header
    elements.append(Paragraph("BizScore", title_style))
    elements.append(Paragraph("Business Performance Report", styles["Heading3"]))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#1a56db"), thickness=2))
    elements.append(Spacer(1, 12))

    # Business Info
    elements.append(Paragraph(f"<b>Business:</b> {owner_info.get('business_name', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Owner:</b> {owner_info.get('name', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Type:</b> {owner_info.get('business_type', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Location:</b> {owner_info.get('location', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}", body_style))
    elements.append(Spacer(1, 12))

    # Score Summary
    elements.append(Paragraph("Business Performance Score", h2_style))

    score = score_data.get("total_score", 0)
    tier = score_data.get("tier", "N/A")

    score_table_data = [
        ["Overall Score", f"{score} / 850"],
        ["Tier", tier],
    ]
    score_table = Table(score_table_data, colWidths=[2.5 * inch, 3 * inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4ff")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # Component Breakdown
    elements.append(Paragraph("Score Breakdown", h2_style))
    comp_data = [["Component", "Score", "Max", "Rating"]]
    for c in score_data.get("components", []):
        pct = c["score"] / c["max_score"] * 100 if c["max_score"] > 0 else 0
        rating = "Excellent" if pct >= 80 else "Good" if pct >= 60 else "Fair" if pct >= 40 else "Needs Work"
        comp_data.append([c["name"], str(c["score"]), str(c["max_score"]), rating])

    comp_table = Table(comp_data, colWidths=[2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a56db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(comp_table)
    elements.append(Spacer(1, 12))

    # Financial Summary
    elements.append(Paragraph("Financial Summary", h2_style))
    fin_data = [
        ["Revenue", f"RM {pnl.get('revenue', 0):,.2f}"],
        ["Cost of Goods", f"RM {pnl.get('cost_of_goods', 0):,.2f}"],
        ["Gross Profit", f"RM {pnl.get('gross_profit', 0):,.2f}"],
        ["Operating Expenses", f"RM {pnl.get('operating_expenses', 0):,.2f}"],
        ["Net Profit", f"RM {pnl.get('net_profit', 0):,.2f}"],
    ]
    fin_table = Table(fin_data, colWidths=[3 * inch, 3 * inch])
    fin_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0f4ff")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(fin_table)
    elements.append(Spacer(1, 12))

    # AI Narrative
    elements.append(Paragraph("Business Analysis", h2_style))
    # Convert markdown-like formatting to simple paragraphs
    for line in narrative.split("\n"):
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 4))
        elif line.startswith("**") and line.endswith("**"):
            elements.append(Paragraph(line.replace("**", "<b>").replace("**", "</b>"), h2_style))
        else:
            clean = line.replace("**", "<b>").rstrip("**") 
            if clean.count("<b>") > clean.count("</b>"):
                clean += "</b>"
            elements.append(Paragraph(clean, body_style))

    elements.append(Spacer(1, 20))

    # Footer
    elements.append(HRFlowable(width="100%", color=colors.lightgrey, thickness=1))
    elements.append(Paragraph(
        "This report was generated by BizScore — Business Performance Scoring for Financial Inclusion. "
        "Score is based on real transaction data recorded through the BizScore e-wallet.",
        small_style,
    ))

    doc.build(elements)
    buf.seek(0)
    return buf
