from pydantic import ConfigDict, BaseModel, Field

from datetime import datetime


class ReviewBase(BaseModel): 
    text: str = Field(min_length=5)
    rating: int | None = Field(default=None, ge=1, le=5) 
    author: str | None = Field(default=None, max_length=150) 
    source: str | None = Field(default="manual", max_length=100)
    language: str | None = Field(default=None, max_length=20) 

class ReviewCreate(ReviewBase): 
    pass

class ReviewResponse(ReviewBase): 
    id: int 
    business_id: int 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 