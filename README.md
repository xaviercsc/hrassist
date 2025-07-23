# HR Assist AI Web Application

A comprehensive Django-based HR management system with AI-powered candidate matching and interview question generation.

## Features

### 🎯 For HR Professionals
- **Job Management**: Create, edit, and manage job postings with detailed requirements
- **AI-Powered Matching**: Automatic candidate scoring (1-10) based on skills and experience
- **Smart Shortlisting**: Shortlist candidates with AI scores above 5
- **Interview Questions**: Auto-generate tailored interview questions using AI
- **PDF Export**: Download interview questions in professional PDF format
- **Candidate Notifications**: Send interview schedules with WebEx meeting links
- **Application Tracking**: Monitor all applications and their status

### 👤 For Candidates
- **Job Discovery**: Browse and search available job openings
- **Complete Profiles**: Add work experience, projects, and skills
- **Easy Applications**: Apply for jobs with detailed application forms
- **Status Tracking**: Monitor application progress in real-time
- **Smart Notifications**: Receive interview invitations and updates
- **Profile Management**: Update contact information and preferences

### 🤖 AI Features
- **Intelligent Matching**: Advanced algorithm considers skills, experience, and job requirements
- **Dynamic Scoring**: Real-time candidate evaluation with detailed breakdowns
- **Question Generation**: Context-aware interview questions based on job and candidate profile
- **Fallback Systems**: Robust algorithms work even without external AI APIs

## Tech Stack

### Backend
- **Django 4.2** - Python web framework
- **SQLite** - Database for development (easily switchable to PostgreSQL for production)
- **OpenAI API** - AI-powered features (with fallback algorithms)
- **ReportLab** - PDF generation
- **Django Crispy Forms** - Enhanced form rendering

### Frontend
- **HTML5 & CSS3** - Semantic markup and modern styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript & jQuery** - Interactive features and AJAX
- **Font Awesome** - Professional icons

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd HRASSISTAPP
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   # Copy the example file
   copy .env .env.local  # Windows
   cp .env .env.local    # macOS/Linux
   
   # Edit .env.local with your API keys (optional)
   # OPENAI_API_KEY=your-openai-key-here
   # ANTHROPIC_API_KEY=your-anthropic-key-here
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin` (if superuser created)

## Usage Guide

### For HR Users

1. **Register as HR**
   - Go to the homepage and click "Register as HR"
   - Fill in your details and create an account

2. **Create Job Postings**
   - Navigate to Dashboard → Jobs → Create Job
   - Add job title, description, required skills, experience, and location
   - Job will be automatically published and visible to candidates

3. **Manage Applications**
   - View applications for each job posting
   - Click "Calculate AI Score" to get candidate matching scores
   - Shortlist candidates with scores ≥ 5
   - Generate and download interview questions
   - Schedule interviews and send notifications

### For Candidates

1. **Register as Candidate**
   - Click "Register as Candidate" on the homepage
   - Create your account

2. **Complete Your Profile**
   - Add personal information, skills, and education
   - Add work experiences and projects
   - Keep your profile updated for better matching

3. **Find and Apply for Jobs**
   - Browse available job openings
   - View detailed job descriptions
   - Submit applications with relevant experience details
   - Track your application status

4. **Manage Notifications**
   - Check your inbox for interview invitations
   - Update your contact information as needed

## API Keys Setup (Optional)

The application works with built-in algorithms, but you can enhance AI features by adding API keys:

1. **OpenAI API** (for advanced AI features)
   - Sign up at https://platform.openai.com/
   - Get your API key
   - Add to `.env`: `OPENAI_API_KEY=your-key-here`

2. **Anthropic API** (alternative AI provider)
   - Sign up at https://console.anthropic.com/
   - Get your API key
   - Add to `.env`: `ANTHROPIC_API_KEY=your-key-here`

**Note**: The application includes robust fallback algorithms that work without any external APIs.

## Project Structure

```
HRASSISTAPP/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── db.sqlite3            # SQLite database (created after migration)
├── hrassist/             # Django project settings
│   ├── __init__.py
│   ├── settings.py       # Main configuration
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── hrapp/               # Main Django application
│   ├── __init__.py
│   ├── admin.py         # Admin interface configuration
│   ├── apps.py          # App configuration
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URL patterns
│   ├── forms.py         # Django forms
│   ├── ai_services.py   # AI integration services
│   └── utils.py         # Utility functions (PDF generation)
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   └── hrapp/           # App-specific templates
└── static/             # Static files (CSS, JS, images)
```

## Database Models

- **UserProfile**: Extends Django User with role (HR/Candidate)
- **JobPosting**: Job openings with requirements and status
- **CandidateProfile**: Detailed candidate information
- **WorkExperience**: Candidate work history
- **Project**: Candidate project portfolio
- **JobApplication**: Applications linking candidates to jobs
- **InterviewQuestions**: AI-generated questions for interviews
- **Notification**: System notifications for candidates

## Customization

### Adding New AI Providers
Edit `hrapp/ai_services.py` to add support for new AI APIs.

### Styling Changes
- Modify `templates/base.html` for global styles
- Update individual templates in `templates/hrapp/`
- Add custom CSS in the `static/` directory

### Email Notifications
Configure Django's email settings in `hrassist/settings.py` to enable email notifications.

## Deployment

### For Production

1. **Environment Setup**
   ```bash
   # Set production environment variables
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=your-domain.com
   ```

2. **Database Migration**
   - For PostgreSQL: Update `DATABASES` in settings.py
   - Run migrations: `python manage.py migrate`

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Web Server**
   - Use Gunicorn, uWSGI, or similar WSGI server
   - Configure reverse proxy (Nginx, Apache)

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Database Errors**
   - Run `python manage.py makemigrations`
   - Run `python manage.py migrate`

3. **AI Features Not Working**
   - Check if API keys are correctly set in `.env`
   - The app will use fallback algorithms if APIs are unavailable

4. **PDF Generation Issues**
   - Ensure ReportLab is installed: `pip install reportlab`

### Getting Help

- Check Django documentation: https://docs.djangoproject.com/
- Review error logs in the console
- Verify all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions about this HR Assist AI application, please refer to the documentation or create an issue in the project repository.

---

**HR Assist AI** - Transforming recruitment with artificial intelligence! 🚀
