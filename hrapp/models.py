from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('hr', 'HR'),
        ('candidate', 'Candidate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)])
    relevant_experience = models.TextField()
    key_skills = models.TextField()
    work_location = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    total_experience = models.IntegerField(validators=[MinValueValidator(0)])
    primary_skills = models.TextField()
    educational_background = models.TextField()
    institution = models.CharField(max_length=200)
    year_of_passing = models.IntegerField()
    preferred_location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class WorkExperience(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='work_experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.candidate.user.username} - {self.company}"
    
    class Meta:
        ordering = ['-from_date']


class Project(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.TextField()
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.candidate.user.username} - {self.title}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
    ]
    
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    relevant_experience = models.TextField()
    cover_letter = models.TextField(blank=True)
    ai_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"
    
    class Meta:
        unique_together = ['job', 'candidate']
        ordering = ['-applied_at']


class InterviewQuestions(models.Model):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE)
    questions = models.TextField()  # JSON field for storing questions
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Questions for {self.application.candidate.user.username} - {self.application.job.title}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('shortlist', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejection', 'Application Rejected'),
        ('selection', 'Selected'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    interview_date = models.DateTimeField(null=True, blank=True)
    webex_link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']
