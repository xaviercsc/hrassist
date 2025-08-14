from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import re
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import json
from passlib.context import CryptContext
import openai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import io
import base64
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = [
    "OPENAI_API_KEY", "AZURE_API_VERSION", "AZURE_ENDPOINT", "AZURE_DEPLOYMENT_NAME",
    "AZURE_MODEL_NAME", "AZURE_MODEL_VERSION",
    "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "HR_ADMIN_SECRET_CODE"
]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

from database import get_db, engine
from models import Base, User, Job, Application, Notification, Interview
from schemas import (
    UserCreate, UserLogin, JobCreate, JobUpdate, ApplicationCreate,
    NotificationCreate, UserResponse, JobResponse, ApplicationResponse,
    InterviewSchedule, InterviewResponse
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Assist AI", description="AI-powered HR recruitment platform")

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Admin configuration
HR_ADMIN_SECRET_CODE = os.getenv("HR_ADMIN_SECRET_CODE")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Azure OpenAI setup
from openai import AzureOpenAI

# Azure OpenAI client configuration
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

# Azure OpenAI deployment details
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")  # Deployment name
AZURE_MODEL_NAME = os.getenv("AZURE_MODEL_NAME")  # Model name
AZURE_MODEL_VERSION = os.getenv("AZURE_MODEL_VERSION")  # Model version

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
    try:
        # Validate admin secret code for HR users
        if user.user_type == "hr":
            if not user.admin_code:
                raise HTTPException(
                    status_code=400, 
                    detail="Admin secret code is required for HR registration"
                )
            if user.admin_code != HR_ADMIN_SECRET_CODE:
                print(f"Invalid admin code attempt: '{user.admin_code}' vs expected '{HR_ADMIN_SECRET_CODE}'")
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid admin secret code. Please contact administrator."
                )
        
        # Check if user exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email exists
        db_user_email = db.query(User).filter(User.email == user.email).first()
        if db_user_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
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
        
        print(f"User registered successfully: {user.username} ({user.user_type})")
        return {"message": "User registered successfully", "user_id": db_user.id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

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
    
    # Create job with enhanced fields
    job_data = job.dict()
    job_data['is_closed'] = False
    job_data['created_by'] = current_user.id
    
    db_job = Job(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Create notification for HR about job creation
    hr_notification = Notification(
        user_id=current_user.id,
        title=f"Job Posted Successfully - {job.title}",
        message=f"""✅ Your job posting has been created successfully!

Job Details:
💼 Position: {job.title}
📍 Location: {job.work_location}
👥 Vacancies: {job.number_of_vacancies}
💰 Salary: {job.salary_range if job.salary_range else 'Not specified'}
⏰ Application Deadline: {job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else 'No deadline set'}

The position is now live and candidates can start applying.""",
        notification_type="job_created"
    )
    db.add(hr_notification)
    db.commit()
    
    return db_job

@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type == "hr":
        # HR users see all jobs they created (including closed ones)
        jobs = db.query(Job).filter(Job.created_by == current_user.id).all()
    else:
        # Candidates see only active, non-closed jobs with available vacancies
        jobs = db.query(Job).filter(
            Job.is_active == True,
            Job.is_closed == False,
            Job.number_of_vacancies > 0
        ).all()
        
        # Filter by application deadline
        current_date = datetime.now().date()
        jobs = [job for job in jobs if not job.application_deadline or job.application_deadline.date() >= current_date]
    
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

@app.post("/api/applications/{application_id}/reject")
def reject_candidate(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can reject candidates")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = "rejected"
    db.commit()
    
    # Get job details for notification
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    # Create notification
    notification = Notification(
        user_id=application.candidate_id,
        title="Application Update",
        message=f"Thank you for your interest in the position: {job.title}. After careful consideration, we have decided to move forward with other candidates.",
        notification_type="rejection"
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Candidate rejected successfully"}

@app.post("/api/applications/{application_id}/schedule-interview")
async def schedule_interview(
    application_id: int,
    interview_data: InterviewSchedule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can schedule interviews")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Create interview datetime
    interview_datetime_str = f"{interview_data.interview_date} {interview_data.interview_time}"
    try:
        interview_datetime = datetime.strptime(interview_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    # Check for scheduling conflicts
    conflict = check_interview_conflict(
        db, interview_datetime, interview_data.duration_minutes, current_user.id
    )
    if conflict:
        conflict_app = db.query(Application).filter(Application.id == conflict.application_id).first()
        raise HTTPException(
            status_code=409, 
            detail=f"Interview conflict! You already have an interview scheduled at this time with {conflict_app.name} from {conflict.interview_date.strftime('%H:%M')} to {(conflict.interview_date + timedelta(minutes=conflict.duration_minutes)).strftime('%H:%M')}"
        )
    
    # Create interview record
    interview_record = Interview(
        application_id=application_id,
        interview_type=interview_data.interview_type,
        interview_date=interview_datetime,
        interview_time=interview_data.interview_time,
        duration_minutes=interview_data.duration_minutes,
        timezone=interview_data.timezone,
        platform=interview_data.platform,
        meeting_link=interview_data.meeting_link,
        meeting_password=interview_data.meeting_password,
        notes=interview_data.notes,
        created_by=current_user.id
    )
    db.add(interview_record)
    
    # Update application status
    if interview_data.interview_type == "technical":
        application.status = "interview_scheduled"
        application.technical_interview_date = interview_datetime
    elif interview_data.interview_type == "hr":
        application.status = "hr_round"
        application.hr_interview_date = interview_datetime
    
    # Get job details for notification
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    # Platform names for display
    platform_names = {
        "webex": "Cisco Webex",
        "teams": "Microsoft Teams", 
        "zoom": "Zoom",
        "google-meet": "Google Meet"
    }
    
    # Create detailed notification message for candidate
    candidate_message = f"""Congratulations! Your {interview_data.interview_type} interview has been scheduled for: {job.title}

Interview Details:
📅 Date: {interview_data.interview_date}
🕒 Time: {interview_data.interview_time} ({interview_data.timezone})
⏱️ Duration: {interview_data.duration_minutes} minutes
💻 Platform: {platform_names.get(interview_data.platform, interview_data.platform)}
🔗 Meeting Link: {interview_data.meeting_link}"""
    
    if interview_data.meeting_password:
        candidate_message += f"\n🔐 Meeting Password: {interview_data.meeting_password}"
    
    if interview_data.notes:
        candidate_message += f"\n📝 Additional Notes: {interview_data.notes}"
    
    candidate_message += "\n\nPlease join the meeting a few minutes early. Good luck!"
    
    # Create notification for candidate
    candidate_notification = Notification(
        user_id=application.candidate_id,
        title=f"{interview_data.interview_type.title()} Interview Scheduled!",
        message=candidate_message,
        notification_type="interview",
        interview_date=interview_datetime,
        interview_time=f"{interview_data.interview_time} ({interview_data.timezone})",
        webex_link=interview_data.meeting_link,
        meeting_password=interview_data.meeting_password,
        interview_duration=interview_data.duration_minutes
    )
    db.add(candidate_notification)
    
    # Create notification for HR
    hr_message = f"""Interview Scheduled Successfully!

You have scheduled a {interview_data.interview_type} interview for:
👤 Candidate: {application.name}
💼 Position: {job.title}
📅 Date: {interview_data.interview_date}
🕒 Time: {interview_data.interview_time} ({interview_data.timezone})
⏱️ Duration: {interview_data.duration_minutes} minutes
💻 Platform: {platform_names.get(interview_data.platform, interview_data.platform)}
🔗 Meeting Link: {interview_data.meeting_link}"""
    
    if interview_data.meeting_password:
        hr_message += f"\n🔐 Meeting Password: {interview_data.meeting_password}"
    
    if interview_data.notes:
        hr_message += f"\n📝 Notes: {interview_data.notes}"
    
    hr_notification = Notification(
        user_id=current_user.id,
        title=f"Interview Scheduled - {application.name}",
        message=hr_message,
        notification_type="interview_scheduled",
        interview_date=interview_datetime,
        interview_time=f"{interview_data.interview_time} ({interview_data.timezone})",
        webex_link=interview_data.meeting_link,
        meeting_password=interview_data.meeting_password,
        interview_duration=interview_data.duration_minutes
    )
    db.add(hr_notification)
    
    db.commit()
    
@app.put("/api/interviews/{interview_id}/update-result")
async def update_interview_result(
    interview_id: int,
    result_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can update interview results")
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    application = db.query(Application).filter(Application.id == interview.application_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    result = result_data.get("result")  # "passed", "failed"
    feedback = result_data.get("feedback", "")
    
    # Update interview record
    interview.result = result
    interview.feedback = feedback
    interview.conducted_date = datetime.now()
    
    if result == "passed":
        if interview.interview_type == "technical":
            # Technical interview passed, move to HR round
            application.status = "technical_passed"
            
            # Create notification for candidate
            notification = Notification(
                user_id=application.candidate_id,
                title="Technical Interview - Congratulations!",
                message=f"""Great news! You have successfully passed the technical interview for: {job.title}

Next Steps:
🎉 You've cleared the technical round
👥 HR interview will be scheduled soon
📧 Please wait for further communication

{f'Feedback: {feedback}' if feedback else ''}

Keep up the excellent work!""",
                notification_type="interview_result"
            )
            db.add(notification)
            
        elif interview.interview_type == "hr":
            # HR interview passed, move to selection
            application.status = "hr_passed"
            
            # Create notification for candidate
            notification = Notification(
                user_id=application.candidate_id,
                title="HR Interview - Congratulations!",
                message=f"""Excellent! You have successfully completed all interview rounds for: {job.title}

Status Update:
🎉 You've cleared the HR round
⭐ You are now being considered for final selection
📞 We may contact you soon for next steps

{f'Feedback: {feedback}' if feedback else ''}

Thank you for your patience during this process!""",
                notification_type="interview_result"
            )
            db.add(notification)
    
    else:  # Failed
        application.status = "rejected"
        application.rejection_reason = f"{interview.interview_type.title()} interview: {feedback}" if feedback else f"Did not pass {interview.interview_type} interview"
        
        # Create notification for candidate
        notification = Notification(
            user_id=application.candidate_id,
            title=f"{interview.interview_type.title()} Interview Update",
            message=f"""Thank you for taking the time to interview for: {job.title}

Update:
📝 We have completed our evaluation
🙏 While we were impressed with your background, we have decided to move forward with other candidates

{f'Feedback: {feedback}' if feedback else ''}

We encourage you to apply for future opportunities that match your skills. Best of luck in your job search!""",
            notification_type="interview_result"
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": f"Interview result updated: {result}"}

@app.post("/api/applications/{application_id}/select-candidate")
async def select_candidate(
    application_id: int,
    selection_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can select candidates")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "hr_passed":
        raise HTTPException(status_code=400, detail="Candidate must pass HR interview before selection")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    # Set willingness confirmation deadline (default 7 days)
    deadline_days = selection_data.get("willingness_deadline_days", 7)
    willingness_deadline = datetime.now() + timedelta(days=deadline_days)
    
    # Update application status
    application.status = "selected"
    application.selected_date = datetime.now()
    application.willingness_deadline = willingness_deadline
    
    # Get selection details
    salary_offered = selection_data.get("salary_offered")
    start_date = selection_data.get("start_date")
    additional_notes = selection_data.get("notes", "")
    
    # Create detailed selection notification
    message = f"""🎉 Congratulations! We are pleased to offer you the position of: {job.title}

Offer Details:"""

    if salary_offered:
        message += f"\n💰 Salary: {salary_offered}"
    if start_date:
        message += f"\n📅 Proposed Start Date: {start_date}"
    
    message += f"""

Next Steps:
✅ Please confirm your willingness to join by: {willingness_deadline.strftime('%Y-%m-%d %H:%M')}
📧 Reply to this notification with your confirmation
📞 Our HR team will contact you with further details

{f'Additional Information: {additional_notes}' if additional_notes else ''}

We look forward to welcoming you to our team!"""
    
    # Create notification for selected candidate
    notification = Notification(
        user_id=application.candidate_id,
        title=f"Job Offer - {job.title}",
        message=message,
        notification_type="job_offer"
    )
    db.add(notification)
    
    # Create notification for HR
    hr_notification = Notification(
        user_id=current_user.id,
        title=f"Candidate Selected - {application.name}",
        message=f"""You have successfully selected: {application.name} for {job.title}

Selection Details:
👤 Candidate: {application.name}
💼 Position: {job.title}
⏰ Willingness Deadline: {willingness_deadline.strftime('%Y-%m-%d %H:%M')}
{f'💰 Salary Offered: {salary_offered}' if salary_offered else ''}
{f'📅 Start Date: {start_date}' if start_date else ''}

Please follow up to ensure timely confirmation.""",
        notification_type="candidate_selected"
    )
    db.add(hr_notification)
    
    db.commit()
    
    return {"message": "Candidate selected successfully", "willingness_deadline": willingness_deadline.isoformat()}

@app.post("/api/applications/{application_id}/confirm-willingness")
async def confirm_willingness(
    application_id: int,
    willingness_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only confirm your own applications")
    
    if application.status != "selected":
        raise HTTPException(status_code=400, detail="Application is not in selected status")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    confirmed = willingness_data.get("confirmed", False)
    response_notes = willingness_data.get("notes", "")
    
    application.willingness_confirmed = confirmed
    application.willingness_response_date = datetime.now()
    
    if confirmed:
        application.status = "hired"
        application.hired_date = datetime.now()
        
        # Reduce job vacancy count
        if job.number_of_vacancies > 0:
            job.number_of_vacancies -= 1
        
        # Create congratulations notification
        notification = Notification(
            user_id=current_user.id,
            title="Welcome to the Team!",
            message=f"""🎉 Thank you for accepting our offer for: {job.title}

What's Next:
✅ Your acceptance has been confirmed
📋 HR will contact you with onboarding details
📧 Please watch for further communications
🎯 We're excited to have you join our team!

{f'Your Response: {response_notes}' if response_notes else ''}

Welcome aboard!""",
            notification_type="offer_accepted"
        )
        db.add(notification)
        
        # Notify HR of acceptance
        hr_users = db.query(User).filter(User.user_type == "hr").all()
        for hr_user in hr_users:
            hr_notification = Notification(
                user_id=hr_user.id,
                title=f"Offer Accepted - {application.name}",
                message=f"""✅ Great news! {application.name} has accepted the offer for: {job.title}

Details:
👤 New Hire: {application.name}
💼 Position: {job.title}
📅 Acceptance Date: {datetime.now().strftime('%Y-%m-%d')}
🏢 Remaining Vacancies: {job.number_of_vacancies}
{f'💬 Candidate Notes: {response_notes}' if response_notes else ''}

Please proceed with onboarding process.""",
                notification_type="offer_accepted"
            )
            db.add(hr_notification)
    
    else:
        application.status = "offer_declined"
        
        # Create declined notification
        notification = Notification(
            user_id=current_user.id,
            title="Offer Response Confirmed",
            message=f"""Thank you for your response regarding the position: {job.title}

We understand that you have decided not to accept our offer at this time.

{f'Your Feedback: {response_notes}' if response_notes else ''}

We appreciate the time you invested in our interview process and wish you the best in your career endeavors. Please feel free to apply for future opportunities that may be a better fit.""",
            notification_type="offer_declined"
        )
        db.add(notification)
        
        # Notify HR of decline
        hr_users = db.query(User).filter(User.user_type == "hr").all()
        for hr_user in hr_users:
            hr_notification = Notification(
                user_id=hr_user.id,
                title=f"Offer Declined - {application.name}",
                message=f"""❌ {application.name} has declined the offer for: {job.title}

Details:
👤 Candidate: {application.name}
💼 Position: {job.title}
📅 Response Date: {datetime.now().strftime('%Y-%m-%d')}
{f'💬 Candidate Feedback: {response_notes}' if response_notes else ''}

Please consider other candidates or repost the position.""",
                notification_type="offer_declined"
            )
            db.add(hr_notification)
    
    db.commit()
    
    return {"message": f"Willingness {'confirmed' if confirmed else 'declined'} successfully"}

@app.put("/api/jobs/{job_id}/close")
async def close_job(
    job_id: int,
    close_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can close jobs")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    close_reason = close_data.get("reason", "Position filled")
    
    # Update job status
    job.is_closed = True
    job.closed_date = datetime.now()
    job.close_reason = close_reason
    
    # Get pending applications
    pending_applications = db.query(Application).filter(
        Application.job_id == job_id,
        Application.status.in_(["applied", "interview_scheduled", "technical_passed"])
    ).all()
    
    # Notify pending candidates
    for application in pending_applications:
        if application.status not in ["hired", "rejected", "offer_declined"]:
            application.status = "position_closed"
            
            notification = Notification(
                user_id=application.candidate_id,
                title=f"Position Update - {job.title}",
                message=f"""Thank you for your interest in the position: {job.title}

Update:
📝 This position has been closed
🏢 Reason: {close_reason}
🙏 We appreciate your time and interest

We encourage you to explore other opportunities on our careers page. Thank you for considering us as a potential employer.""",
                notification_type="position_closed"
            )
            db.add(notification)
    
    # Create notification for HR
    hr_notification = Notification(
        user_id=current_user.id,
        title=f"Job Closed - {job.title}",
        message=f"""✅ Successfully closed position: {job.title}

Closure Details:
📅 Closed Date: {datetime.now().strftime('%Y-%m-%d')}
📝 Reason: {close_reason}
👥 Pending Applications Notified: {len(pending_applications)}

All pending candidates have been notified of the position closure.""",
        notification_type="job_closed"
    )
    db.add(hr_notification)
    
    db.commit()
    
@app.get("/api/interviews/conflicts")
async def check_interview_conflicts(
    interview_date: str,
    interview_time: str,
    duration_minutes: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can check interview conflicts")
    
    # Create interview datetime
    interview_datetime_str = f"{interview_date} {interview_time}"
    try:
        interview_datetime = datetime.strptime(interview_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    # Check for conflicts
    conflict = check_interview_conflict(db, interview_datetime, duration_minutes, current_user.id)
    
    if conflict:
        conflict_app = db.query(Application).filter(Application.id == conflict.application_id).first()
        conflict_end_time = conflict.interview_date + timedelta(minutes=conflict.duration_minutes)
        return {
            "has_conflict": True,
            "conflict_details": {
                "candidate_name": conflict_app.name,
                "interview_start": conflict.interview_date.strftime('%Y-%m-%d %H:%M'),
                "interview_end": conflict_end_time.strftime('%Y-%m-%d %H:%M'),
                "interview_type": conflict.interview_type,
                "duration_minutes": conflict.duration_minutes
            }
        }
    
    return {"has_conflict": False}

@app.get("/api/interviews/my-schedule")
async def get_my_interview_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can view interview schedules")
    
    # Get upcoming interviews for this HR user
    current_time = datetime.now()
    interviews = db.query(Interview).filter(
        Interview.created_by == current_user.id,
        Interview.interview_date >= current_time
    ).order_by(Interview.interview_date).all()
    
    schedule = []
    for interview in interviews:
        application = db.query(Application).filter(Application.id == interview.application_id).first()
        job = db.query(Job).filter(Job.id == application.job_id).first()
        
        schedule.append({
            "interview_id": interview.id,
            "candidate_name": application.name,
            "job_title": job.title,
            "interview_type": interview.interview_type,
            "interview_date": interview.interview_date.strftime('%Y-%m-%d'),
            "interview_time": interview.interview_time,
            "duration_minutes": interview.duration_minutes,
            "platform": interview.platform,
            "meeting_link": interview.meeting_link,
            "status": interview.result if interview.result else "scheduled"
        })
    
    return {"schedule": schedule}

    return {"message": "Job closed successfully", "applications_affected": len(pending_applications)}

@app.get("/api/applications/{application_id}/questions/pdf")
def download_questions_pdf(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "hr":
        raise HTTPException(status_code=403, detail="Only HR can download questions")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    questions = generate_interview_questions(job, application)
    
    # Generate PDF with proper formatting
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Build PDF content
    story = []
    
    # Title
    title = Paragraph(f"Interview Questions", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Job and candidate info
    job_info = Paragraph(f"<b>Position:</b> {job.title}", heading_style)
    story.append(job_info)
    story.append(Spacer(1, 0.1*inch))
    
    candidate_info = Paragraph(f"<b>Candidate:</b> {application.name}", heading_style)
    story.append(candidate_info)
    story.append(Spacer(1, 0.3*inch))
    
    # Process questions to remove double numbering
    processed_questions = []
    for question in questions:
        question = question.strip()
        if question:
            # Remove leading numbers and dots if present (e.g., "1. " or "1.")
            # Pattern to match number followed by dot and optional space at the beginning
            clean_question = re.sub(r'^\d+\.\s*', '', question)
            processed_questions.append(clean_question)
    
    # Add questions with proper formatting
    for i, question in enumerate(processed_questions, 1):
        if question.strip():  # Only add non-empty questions
            # Question number and text
            question_text = f"<b>{i}.</b> {question}"
            question_para = Paragraph(question_text, normal_style)
            story.append(question_para)
            story.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(story)
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
        "phone": current_user.phone,
        "address": current_user.address,
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

# Application routes for candidates
@app.get("/api/my-applications")
def get_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all applications submitted by the current user"""
    if current_user.user_type != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access this endpoint")
    
    applications = db.query(Application).filter(Application.candidate_id == current_user.id).all()
    
    # Include job details in the response
    result = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        app_dict = {
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job.title if job else "Unknown Job",
            "job_location": job.work_location if job else "Unknown Location",
            "name": app.name,
            "email": app.email,
            "phone": app.phone,
            "address": app.address,
            "experience_years": app.experience_years,
            "relevant_experience": app.relevant_experience,
            "skills": app.skills,
            "education": app.education,
            "projects": app.projects,
            "preferred_location": app.preferred_location,
            "ai_score": app.ai_score,
            "status": app.status,
            "applied_at": app.created_at,
            "photo_path": app.photo_path
        }
        result.append(app_dict)
    
    return result

# AI Helper functions
def check_interview_conflict(db: Session, interview_datetime: datetime, duration_minutes: int, hr_user_id: int):
    """Check if HR already has an interview scheduled at the same time"""
    from datetime import timedelta
    
    # Calculate the time range for the new interview
    start_time = interview_datetime
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Find all interviews created by this HR user
    existing_interviews = db.query(Interview).filter(
        Interview.created_by == hr_user_id
    ).all()
    
    for interview in existing_interviews:
        existing_start = interview.interview_date
        existing_end = existing_start + timedelta(minutes=interview.duration_minutes)
        
        # Check for overlap
        if (start_time < existing_end) and (end_time > existing_start):
            return interview  # Conflict found
    
    return None  # No conflict

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
        
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
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
        Generate 15 comprehensive interview questions for the following job and candidate:
        
        Job: {job.title}
        Job Description: {job.description}
        Required Skills: {job.skills}
        Experience Required: {job.experience_years} years
        Work Location: {job.work_location}
        
        Candidate Profile:
        - Name: {application.name}
        - Skills: {application.skills}
        - Experience: {application.experience_years} years
        - Education: {application.education}
        - Projects: {application.projects}
        - Relevant Experience: {application.relevant_experience}
        
        Generate 15 relevant interview questions that include:
        - 5 technical questions specific to the required skills
        - 5 behavioral/situational questions
        - 3 questions about experience and projects
        - 2 questions about cultural fit and motivation
        
        Format each question with a number (1-15) and return each question on a new line.
        Make sure questions are specific to the job requirements and candidate background.
        """
        
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        questions = response.choices[0].message.content.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fallback questions (15 questions)
        return [
            "1. Tell me about yourself and your relevant experience for this position.",
            "2. Why are you interested in this specific role and our company?",
            "3. Walk me through your experience with the key technologies mentioned in the job description.",
            "4. Describe a challenging technical problem you solved recently.",
            "5. How do you approach learning new technologies or skills?",
            "6. Tell me about a time when you had to work under tight deadlines.",
            "7. Describe a situation where you had to collaborate with a difficult team member.",
            "8. How do you handle feedback and criticism?",
            "9. What's your approach to debugging and troubleshooting?",
            "10. Tell me about a project you're particularly proud of.",
            "11. How do you prioritize tasks when you have multiple deadlines?",
            "12. What motivates you in your work?",
            "13. How do you stay updated with industry trends and best practices?",
            "14. Where do you see yourself in the next 3-5 years?",
            "15. Do you have any questions about the role or our company?"
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
