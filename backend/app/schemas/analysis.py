from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReviewAnalysisReponse(BaseModel): 
    id: int
    review_id: int 
    sentiment: str
    sentiment_score: float 
    positive_aspects: list[str]
    negative_aspects: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 

class AspectCount(BaseModel): 
    name: str 
    count: int    

class BusinessAnalysisSummary(BaseModel):
    business_id: int 
    total_reviews: int 
    analyzed_reviews: int 
    positive_reviews: int 
    negative_reviews: int 
    neutral_reviews: int
    average_sentiment_score: float
    top_positive_aspects: list[AspectCount]
    top_negative_aspects: list[AspectCount]