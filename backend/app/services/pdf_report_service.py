from html import escape
from io import BytesIO
from re import sub

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from app.models.business import Business
from app.models.report import Report


def build_report_pdf(
    business: Business,
    report: Report,
) -> BytesIO:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Informe ReviewMind AI - {business.name}",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        spaceAfter=14,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor="#475569",
        spaceAfter=18,
    )

    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        spaceAfter=8,
    )

    item_style = ParagraphStyle(
        "ListItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        leftIndent=12,
        spaceAfter=5,
    )

    story = []

    story.append(Paragraph("Informe ejecutivo - ReviewMind AI", title_style))
    story.append(
        Paragraph(
            f"Negocio: {escape(business.name)}<br/>"
            f"Fecha de generacion: {report.created_at.strftime('%d/%m/%Y %H:%M')}",
            subtitle_style,
        )
    )

    add_section(
        story=story,
        title="Resumen ejecutivo",
        content=report.executive_summary,
        section_title_style=section_title_style,
        body_style=body_style,
    )

    add_section(
        story=story,
        title="Vision general del sentimiento",
        content=report.sentiment_overview,
        section_title_style=section_title_style,
        body_style=body_style,
    )

    add_list_section(
        story=story,
        title="Fortalezas principales",
        items=report.strengths,
        section_title_style=section_title_style,
        item_style=item_style,
    )

    add_list_section(
        story=story,
        title="Debilidades principales",
        items=report.weaknesses,
        section_title_style=section_title_style,
        item_style=item_style,
    )

    add_list_section(
        story=story,
        title="Recomendaciones",
        items=report.recommendations,
        section_title_style=section_title_style,
        item_style=item_style,
    )

    add_list_section(
        story=story,
        title="Acciones prioritarias",
        items=report.priority_actions,
        section_title_style=section_title_style,
        item_style=item_style,
    )

    story.append(Spacer(1, 18))
    story.append(
        Paragraph(
            "Documento generado automaticamente por ReviewMind AI.",
            subtitle_style,
        )
    )

    document.build(story)
    buffer.seek(0)

    return buffer


def add_section(
    story: list,
    title: str,
    content: str,
    section_title_style: ParagraphStyle,
    body_style: ParagraphStyle,
) -> None:
    story.append(Paragraph(escape(title), section_title_style))
    story.append(Paragraph(escape(content), body_style))


def add_list_section(
    story: list,
    title: str,
    items: list[str],
    section_title_style: ParagraphStyle,
    item_style: ParagraphStyle,
) -> None:
    story.append(Paragraph(escape(title), section_title_style))

    if not items:
        story.append(Paragraph("- Sin datos disponibles.", item_style))
        return

    for item in items:
        story.append(Paragraph(f"- {escape(item)}", item_style))


def build_report_filename(business_name: str) -> str:
    clean_name = business_name.lower().strip()
    clean_name = sub(r"[^a-z0-9]+", "-", clean_name)
    clean_name = clean_name.strip("-") or "negocio"

    return f"reviewmind-{clean_name}-informe.pdf"