from django.contrib import admin
from .models import (
    UserProfile, JobPosting, CandidateProfile, WorkExperience, 
    Project, JobApplication, InterviewQuestions, Notification
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'work_location', 'created_at']
    list_filter = ['status', 'work_location', 'created_at']
    search_fields = ['title', 'description']

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'total_experience', 'preferred_location']
    search_fields = ['user__username', 'user__email']

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'company', 'position', 'from_date', 'to_date']
    list_filter = ['company', 'is_current']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'title', 'from_date', 'to_date']
    search_fields = ['title', 'technologies']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'ai_score', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['candidate__user__username', 'job__title']

@admin.register(InterviewQuestions)
class InterviewQuestionsAdmin(admin.ModelAdmin):
    list_display = ['application', 'generated_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
