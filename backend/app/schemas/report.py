from datetime import datetime

from pydantic import BaseModel

class ExecutiveReportDraft(BaseModel): 
    business_id: int
    business_name: str
    generated_at: datetime  
    executive_summary: str
    sentiment_overview: str
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    priority_actions: list[str]
    
class ExecutiveReportResponse(BaseModel): 
    id: int
    business_id: int
    business_name: str
    generated_at: datetime  
    executive_summary: str
    sentiment_overview: str
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    priority_actions: list[str]

