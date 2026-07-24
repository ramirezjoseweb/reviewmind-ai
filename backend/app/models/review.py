from __future__ import annotations
from typing import TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING: # esto sirve para evitar importaciones circulares y mejorar el rendimiento. Cuando se utiliza TYPE_CHECKING, las importaciones dentro de este bloque solo se evaluarán durante la verificación de tipos (por ejemplo, con herramientas como mypy) y no se ejecutarán en tiempo de ejecución. Esto es útil cuando se tienen dependencias entre módulos que podrían causar problemas si se importan directamente.
    from app.models.business import Business
    from app.models.review_analysis import ReviewAnalysis

from sqlalchemy import ForeignKey, Integer, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

class Review(Base): 
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), # esto define una relación de clave foránea entre la tabla "reviews" y la tabla "businesses". La columna "business_id" en la tabla "reviews" hace referencia a la columna "id" en la tabla "businesses". La opción ondelete="CASCADE" significa que si un negocio se elimina, todas las reseñas asociadas a ese negocio también se eliminarán automáticamente.
        nullable=False, 
        index=True,
    )

    text: Mapped[str] = mapped_column(Text, nullable=False) 
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author: Mapped[str | None] = mapped_column(String(150), nullable=True)
    source: Mapped[str | None] = mapped_column(String(150), nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )

    business: Mapped["Business"] = relationship(
        "Business", 
        back_populates = "reviews", 
    ) # esto establece una relación bidireccional entre la clase Review y la clase Business. La propiedad "business" en la clase Review permite acceder al negocio asociado a una reseña, mientras que la propiedad "reviews" en la clase Business permite acceder a todas las reseñas asociadas a ese negocio.

    analysis: Mapped["ReviewAnalysis | None"] = relationship(
        "Analysis", 
        back_populates= "review", 
        cascade="all, delete-orphan", 
        uselist=False, 
    )