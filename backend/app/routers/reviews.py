import io 
import pandas as pd


from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.business import Business
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewImportResponse
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

@router.delete(
    "/{review_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    business_id: int, 
    review_id: int, 
    db: Session = Depends(get_db), 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado", 
        )

    review = db.scalar(
        select(Review).where(
            Review.id == review_id, 
            Review.business_id == business_id, 
        )
    )

    if review is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Negocio no encontrado", 
        )

    db.delete(review) 
    db.commit() 

    return None 

@router.post(
    prefix="/import-csv", 
    response_model=ReviewImportResponse, 
    status_code=status.HTTP_201_CREATED, 
)
async def import_reviews_from_csv(
    business_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db) 
): 
    business = db.get(Business, business_id) 

    if business is None: 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail="No se encuentra el negocio"
        )

    if not file.filename or not file.filename.endswith(".csv"): 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Solo se permiten archivos .csv"
        )

    content = await file.read() 

    try:
        # Convierte el contenido del archivo en memoria en un DataFrame de pandas.
        dataframe = pd.read_csv(io.BytesIO(content))
    except Exception as error: 
        # Devuelve un error si el archivo no se puede interpretar como un CSV válido.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Archivo CSV inválido: {error}", 
        ) from error

    # Normaliza los nombres de las columnas eliminando espacios y usando minúsculas.
    dataframe.columns = [
        str(column).strip().lower() for column in dataframe.columns
    ]

    if "text" not in dataframe.columns: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El CSV debe tener una columna 'text'", 
        )

    imported_reviews = 0 
    skipped_rows = 0 
    errors: list[str] = []

    for index, row in dataframe.iterrows(): 
        raw_text = row.get("text")  # Obtiene el texto sin asumir otras columnas.

        if pd.isna(raw_text) or not str(raw_text).strip(): 
            skipped_rows += 1 
            errors.append(f"Fila {index + 2}: falta el texto") 
            continue

        text = str(raw_text).strip() 

        raw_rating = row.get("rating") 
        rating: int | None = None

        if raw_rating is not None and not pd.isna(raw_rating): 
            try: 
                rating = int(raw_rating)
                if rating < 1 or rating > 5:
                    raise ValueError("La puntuación debe estar entre 1 y 5")
            except Exception:
                skipped_rows += 1
                errors.append(f"Fila {index + 2}: puntuación inválida")
                continue

        author = row.get("author")
        source = row.get("source")
        language = row.get("language")

        review = Review(
            business_id=business_id,
            text=text,
            rating=rating,
            author=None if pd.isna(author) else str(author).strip(),
            source="csv" if pd.isna(source) else str(source).strip(),
            language=None if pd.isna(language) else str(language).strip(),
        )

        db.add(review)
        imported_reviews += 1

    db.commit()

    return ReviewImportResponse(
        imported_reviews=imported_reviews,
        skipped_rows=skipped_rows,
        errors=errors,
    )