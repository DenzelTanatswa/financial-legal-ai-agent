"""Professional PDF report rendering from structured analysis data."""
from io import BytesIO
from datetime import datetime

def generate_pdf_report(document_info: dict, result: dict) -> bytes:
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("PDF reports require ReportLab. Install requirements-local.txt.") from exc
    buffer = BytesIO(); styles = getSampleStyleSheet()
    title = ParagraphStyle("AureonTitle", parent=styles["Title"], textColor=HexColor("#15264a"), fontSize=22)
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.65*inch)
    story = [Paragraph("AUREON INTELLIGENCE REPORT", title), Spacer(1, 12)]
    rows = [["Document", document_info.get("filename", "")], ["Type", document_info.get("document_type", "")], ["Classification", document_info.get("classification_label", "")], ["Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")]]
    table = Table(rows, colWidths=[1.5*inch, 5.6*inch]); table.setStyle(TableStyle([("BACKGROUND", (0,0), (0,-1), HexColor("#eaf1f8")), ("TEXTCOLOR", (0,0), (-1,-1), HexColor("#17233c")), ("GRID", (0,0), (-1,-1), .25, HexColor("#cdd8e6")), ("PADDING", (0,0), (-1,-1), 7)])); story += [table, Spacer(1, 16)]
    analysis = result.get("structured", {})
    for heading, value in [("Executive summary", result.get("summary", "")), ("Key findings", analysis.get("financial_highlights") or analysis.get("important_clauses") or []), ("Risks", analysis.get("risks", [])), ("Recommendations", analysis.get("recommendations", [])), ("Agent analysis", ", ".join(a.get("agent_name", "") for a in result.get("agent_responses", [])))]:
        story.append(Paragraph(heading, styles["Heading2"]))
        if isinstance(value, list): value = "<br/>".join(f"• {item.get('description', item) if isinstance(item, dict) else item}" for item in value) or "None identified."
        story += [Paragraph(str(value or "None identified."), styles["BodyText"]), Spacer(1, 9)]
    doc.build(story); return buffer.getvalue()
