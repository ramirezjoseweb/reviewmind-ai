from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse


from app.config import settings
from app.db.database import get_db
from app.schemas.report import ExecutiveReportResponse
from app.models.business import Business
from app.models.review import Review
from app.models.review_analysis import ReviewAnalysis
from app.models.report import Report
from app.services.report_service import generate_executive_report
from app.services.pdf_report_service import build_report_filename, build_report_pdf
from app.services.ai_report_service import generate_ai_executive_report

router = APIRouter(
    prefix="/businesses/{business_id}/reports", 
    tags=["Reports"], 
)

def build_report_response(
        report: Report, 
        business: Business, 
) -> ExecutiveReportResponse: 
    return ExecutiveReportResponse(
        id=report.id, 
        business_id=business.id, 
        business_name=business.name,
        generated_at=report.created_at, 
        executive_summary=report.executive_summary, 
        sentiment_overview=report.sentiment_overview, 
        strengths=report.strengths, 
        weaknesses=report.weaknesses, 
        recommendations=report.recommendations,
        priority_actions=report.priority_actions, 
    )

@router.post(
    "/generate", 
    response_model=ExecutiveReportResponse, 
)
def generate_business_report(
    business_id: int, 
    db: Session = Depends(get_db)
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encuentra el negocio",
        )

    reviews = db.scalars(
        select(Review).where(Review.business_id == business_id)
    ).all() 

    if not reviews: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Business has no reviews", 
        )

    analyses = db.scalars(
        select(ReviewAnalysis)
        .join(Review)
        .where(Review.business_id == business_id) 
    ).all() 

    if not analyses: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este negocio no tiene análisis. Ejecuta un análisis antes de generar el informe."
        )

    if settings.enable_ai_reports:
        try:
            print("AI reports enabled. Trying OpenAI...")
            raft = generate_ai_executive_report(
                business=business,
                reviews=reviews,
                analyses=analyses,
            )
            print("OpenAI report generated successfully.")
        except Exception as error:
            print(f"OpenAI report failed. Falling back to rules. Error: {error}")
            draft = generate_executive_report(
                business=business,
                reviews=reviews,
                analyses=analyses,
            )
    else:
        print("AI reports disabled. Using rules report.")
        draft = generate_executive_report(
            business=business,
            reviews=reviews,
            analyses=analyses,
        )

    report = Report(
        business_id=business.id,
        executive_summary=draft.executive_summary,
        sentiment_overview=draft.sentiment_overview,
        strengths=draft.strengths,
        weaknesses=draft.weaknesses,
        recommendations=draft.recommendations,
        priority_actions=draft.priority_actions,
    )

    db.add(report)
    db.commit() 
    db.refresh(report)

    return build_report_response(report=report, business=business)

@router.get(
    "", 
    response_model=list[ExecutiveReportResponse]
)
def list_business_reports(
    business_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado"
        )

    reports = db.scalars(
        select(Report)
        .where(Report.business_id == business_id)
        .order_by(Report.created_at.desc())
    ).all()

    return [
        build_report_response(report=report, business= business)
        for report in reports
    ]

@router.get(
    "/latest",
    response_model=ExecutiveReportResponse 
)
def get_latest_business_report(
    business_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id)

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado", 
        )

    """report = db.scalars(
        select(Report)
        .where(Report.business_id == business_id)
        .order_by(Report.created_at.desc())
    )

    if report is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se han encontrado informes",
        )
    """

    statement = (
        select(Report)
        .where(Report.business_id == business_id)
        .order_by(Report.created_at.desc())
        .limit(1) 
    )

    report = db.scalars(statement).first()

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay informes generados para este negocio",
        )


    return build_report_response(report=report, business=business) 

@router.get("/latest/pdf")
def download_latest_business_report_pdf(
    business_id: int, 
    db: Session = Depends(get_db) 
): 
    business = db.get(Business, business_id)

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encuentra el negocio"
        )

    report = db.scalar(
        select(Report)
        .where(Report.business_id == business_id) 
        .order_by(Report.created_at.desc())
    )

    if report is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se han encontrado informes para este negocio"
        )

    pdf_buffer = build_report_pdf(
        business = business, 
        report = report, 
    )

    filename = build_report_filename(business.name) 

    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"', 
        },
    ) 