from __future__ import annotations

from app.db.database import Base

from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, DateTime

from app.models.review import Review


class ReviewAnalysis(Base): 
    __tablename__ = "review analysis"

    id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        unique=True, 
    )

    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(float, nullable=False)

    positive_aspects: Mapped[list[str]] = mapped_column(
        JSON, 
        default=list, 
        nullable=False,
    )

    negative_aspects: Mapped[list[str]] = mapped_column(
            JSON, 
            default=list, 
            nullable=False,
        )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False, 
    )

    review: Mapped["Review"] = relationship(
        back_populates="analysis", 
    )