from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import (
    UserProfile, JobPosting, CandidateProfile, WorkExperience, 
    Project, JobApplication, InterviewQuestions, Notification
)
from .forms import (
    HRRegistrationForm, CandidateRegistrationForm, JobPostingForm,
    CandidateProfileForm, WorkExperienceForm, ProjectForm, 
    JobApplicationForm, UserUpdateForm, UserProfileUpdateForm
)
from .ai_services import AIService
from .utils import PDFGenerator


def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get some statistics for the home page
    context = {
        'total_jobs': JobPosting.objects.filter(status='active').count(),
        'total_applications': JobApplication.objects.count(),
    }
    return render(request, 'hrapp/home.html', context)


def hr_register(request):
    """HR registration view"""
    if request.method == 'POST':
        form = HRRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'HR account created successfully!')
            return redirect('dashboard')
    else:
        form = HRRegistrationForm()
    return render(request, 'hrapp/register_hr.html', {'form': form})


def candidate_register(request):
    """Candidate registration view"""
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Candidate account created successfully! Please complete your profile.')
            return redirect('candidate_profile_edit')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'hrapp/register_candidate.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard view for both HR and candidates"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.role == 'hr':
            # HR Dashboard
            context = {
                'role': 'hr',
                'total_jobs': JobPosting.objects.filter(created_by=request.user).count(),
                'active_jobs': JobPosting.objects.filter(created_by=request.user, status='active').count(),
                'total_applications': JobApplication.objects.filter(job__created_by=request.user).count(),
                'pending_applications': JobApplication.objects.filter(
                    job__created_by=request.user, 
                    status='submitted'
                ).count(),
                'recent_jobs': JobPosting.objects.filter(created_by=request.user).order_by('-created_at')[:5],
                'recent_applications': JobApplication.objects.filter(
                    job__created_by=request.user
                ).order_by('-applied_at')[:5]
            }
        else:
            # Candidate Dashboard
            try:
                candidate_profile = CandidateProfile.objects.get(user=request.user)
                profile_exists = True
            except CandidateProfile.DoesNotExist:
                candidate_profile = None
                profile_exists = False
            
            context = {
                'role': 'candidate',
                'profile_exists': profile_exists,
                'total_jobs': JobPosting.objects.filter(status='active').count(),
                'applied_jobs': JobApplication.objects.filter(candidate=candidate_profile).count() if candidate_profile else 0,
                'unread_notifications': Notification.objects.filter(recipient=request.user, is_read=False).count(),
                'recent_jobs': JobPosting.objects.filter(status='active').order_by('-created_at')[:5],
                'recent_applications': JobApplication.objects.filter(
                    candidate=candidate_profile
                ).order_by('-applied_at')[:5] if candidate_profile else []
            }
        
        return render(request, 'hrapp/dashboard.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please contact administrator.')
        return redirect('home')


# HR Views
@login_required
def hr_job_list(request):
    """List all jobs created by HR user"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'hr':
        messages.error(request, 'Access denied. HR access required.')
        return redirect('dashboard')
    
    jobs = JobPosting.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Add application count to each job
    for job in jobs:
        job.application_count = JobApplication.objects.filter(job=job).count()
    
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'hrapp/hr_job_list.html', {'page_obj': page_obj})


@login_required
def hr_job_create(request):
    """Create a new job posting"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'hr':
        messages.error(request, 'Access denied. HR access required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, 'Job posting created successfully!')
            return redirect('hr_job_list')
    else:
        form = JobPostingForm()
    
    return render(request, 'hrapp/hr_job_form.html', {'form': form, 'title': 'Create Job Posting'})


@login_required
def hr_job_edit(request, job_id):
    """Edit an existing job posting"""
    job = get_object_or_404(JobPosting, id=job_id, created_by=request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated successfully!')
            return redirect('hr_job_list')
    else:
        form = JobPostingForm(instance=job)
    
    return render(request, 'hrapp/hr_job_form.html', {
        'form': form, 
        'title': 'Edit Job Posting',
        'job': job
    })


@login_required
def hr_job_withdraw(request, job_id):
    """Withdraw a job posting"""
    job = get_object_or_404(JobPosting, id=job_id, created_by=request.user)
    
    if request.method == 'POST':
        job.status = 'withdrawn'
        job.save()
        messages.success(request, 'Job posting withdrawn successfully!')
        return redirect('hr_job_list')
    
    return render(request, 'hrapp/confirm_withdraw.html', {'job': job})


@login_required
def hr_job_applications(request, job_id):
    """View all applications for a specific job"""
    job = get_object_or_404(JobPosting, id=job_id, created_by=request.user)
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
    
    return render(request, 'hrapp/hr_job_applications.html', {
        'job': job,
        'applications': applications
    })


@login_required
def calculate_score(request, app_id):
    """Calculate AI score for a job application"""
    application = get_object_or_404(JobApplication, id=app_id, job__created_by=request.user)
    
    if request.method == 'POST':
        try:
            score = AIService.calculate_candidate_score(application)
            application.status = 'under_review'
            application.save()
            messages.success(request, f'AI score calculated: {score}/10')
            return JsonResponse({'success': True, 'score': score})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def shortlist_candidate(request, app_id):
    """Shortlist a candidate"""
    application = get_object_or_404(JobApplication, id=app_id, job__created_by=request.user)
    
    if request.method == 'POST':
        if application.ai_score and application.ai_score >= 5:
            application.status = 'shortlisted'
            application.save()
            
            # Create notification for candidate
            Notification.objects.create(
                recipient=application.candidate.user,
                notification_type='shortlist',
                title=f'Shortlisted for {application.job.title}',
                message=f'Congratulations! You have been shortlisted for the position of {application.job.title}. We will contact you soon with interview details.'
            )
            
            messages.success(request, 'Candidate shortlisted successfully!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Candidate score must be 5 or above to shortlist'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def generate_questions(request, app_id):
    """Generate interview questions for a shortlisted candidate"""
    application = get_object_or_404(JobApplication, id=app_id, job__created_by=request.user)
    
    if request.method == 'POST':
        try:
            # Check if questions already exist
            interview_questions, created = InterviewQuestions.objects.get_or_create(
                application=application,
                defaults={'questions': ''}
            )
            
            if created or not interview_questions.questions:
                questions = AIService.generate_interview_questions(application)
                interview_questions.questions = questions
                interview_questions.save()
            
            return JsonResponse({
                'success': True, 
                'questions': interview_questions.questions,
                'generated_at': interview_questions.generated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def download_questions_pdf(request, app_id):
    """Download interview questions as PDF"""
    application = get_object_or_404(JobApplication, id=app_id, job__created_by=request.user)
    
    try:
        interview_questions = InterviewQuestions.objects.get(application=application)
        
        # Generate PDF
        buffer = PDFGenerator.generate_interview_questions_pdf(application, interview_questions.questions)
        filename = f"interview_questions_{application.candidate.user.username}_{application.job.title.replace(' ', '_')}.pdf"
        
        return PDFGenerator.create_pdf_response(buffer, filename)
        
    except InterviewQuestions.DoesNotExist:
        messages.error(request, 'Interview questions not generated yet.')
        return redirect('hr_job_applications', job_id=application.job.id)


@login_required
def notify_candidate(request, app_id):
    """Send interview notification to candidate"""
    application = get_object_or_404(JobApplication, id=app_id, job__created_by=request.user)
    
    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_time = request.POST.get('interview_time')
        webex_link = request.POST.get('webex_link')
        
        if interview_date and interview_time:
            try:
                # Combine date and time
                interview_datetime = datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
                
                # Create notification
                Notification.objects.create(
                    recipient=application.candidate.user,
                    notification_type='interview',
                    title=f'Interview Scheduled for {application.job.title}',
                    message=f'Your interview has been scheduled for {interview_datetime.strftime("%B %d, %Y at %I:%M %p")}. Please join using the provided link.',
                    interview_date=interview_datetime,
                    webex_link=webex_link
                )
                
                messages.success(request, 'Interview notification sent to candidate!')
                return JsonResponse({'success': True})
                
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date/time format'})
        else:
            return JsonResponse({'success': False, 'error': 'Date and time are required'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Candidate Views
@login_required
def candidate_job_list(request):
    """List all active job postings for candidates"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    jobs = JobPosting.objects.filter(status='active').order_by('-created_at')
    
    # Add application status for each job
    applied_jobs = set(JobApplication.objects.filter(candidate=candidate_profile).values_list('job_id', flat=True))
    
    for job in jobs:
        job.has_applied = job.id in applied_jobs
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(key_skills__icontains=search_query) |
            Q(work_location__icontains=search_query)
        )
    
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'hrapp/candidate_job_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@login_required
def candidate_job_detail(request, job_id):
    """View detailed job information"""
    job = get_object_or_404(JobPosting, id=job_id, status='active')
    
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        has_applied = JobApplication.objects.filter(job=job, candidate=candidate_profile).exists()
    except CandidateProfile.DoesNotExist:
        candidate_profile = None
        has_applied = False
    
    return render(request, 'hrapp/candidate_job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'candidate_profile': candidate_profile
    })


@login_required
def candidate_job_apply(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(JobPosting, id=job_id, status='active')
    
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, candidate=candidate_profile).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('candidate_job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = candidate_profile
            application.save()
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('candidate_applications')
    else:
        form = JobApplicationForm()
    
    return render(request, 'hrapp/candidate_job_apply.html', {
        'form': form,
        'job': job,
        'candidate': candidate_profile
    })


@login_required
def candidate_applications(request):
    """View all applications submitted by candidate"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    applications = JobApplication.objects.filter(candidate=candidate_profile).order_by('-applied_at')
    
    return render(request, 'hrapp/candidate_applications.html', {
        'applications': applications
    })


@login_required
def candidate_profile(request):
    """View candidate profile"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        work_experiences = WorkExperience.objects.filter(candidate=candidate_profile)
        projects = Project.objects.filter(candidate=candidate_profile)
        
        return render(request, 'hrapp/candidate_profile.html', {
            'candidate': candidate_profile,
            'work_experiences': work_experiences,
            'projects': projects
        })
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')


@login_required
def candidate_profile_edit(request):
    """Edit candidate profile"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        is_new = False
    except CandidateProfile.DoesNotExist:
        candidate_profile = None
        is_new = True
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, instance=candidate_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            if is_new:
                messages.success(request, 'Profile created successfully!')
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('candidate_profile')
    else:
        form = CandidateProfileForm(instance=candidate_profile)
    
    return render(request, 'hrapp/candidate_profile_edit.html', {
        'form': form,
        'is_new': is_new
    })


@login_required
def add_work_experience(request):
    """Add work experience"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.candidate = candidate_profile
            experience.save()
            messages.success(request, 'Work experience added successfully!')
            return redirect('candidate_profile')
    else:
        form = WorkExperienceForm()
    
    return render(request, 'hrapp/work_experience_form.html', {
        'form': form,
        'title': 'Add Work Experience'
    })


@login_required
def edit_work_experience(request, exp_id):
    """Edit work experience"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        experience = get_object_or_404(WorkExperience, id=exp_id, candidate=candidate_profile)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('candidate_profile')
    else:
        form = WorkExperienceForm(instance=experience)
    
    return render(request, 'hrapp/work_experience_form.html', {
        'form': form,
        'title': 'Edit Work Experience',
        'experience': experience
    })


@login_required
def delete_work_experience(request, exp_id):
    """Delete work experience"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        experience = get_object_or_404(WorkExperience, id=exp_id, candidate=candidate_profile)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Work experience deleted successfully!')
        return redirect('candidate_profile')
    
    return render(request, 'hrapp/confirm_delete.html', {
        'object': experience,
        'object_type': 'work experience'
    })


@login_required
def add_project(request):
    """Add project"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.candidate = candidate_profile
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('candidate_profile')
    else:
        form = ProjectForm()
    
    return render(request, 'hrapp/project_form.html', {
        'form': form,
        'title': 'Add Project'
    })


@login_required
def edit_project(request, project_id):
    """Edit project"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        project = get_object_or_404(Project, id=project_id, candidate=candidate_profile)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('candidate_profile')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'hrapp/project_form.html', {
        'form': form,
        'title': 'Edit Project',
        'project': project
    })


@login_required
def delete_project(request, project_id):
    """Delete project"""
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        project = get_object_or_404(Project, id=project_id, candidate=candidate_profile)
    except CandidateProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_profile_edit')
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('candidate_profile')
    
    return render(request, 'hrapp/confirm_delete.html', {
        'object': project,
        'object_type': 'project'
    })


@login_required
def candidate_notifications(request):
    """View notifications for candidate"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Mark all notifications as read when viewing
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'hrapp/candidate_notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_read(request, notif_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
def candidate_settings(request):
    """Candidate settings - update contact info"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('candidate_settings')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=user_profile)
    
    return render(request, 'hrapp/candidate_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
