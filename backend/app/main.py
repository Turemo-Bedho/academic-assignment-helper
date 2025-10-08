import uuid
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import os
import shutil
from typing import List
import requests
import json

from . import models, schemas, auth, rag_service, database
from .config import settings
from .auth import verify_token

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Academic Assignment Helper API", version="1.0.0")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth endpoints
@app.post("/auth/register", response_model=schemas.StudentResponse)
def register(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check if student already exists
    db_student = db.query(models.Student).filter(models.Student.email == student.email).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new student
    hashed_password = auth.get_password_hash(student.password)
    db_student = models.Student(
        email=student.email,
        password_hash=hashed_password,
        full_name=student.full_name,
        student_id=student.student_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    # Create token with string student ID
    access_token = auth.create_access_token(data={"sub": str(db_student.id)})
    print(f"✅ Registered student {db_student.id}, token created")
    
    return db_student



@app.post("/auth/login", response_model=schemas.Token)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    student = auth.authenticate_student(db, email, password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert student.id to string for JWT compliance
    access_token = auth.create_access_token(data={"sub": str(student.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/upload", response_model=dict)
async def upload_assignment(
    file: UploadFile = File(...),
    token_data: schemas.TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file with unique name to avoid conflicts
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create assignment record
    assignment = models.Assignment(
        student_id=token_data.student_id,
        filename=unique_filename,
        original_text=f"File stored at: {file_path}"  # We'll extract text in n8n
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    print(f"✅ File uploaded: {unique_filename}, Assignment ID: {assignment.id}")
    
    # Trigger n8n workflow
    try:
        webhook_data = {
            "assignment_id": assignment.id,
            "filename": unique_filename,
            "file_path": file_path,
            "student_id": token_data.student_id,
            "original_filename": file.filename
        }
        
        print(f"🚀 Triggering n8n workflow with data: {webhook_data}")
        
        response = requests.post(
            settings.N8N_WEBHOOK_URL, 
            json=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ n8n webhook triggered successfully")
        else:
            print(f"⚠️ n8n webhook returned status: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error calling n8n webhook: {e}")
    
    return {
        "message": "File uploaded successfully", 
        "assignment_id": assignment.id, 
        "analysis_job_id": assignment.id
    }




@app.get("/analysis/{analysis_id}", response_model=schemas.AnalysisResultResponse)
def get_analysis(
    analysis_id: int,
    token_data: schemas.TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # Verify the assignment belongs to the student
    analysis = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    assignment = db.query(models.Assignment).filter(models.Assignment.id == analysis.assignment_id).first()
    if assignment.student_id != token_data.student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return analysis




@app.get("/sources", response_model=schemas.SourceSearchResponse)
def search_sources(
    query: str,
    token_data: schemas.TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    rag = rag_service.RAGService()
    sources = rag.search_similar_sources(db, query)
    return {"query": query, "sources": sources}



# Internal endpoint for n8n to store analysis results
@app.post("/internal/store-analysis")
async def store_analysis_results(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint for n8n workflow to store analysis results
    Expects JSON with: assignment_id, suggested_sources, plagiarism_score, 
    flagged_sections, research_suggestions, citation_recommendations, confidence_score
    """
    try:
        print(f"📥 Received analysis results for assignment: {request}")
        
        # Extract data from request
        assignment_id = request.get("assignment_id")
        suggested_sources = request.get("suggested_sources", [])
        plagiarism_score = request.get("plagiarism_score", 0.0)
        flagged_sections = request.get("flagged_sections", [])
        research_suggestions = request.get("research_suggestions", "")
        citation_recommendations = request.get("citation_recommendations", "")
        confidence_score = request.get("confidence_score", 0.0)
        
        # Validate assignment exists
        assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
        if not assignment:
            return JSONResponse(
                status_code=404,
                content={"error": f"Assignment {assignment_id} not found"}
            )
        
        # Create analysis result
        analysis = models.AnalysisResult(
            assignment_id=assignment_id,
            suggested_sources=suggested_sources,
            plagiarism_score=plagiarism_score,
            flagged_sections=flagged_sections,
            research_suggestions=research_suggestions,
            citation_recommendations=citation_recommendations,
            confidence_score=confidence_score
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        print(f"✅ Analysis stored with ID: {analysis.id}")
        
        return {
            "status": "success", 
            "analysis_id": analysis.id,
            "message": "Analysis results stored successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error storing analysis: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to store analysis: {str(e)}"}
        )


# Health check
@app.get("/")
def read_root():
    return {"message": "Academic Assignment Helper API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}