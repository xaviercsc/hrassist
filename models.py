from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    user_type = Column(String(20), nullable=False)  # 'hr' or 'candidate'
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    created_jobs = relationship("Job", back_populates="creator")
    applications = relationship("Application", back_populates="candidate")
    notifications = relationship("Notification", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    experience_years = Column(Integer, nullable=False)
    relevant_experience = Column(Text)
    skills = Column(Text, nullable=False)
    work_location = Column(String(100), nullable=False)
    salary_range = Column(String(100))
    employment_type = Column(String(50), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New fields for enhanced job management
    number_of_vacancies = Column(Integer, default=1)
    application_deadline = Column(DateTime)
    is_closed = Column(Boolean, default=False)
    closed_date = Column(DateTime)
    close_reason = Column(String(200))
    
    # Relationships
    creator = relationship("User", back_populates="created_jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Application data
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    experience_years = Column(Integer, nullable=False)
    relevant_experience = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)
    education = Column(Text, nullable=False)
    projects = Column(Text, nullable=False)
    preferred_location = Column(String(100), nullable=False)
    photo_path = Column(String(255))
    
    # AI scoring and status
    ai_score = Column(Float, default=0.0)
    status = Column(String(30), default="applied")  # applied, shortlisted, interview_scheduled, hr_round, rejected, selected, willingness_pending, hired
    
    # Interview tracking
    technical_interview_date = Column(DateTime)
    hr_interview_date = Column(DateTime)
    willingness_deadline = Column(DateTime)
    willingness_confirmed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    interview_type = Column(String(20), nullable=False)  # 'technical' or 'hr'
    interview_date = Column(DateTime, nullable=False)
    interview_time = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), nullable=False)
    platform = Column(String(30), nullable=False)
    meeting_link = Column(String(500), nullable=False)
    meeting_password = Column(String(100))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    creator = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # shortlist, interview, rejection, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional fields for interview notifications
    interview_date = Column(DateTime)
    interview_time = Column(String(20))
    webex_link = Column(String(500))
    meeting_password = Column(String(100))
    interview_duration = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
