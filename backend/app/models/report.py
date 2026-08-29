from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON

if TYPE_CHECKING: 
    from app.models.business import Business

class Report(Base): 
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True,) 
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE", nullable=False, index=True,) 
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False,)
    sentiment_overview: Mapped[str] = mapped_column(Text, nullable=False,) 
    strengths: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False,
    ) 
    weaknesses: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False,
    ) 
    recommendations: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False,
    )
    priority_actions: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow(), nullable=False,) 

    business: Mapped["Business"] = relationship(
        back_populates="reports", 
    )