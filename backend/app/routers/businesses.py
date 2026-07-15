from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.business import BusinessCreate, BusinessResponse
from app.db.database import get_db 
from app.models.business import Business

router = APIRouter(
    prefix="/businesses", 
    tags=["Businesses"], 
)

@router.post(
    "", 
    response_model=BusinessResponse, 
    status_code=status.HTTP_201_CREATED,
)
def create_business(
    business_data: BusinessCreate, 
    db: Session = Depends(get_db), 
): 
    business = Business(
        name = business_data.name, 
        category = business_data.category, 
        location = business_data.location,
    )

    db.add(business)
    db.commit() 
    db.refresh(business) 

    return business 


@router.get(
    "", 
    response_model=list[BusinessResponse], 
)
def list_business(
    db: Session = Depends(get_db), 
):
    statement = select(Business).order_by(Business.created_at.desc())
    businesses = db.scalars(statement).all() # db.scalars(statement) ejecuta la consulta SQL generada por el objeto statement 
    # y devuelve un objeto que contiene los resultados de la consulta.
    return businesses

@router.get(
    "/{business_id}", 
    response_model=BusinessResponse,
)
def get_business(
    business_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Negocio no encontrado", 
        )
    
    return business