from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JobPosting, CandidateProfile, WorkExperience, Project, JobApplication, UserProfile


class HRRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='hr',
                phone=self.cleaned_data['phone']
            )
        return user


class CandidateRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, role='candidate')
        return user


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'years_of_experience', 'relevant_experience', 'key_skills', 'work_location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'relevant_experience': forms.Textarea(attrs={'rows': 4}),
            'key_skills': forms.Textarea(attrs={'rows': 3}),
        }


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['phone', 'total_experience', 'primary_skills', 'educational_background', 
                 'institution', 'year_of_passing', 'preferred_location']
        widgets = {
            'primary_skills': forms.Textarea(attrs={'rows': 3}),
            'educational_background': forms.Textarea(attrs={'rows': 3}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'from_date', 'to_date', 'is_current', 'description']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_date'].required = False


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'from_date', 'to_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'technologies': forms.Textarea(attrs={'rows': 2}),
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_date'].required = False


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['relevant_experience', 'cover_letter']
        widgets = {
            'relevant_experience': forms.Textarea(attrs={'rows': 4}),
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
