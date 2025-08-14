from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    user_type: str

class UserCreate(UserBase):
    password: str
    admin_code: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Job schemas
class JobBase(BaseModel):
    title: str
    description: str
    experience_years: int
    relevant_experience: Optional[str] = None
    skills: str
    work_location: str
    salary_range: Optional[str] = None
    employment_type: str
    number_of_vacancies: Optional[int] = 1
    application_deadline: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    experience_years: Optional[int] = None
    relevant_experience: Optional[str] = None
    skills: Optional[str] = None
    work_location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    is_active: Optional[bool] = None
    number_of_vacancies: Optional[int] = None
    application_deadline: Optional[datetime] = None
    is_closed: Optional[bool] = None

class JobResponse(JobBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Application schemas
class ApplicationBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    experience_years: int
    relevant_experience: str
    skills: str
    education: str
    projects: str
    preferred_location: str

class ApplicationCreate(ApplicationBase):
    job_id: int

class ApplicationResponse(ApplicationBase):
    id: int
    job_id: int
    candidate_id: int
    photo_path: Optional[str] = None
    ai_score: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str

class NotificationCreate(NotificationBase):
    user_id: int
    interview_date: Optional[datetime] = None
    interview_time: Optional[str] = None
    webex_link: Optional[str] = None
    meeting_password: Optional[str] = None
    interview_duration: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    interview_date: Optional[datetime] = None
    interview_time: Optional[str] = None
    webex_link: Optional[str] = None
    meeting_password: Optional[str] = None
    interview_duration: Optional[int] = None
    
    class Config:
        from_attributes = True

# Interview scheduling schemas
class InterviewSchedule(BaseModel):
    interview_date: str
    interview_time: str
    duration_minutes: Optional[int] = 60
    timezone: str
    platform: str
    meeting_link: str
    meeting_password: Optional[str] = None
    notes: Optional[str] = None
    interview_type: Optional[str] = "technical"  # 'technical' or 'hr'

class InterviewResponse(BaseModel):
    id: int
    application_id: int
    interview_type: str
    interview_date: datetime
    interview_time: str
    duration_minutes: int
    timezone: str
    platform: str
    meeting_link: str
    meeting_password: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
