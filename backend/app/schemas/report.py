from datetime import datetime

from pydantic import BaseModel

class ExecutiveReportResponse(BaseModel): 
    business_id: int
    business_name: str
    generated_at: datetime  
    executive_summary: str
    sentiment_overview: str
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    priority_actions: list[str]

