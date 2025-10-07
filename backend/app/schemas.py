from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Dict, Any, Optional

class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    student_id: str

class StudentResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    student_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    student_id: Optional[int] = None

class AssignmentUpload(BaseModel):
    filename: str

class AssignmentResponse(BaseModel):
    id: int
    filename: str
    topic: Optional[str]
    academic_level: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True

class AnalysisResultResponse(BaseModel):
    id: int
    assignment_id: int
    suggested_sources: List[Dict[str, Any]]
    plagiarism_score: float
    flagged_sections: List[Dict[str, Any]]
    research_suggestions: str
    citation_recommendations: str
    confidence_score: float
    analyzed_at: datetime

    class Config:
        from_attributes = True

class SourceSearchResponse(BaseModel):
    query: str
    sources: List[Dict[str, Any]]