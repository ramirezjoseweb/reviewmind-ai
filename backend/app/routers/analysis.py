from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.database import get_db
from app.schemas.analysis import ReviewAnalysisReponse, BusinessAnalysisSummary
from app.models.business import Business
from app.models.review import Review
from app.models.review_analysis import ReviewAnalysis
from app.services.sentiment_service import analyze_review_text

router = APIRouter(
    prefix="/businesses/{business_id}/analysis", 
    tags=["Analysis"]
)

@router.post(
    "/run", 
    response_model=list[ReviewAnalysisReponse]
)
def run_business_analysis(
    business_id: int, 
    db: Session = Depends(get_db)
): 
    business = db.get(Business, business_id)

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado",
        ) 

    reviews = db.scalars(
        select(Review).where(Review.business_id == business_id) 
    ).all() 

    if not reviews: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este negocio no tiene reseñas que analizar",
        )

    for review in reviews: 
        result = analyze_review_text(review.text) 

        existing_analysis = db.scalar(
            select(ReviewAnalysis).where(ReviewAnalysis.id == review.id) 
        )

        if existing_analysis is None: 
            analysis = ReviewAnalysis(
                id=review.id, 
                sentiment=result["sentiment"], 
                sentiment_score=result["sentiment_score"],
                positive_aspects=result["positive_aspects"], 
                negative_aspects=result["negative_aspects"], 
            )
            db.add(analysis) 
        else: 
            existing_analysis.sentiment = result["sentiment"]
            existing_analysis.sentiment_score = result["sentiment_score"]
            existing_analysis.positive_aspects = result["positive_aspects"]
            existing_analysis.negative_aspects = result["negative_aspects"]

    db.commit() 

    analyses = db.scalars(
        select(ReviewAnalysis)
        .join(Review)
        .where(Review.business_id == business_id) 
        .order_by(ReviewAnalysis.created_at.desc()) 
    ).all()

    return analyses

@router.get(
    "", 
    response_model=BusinessAnalysisSummary, 
)
def list_business_analysis(
    business_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado", 
        )

    reviews = db.scalars(
        select(Review).where(Review.business_id == business_id)
    ).all()

    analyses = db.scalars(
        select(ReviewAnalysis)
        .join(Review) 
        .where(Review.business_id == business_id)
    ).all() 

    positive_reviews = sum(1 for analysis in analyses if analysis.sentiment == "positive") 
    negative_reviews = sum(1 for analysis in analyses if analysis.sentiment == "negative") 
    neutral_reviews = sum(1 for analysis in analyses if analysis.sentiment == "neutral") 

    if analyses:
        average_sentiment_score = sum(
            analysis.sentiment_score for analysis in analyses
        ) / len(analyses) 
    else: 
        average_sentiment_score = 0 

    positive_counter: Counter[str] = Counter()
    negative_counter: Counter[str] = Counter()

    for analysis in analyses: 
        positive_counter.update(analysis.positive_aspects) 
        negative_counter.update(analysis.negative_aspects)

    return BusinessAnalysisSummary(
        business_id=business_id, 
        total_reviews=len(reviews),
        analyzed_reviews=len(analyses), 
        positive_reviews=positive_reviews, 
        neutral_reviews=neutral_reviews, 
        negative_reviews=negative_reviews, 
        average_sentiment_score=round(average_sentiment_score, 2), 
        top_positive_aspects=[
            # Obtiene los 5 aspectos positivos más frecuentes
            aspect for aspect, _ in positive_counter.most_common(5)
        ], 
        top_negative_aspects=[
            aspect for aspect, _ in negative_counter.most_common(5)
        ], 
    )

@router.get(
    "/summary", 
    response_model=BusinessAnalysisSummary
) 
def get_business_analysis_summary(
    business_id: int, 
    db: Session = Depends(get_db) 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado", 
        )

    reviews = db.scalars(
        select(Review).where(Review.business_id == business_id) 
    ).all() 

    analyses = db.scalars(
        select(ReviewAnalysis)
        .join(Review)
        .where(Review.business_id == business_id)
    ).all() 

    positive_reviews = sum(1 for analysis in reviews if analysis.sentiment == "positive") 
    negative_reviews = sum(1 for analysis in reviews if analysis.sentiment == "negative") 
    neutral_reviews = sum(1 for analysis in reviews if analysis.sentiment == "neutral") 

    if analyses: 
        average_sentiment_score = sum(
            analysis.sentiment_score for analysis in analyses
        ) / len(analyses)
    else: 
        average_sentiment_score = 0

    positive_counter: Counter[str] = Counter() 
    negative_counter: Counter[str] = Counter() 

    for analysis in analyses: 
        positive_counter.update(analysis.positive_aspects)
        negative_counter.update(analysis.negative_aspects)

    return BusinessAnalysisSummary(
        business_id=business_id, 
        total_reviews=len(reviews), 
        analyzed_reviews=len(analyses), 
        positive_reviews=positive_reviews, 
        negative_reviews=negative_reviews,
        neutral_reviews=neutral_reviews,
        average_sentiment_score=round(average_sentiment_score, 2), 
        top_positive_aspects=[
            aspect for aspect, _ in positive_counter.most_common(5) 
        ],
        top_negative_aspects=[
            aspect for aspect, _ in negative_counter.most_common(5)
        ], 
    )