from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.business import Business
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.db.database import get_db

router = APIRouter(
    prefix="/businesses/{business_id}/reviews", 
    tags=["Reviews"],
)

@router.post(
    "", 
    response_model=ReviewResponse, 
    status_code=status.HTTP_201_CREATED, 
)
def create_review(
    business_id: int, 
    review_data: ReviewCreate, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id) # aqui creamos... 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado"
        )

    review = Review(
        business_id=business_id, 
        text=review_data.text, 
        rating=review_data.rating, 
        author=review_data.author, 
        source=review_data.source, 
        language=review_data.language, 
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review

@router.get(
    "", 
    response_model=list[ReviewResponse], 
)
def list_reviews(
    business_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id)

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado"
        )
    
    statement = (
        select(Review)
        .where(Review.business_id == business_id)
        .order_by(Review.created_at.desc()) 
    )

    reviews = db.scalars(statement).all() 

    return reviews