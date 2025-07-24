from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import json
from passlib.context import CryptContext
import openai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import base64
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import get_db, engine
from models import Base, User, Job, Application, Notification
from schemas import (
    UserCreate, UserLogin, JobCreate, JobUpdate, ApplicationCreate,
    NotificationCreate, UserResponse, JobResponse, ApplicationResponse
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Assist AI", description="AI-powered HR recruitment platform")

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Azure OpenAI setup
openai.api_type = "azure"
openai.api_base = "https://openai-poc2-agcs.openai.azure.com"
openai.api_version = "2025-01-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Azure OpenAI deployment name
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini-xmj"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory first
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    
    # Simple JWT implementation
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip('=')
    
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_token(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
        
        if signature_b64 != expected_signature_b64:
            return None
            
        # Decode payload
        payload_b64 += '=' * (4 - len(payload_b64) % 4)  # Add padding
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        # Check expiration
        if payload.get('exp', 0) < datetime.utcnow().timestamp():
            return None
            
        return payload
    except Exception:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/api/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        user_type=user.user_type,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User registered successfully", "user_id": db_user.id}

@app.post("/api/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": db_user.user_type,
        "user_id": db_user.id
    }

# Job management routes
@app.post("/api/jobs", response_model=JobResponse)
def create_job(job: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can create jobs")
    
    db_job = Job(**job.dict(), created_by=current_user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type == "hr":
        # HR users only see jobs they created
        jobs = db.query(Job).filter(Job.is_active == True, Job.created_by == current_user.id).all()
    else:
        # Candidates see all active jobs
        jobs = db.query(Job).filter(Job.is_active == True).all()
    return jobs

@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.put("/api/jobs/{job_id}")
def update_job(job_id: int, job_update: JobUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can update jobs")
    
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can delete jobs")
    
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db_job.is_active = False
    db.commit()
    return {"message": "Job deleted successfully"}

# Application routes
@app.post("/api/applications")
async def create_application(
    job_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    experience_years: int = Form(...),
    relevant_experience: str = Form(...),
    skills: str = Form(...),
    education: str = Form(...),
    projects: str = Form(...),
    preferred_location: str = Form(...),
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")
    
    # Save photo
    photo_filename = f"{current_user.id}_{job_id}_{photo.filename}"
    photo_path = f"uploads/{photo_filename}"
    with open(photo_path, "wb") as buffer:
        content = await photo.read()
        buffer.write(content)
    
    # Calculate AI matching score
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    ai_score = calculate_ai_score(job, {
        "experience_years": experience_years,
        "relevant_experience": relevant_experience,
        "skills": skills,
        "education": education,
        "projects": projects
    })
    
    db_application = Application(
        job_id=job_id,
        candidate_id=current_user.id,
        name=name,
        email=email,
        phone=phone,
        address=address,
        experience_years=experience_years,
        relevant_experience=relevant_experience,
        skills=skills,
        education=education,
        projects=projects,
        preferred_location=preferred_location,
        photo_path=photo_path,
        ai_score=ai_score
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return {"message": "Application submitted successfully", "ai_score": ai_score}

@app.get("/api/jobs/{job_id}/applications")
def get_job_applications(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can view applications")
    
    # Check if the job belongs to the current HR user
    job = db.query(Job).filter(Job.id == job_id, Job.created_by == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or you don't have permission to view its applications")
    
    applications = db.query(Application).filter(Application.job_id == job_id).all()
    return applications

@app.post("/api/applications/{application_id}/shortlist")
def shortlist_candidate(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can shortlist candidates")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = "shortlisted"
    db.commit()
    
    # Generate interview questions
    job = db.query(Job).filter(Job.id == application.job_id).first()
    questions = generate_interview_questions(job, application)
    
    # Create notification
    notification = Notification(
        user_id=application.candidate_id,
        title="Congratulations! You've been shortlisted",
        message=f"You have been shortlisted for the position: {job.title}. Interview details will be shared soon.",
        notification_type="shortlist"
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Candidate shortlisted successfully", "questions": questions}

@app.get("/api/applications/{application_id}/questions/pdf")
def download_questions_pdf(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can download questions")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    questions = generate_interview_questions(job, application)
    
    # Generate PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # PDF content
    p.drawString(100, 750, f"Interview Questions - {job.title}")
    p.drawString(100, 730, f"Candidate: {application.name}")
    p.drawString(100, 710, "-" * 50)
    
    y_position = 680
    for i, question in enumerate(questions, 1):
        p.drawString(100, y_position, f"{i}. {question}")
        y_position -= 30
        if y_position < 100:
            p.showPage()
            y_position = 750
    
    p.save()
    buffer.seek(0)
    
    # Save to file
    pdf_filename = f"interview_questions_{application_id}.pdf"
    pdf_path = f"uploads/{pdf_filename}"
    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())
    
    return FileResponse(pdf_path, filename=pdf_filename)

# Notification routes
@app.get("/api/notifications")
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return notifications

@app.put("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

# User profile routes
@app.get("/api/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "user_type": current_user.user_type
    }

@app.put("/api/profile")
def update_profile(
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if email:
        current_user.email = email
    if phone:
        current_user.phone = phone
    if address:
        current_user.address = address
    
    db.commit()
    return {"message": "Profile updated successfully"}

# AI Helper functions
def calculate_ai_score(job, candidate_data):
    """Calculate AI matching score based on job requirements and candidate data"""
    try:
        prompt = f"""
        Job Requirements:
        - Title: {job.title}
        - Required Experience: {job.experience_years} years
        - Skills: {job.skills}
        - Description: {job.description}
        
        Candidate Profile:
        - Experience: {candidate_data['experience_years']} years
        - Relevant Experience: {candidate_data['relevant_experience']}
        - Skills: {candidate_data['skills']}
        - Education: {candidate_data['education']}
        - Projects: {candidate_data['projects']}
        
        Rate this candidate's fit for the job on a scale of 1-10. Consider experience match, skill alignment, and overall suitability. Return only the number.
        """
        
        response = openai.ChatCompletion.create(
            engine=AZURE_DEPLOYMENT_NAME,  # Use engine instead of model for Azure
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.3
        )
        
        score = float(response.choices[0].message.content.strip())
        return min(max(score, 1), 10)  # Ensure score is between 1-10
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fallback scoring logic
        return calculate_fallback_score(job, candidate_data)

def calculate_fallback_score(job, candidate_data):
    """Fallback scoring when OpenAI is not available"""
    score = 5  # Base score
    
    # Experience matching
    if candidate_data['experience_years'] >= job.experience_years:
        score += 2
    elif candidate_data['experience_years'] >= job.experience_years * 0.7:
        score += 1
    
    # Skill matching (simple keyword matching)
    job_skills = job.skills.lower().split(',')
    candidate_skills = candidate_data['skills'].lower().split(',')
    
    skill_matches = 0
    for job_skill in job_skills:
        for candidate_skill in candidate_skills:
            if job_skill.strip() in candidate_skill.strip():
                skill_matches += 1
                break
    
    if skill_matches >= len(job_skills) * 0.8:
        score += 2
    elif skill_matches >= len(job_skills) * 0.5:
        score += 1
    
    return min(max(score, 1), 10)

def generate_interview_questions(job, application):
    """Generate interview questions using AI"""
    try:
        prompt = f"""
        Generate 10 interview questions for the following job and candidate:
        
        Job: {job.title}
        Job Description: {job.description}
        Required Skills: {job.skills}
        Experience Required: {job.experience_years} years
        
        Candidate Skills: {application.skills}
        Candidate Experience: {application.experience_years} years
        Candidate Projects: {application.projects}
        
        Generate 10 relevant interview questions that test both technical skills and cultural fit.
        Return each question on a new line.
        """
        
        response = openai.ChatCompletion.create(
            engine=AZURE_DEPLOYMENT_NAME,  # Use engine instead of model for Azure
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        questions = response.choices[0].message.content.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fallback questions
        return [
            "Tell me about yourself and your relevant experience.",
            "Why are you interested in this position?",
            "What are your key technical skills?",
            "Describe a challenging project you worked on.",
            "How do you handle tight deadlines?",
            "What motivates you in your work?",
            "How do you stay updated with industry trends?",
            "Describe your ideal work environment.",
            "What are your career goals?",
            "Do you have any questions for us?"
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
