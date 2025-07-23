from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='hrapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/hr/', views.hr_register, name='hr_register'),
    path('register/candidate/', views.candidate_register, name='candidate_register'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # HR URLs
    path('hr/jobs/', views.hr_job_list, name='hr_job_list'),
    path('hr/jobs/create/', views.hr_job_create, name='hr_job_create'),
    path('hr/jobs/<int:job_id>/edit/', views.hr_job_edit, name='hr_job_edit'),
    path('hr/jobs/<int:job_id>/withdraw/', views.hr_job_withdraw, name='hr_job_withdraw'),
    path('hr/jobs/<int:job_id>/applications/', views.hr_job_applications, name='hr_job_applications'),
    path('hr/applications/<int:app_id>/score/', views.calculate_score, name='calculate_score'),
    path('hr/applications/<int:app_id>/shortlist/', views.shortlist_candidate, name='shortlist_candidate'),
    path('hr/applications/<int:app_id>/questions/', views.generate_questions, name='generate_questions'),
    path('hr/applications/<int:app_id>/questions/pdf/', views.download_questions_pdf, name='download_questions_pdf'),
    path('hr/applications/<int:app_id>/notify/', views.notify_candidate, name='notify_candidate'),
    
    # Candidate URLs
    path('candidate/jobs/', views.candidate_job_list, name='candidate_job_list'),
    path('candidate/jobs/<int:job_id>/', views.candidate_job_detail, name='candidate_job_detail'),
    path('candidate/jobs/<int:job_id>/apply/', views.candidate_job_apply, name='candidate_job_apply'),
    path('candidate/applications/', views.candidate_applications, name='candidate_applications'),
    path('candidate/profile/', views.candidate_profile, name='candidate_profile'),
    path('candidate/profile/edit/', views.candidate_profile_edit, name='candidate_profile_edit'),
    path('candidate/experience/add/', views.add_work_experience, name='add_work_experience'),
    path('candidate/experience/<int:exp_id>/edit/', views.edit_work_experience, name='edit_work_experience'),
    path('candidate/experience/<int:exp_id>/delete/', views.delete_work_experience, name='delete_work_experience'),
    path('candidate/project/add/', views.add_project, name='add_project'),
    path('candidate/project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('candidate/project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('candidate/notifications/', views.candidate_notifications, name='candidate_notifications'),
    path('candidate/notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('candidate/settings/', views.candidate_settings, name='candidate_settings'),
]
