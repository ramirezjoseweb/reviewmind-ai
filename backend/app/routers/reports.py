from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.report import ExecutiveReportResponse
from app.models.business import Business
from app.models.review import Review
from app.models.review_analysis import ReviewAnalysis
from app.services.report_service import generate_executive_report

router = APIRouter(
    prefix="/businesses/{business_id}/reports", 
    tags=["Reports"], 
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

    return generate_executive_report(
        business=business,
        reviews=reviews,
        analyses=analyses,
    )

    