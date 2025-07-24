# HR Assist AI - Smart Recruitment Platform

An AI-powered HR recruitment web application built with FastAPI backend and vanilla HTML/CSS/JS frontend.

## Features

### For HR Managers:
- **User Authentication**: Secure login/signup with JWT tokens
- **Job Management**: Create, edit, view, and delete job postings
- **Application Management**: View and manage candidate applications
- **AI-Powered Scoring**: Automatic candidate scoring based on job requirements
- **Interview Questions**: AI-generated interview questions for shortlisted candidates
- **PDF Export**: Download interview questions as PDF
- **Notifications**: Real-time updates and notifications
- **Candidate Shortlisting**: One-click shortlisting for qualified candidates

### For Candidates:
- **Job Browser**: View all available job postings
- **Application Submission**: Apply for jobs with detailed profile information
- **Photo Upload**: Upload profile photos with applications
- **Application Tracking**: Track application status
- **Notifications**: Receive interview invitations and updates
- **Profile Management**: Update contact information

### AI Features:
- **Smart Matching**: AI scores candidates based on job requirements (1-10 scale)
- **Interview Questions**: Auto-generated personalized interview questions
- **Skill Analysis**: Intelligent parsing of candidate skills and experience

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI Integration**: OpenAI GPT for candidate scoring and question generation
- **File Handling**: Pillow for image processing
- **PDF Generation**: ReportLab for interview question PDFs
- **Deployment**: Docker with Nginx reverse proxy

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional)
- OpenAI API key (for AI features)

### Installation

1. **Clone or create the project directory**:
   ```bash
   mkdir hr-assist-ai
   cd hr-assist-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env` file and update with your settings
   - Add your OpenAI API key in the `.env` file:
     ```
     OPENAI_API_KEY=your-actual-openai-api-key-here
     ```

5. **Initialize the database**:
   ```bash
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
   ```

6. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the application**:
   - Open your browser and go to `http://localhost:8000`
   - The API documentation is available at `http://localhost:8000/docs`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - HTTP: `http://localhost`
   - HTTPS: `https://localhost` (requires SSL certificates)

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./hr_assist.db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### SSL Configuration

For production deployment with HTTPS:

1. Generate SSL certificates
2. Place them in the `ssl/` directory
3. Update `nginx.conf` with correct certificate paths
4. Use Docker Compose with Nginx

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Job Management
- `GET /api/jobs` - List all jobs
- `POST /api/jobs` - Create new job (HR only)
- `GET /api/jobs/{id}` - Get specific job
- `PUT /api/jobs/{id}` - Update job (HR only)
- `DELETE /api/jobs/{id}` - Delete job (HR only)

### Applications
- `POST /api/applications` - Submit job application
- `GET /api/jobs/{id}/applications` - Get job applications (HR only)
- `POST /api/applications/{id}/shortlist` - Shortlist candidate (HR only)
- `GET /api/applications/{id}/questions/pdf` - Download interview questions PDF

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark notification as read

### User Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

## Database Schema

### Users Table
- User authentication and profile information
- Supports both HR and candidate user types

### Jobs Table
- Job postings with detailed requirements
- Skills, experience, and location information

### Applications Table
- Candidate applications with detailed profiles
- AI scoring and application status tracking

### Notifications Table
- System notifications and interview invitations
- Support for interview scheduling with meeting links

## AI Integration

### Candidate Scoring
The system uses OpenAI's GPT model to analyze:
- Job requirements vs. candidate experience
- Skill matching and relevance
- Educational background alignment
- Project experience correlation

### Interview Question Generation
AI generates personalized interview questions based on:
- Job description and requirements
- Candidate's background and skills
- Industry-specific knowledge areas
- Behavioral and technical aspects

### Fallback System
If OpenAI API is unavailable, the system includes:
- Rule-based scoring algorithm
- Pre-defined interview question templates
- Basic skill matching logic

## Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Authentication**: Stateless token-based authentication
- **Input Validation**: Pydantic models for API validation
- **File Upload Security**: Image type validation and secure storage
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **CORS Protection**: Configurable CORS middleware

## File Structure

```
hr-assist-ai/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic validation schemas
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── nginx.conf           # Nginx configuration
├── static/              # Frontend files
│   ├── index.html       # Main HTML file
│   ├── styles.css       # CSS styles
│   └── script.js        # JavaScript functionality
└── uploads/             # User uploaded files
```

## Development

### Adding New Features

1. **Backend**: Add new routes in `main.py`
2. **Database**: Update models in `models.py`
3. **Validation**: Add schemas in `schemas.py`
4. **Frontend**: Update HTML, CSS, and JavaScript in `static/`

### Testing

```bash
# Install development dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment Options

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Production
```bash
docker-compose -f docker-compose.yml up -d
```

### Cloud Deployment
The application can be deployed on:
- AWS (EC2, ECS, Lambda)
- Google Cloud Platform
- Azure
- Heroku
- DigitalOcean

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   - Ensure your API key is correctly set in `.env`
   - Check API key permissions and billing

2. **Database Connection Issues**:
   - Verify SQLite file permissions
   - Check database file path in `.env`

3. **File Upload Problems**:
   - Ensure `uploads/` directory exists
   - Check file size limits in nginx configuration

4. **JWT Token Errors**:
   - Verify SECRET_KEY in environment variables
   - Check token expiration settings

### Performance Optimization

- Use connection pooling for database
- Implement caching for frequent queries
- Optimize image sizes and formats
- Use CDN for static files in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.


1. Testing in Python Virtual Environment
Prerequisites Setup

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir uploads

# Set environment variables (update .env file with your values)
# Add your OpenAI API key to .env file:
OPENAI_API_KEY=your-actual-openai-api-key-here

Run the Development Server

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run with Python directly
python main.py

Access the Application
Main App: http://localhost:8000
API Documentation: http://localhost:8000/docs
Alternative API Docs: http://localhost:8000/redoc
2. Docker Build and Deployment
Build Docker Image

# Build the Docker image
docker build -t hr-assist-ai .

# Run single container
docker run -p 8000:8000 -e OPENAI_API_KEY=your-api-key hr-assist-ai

Docker Compose Deployment (Recommended)

# Set your OpenAI API key in environment
export OPENAI_API_KEY=your-actual-openai-api-key

# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

SSL Setup for Production (Optional)
# Create SSL directory
mkdir ssl

# Generate self-signed certificates (for testing)
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Or use Let's Encrypt for production
# certbot certonly --standalone -d yourdomain.com

3. Testing the Application
Test User Registration and Login
Register HR User:

Go to Register page
Create account with user type "HR Manager"
Login with credentials
Register Candidate User:

Open incognito/private window
Register with user type "Candidate"
Login with credentials
Test HR Functionality
Create Job Postings:

Login as HR user
Click "Create New Job"
Fill job details and save
Verify job appears in listings
Manage Jobs:

Edit job postings
View job applications
Delete jobs
Test Candidate Functionality
Browse Jobs:

Login as candidate
View available jobs
Check job details
Apply for Jobs:

Click "Apply Now"
Fill application form
Upload photo
Submit application
Check AI score
Test AI Features
Candidate Scoring:

Submit applications with different skill sets
Verify AI scoring (1-10 scale)
Check scoring logic
Interview Questions:

Shortlist candidates (score ≥ 5)
Download interview questions PDF
Verify personalized questions
4. Separate Server Deployment
Cloud Deployment Options
AWS Deployment

# Using AWS EC2
1. Launch EC2 instance (Ubuntu 20.04+)
2. Install Docker and Docker Compose
3. Clone/upload your application
4. Set environment variables
5. Run: docker-compose up -d --build
6. Configure security groups (ports 80, 443)

DigitalOcean Deployment
# Using DigitalOcean Droplet
1. Create droplet with Docker pre-installed
2. Upload application files
3. Set environment variables
4. Run: docker-compose up -d --build
5. Configure firewall rules
Google Cloud Platform
# Using Google Cloud Run
1. Build image: docker build -t gcr.io/PROJECT-ID/hr-assist-ai .
2. Push image: docker push gcr.io/PROJECT-ID/hr-assist-ai
3. Deploy: gcloud run deploy --image gcr.io/PROJECT-ID/hr-assist-ai

Production Configuration
Environment Variables for Production

# Update .env file for production
DATABASE_URL=sqlite:///./hr_assist.db
SECRET_KEY=generate-strong-secret-key-here
OPENAI_API_KEY=your-production-openai-key
DEBUG=False
HOST=0.0.0.0
PORT=8000


Nginx Configuration (if not using Docker Compose)

# Install Nginx
sudo apt update && sudo apt install nginx

# Copy nginx.conf to /etc/nginx/sites-available/hr-assist
sudo ln -s /etc/nginx/sites-available/hr-assist /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx


5. Testing Checklist
Basic Functionality
<input disabled="" type="checkbox"> Home page loads correctly
<input disabled="" type="checkbox"> User registration works (HR and Candidate)
<input disabled="" type="checkbox"> User login/logout works
<input disabled="" type="checkbox"> Navigation between sections works
<input disabled="" type="checkbox"> Responsive design on mobile
HR Features
<input disabled="" type="checkbox"> Create job postings
<input disabled="" type="checkbox"> Edit job postings
<input disabled="" type="checkbox"> Delete job postings
<input disabled="" type="checkbox"> View job applications
<input disabled="" type="checkbox"> Shortlist candidates
<input disabled="" type="checkbox"> Download interview questions PDF
<input disabled="" type="checkbox"> View notifications
Candidate Features
<input disabled="" type="checkbox"> Browse available jobs
<input disabled="" type="checkbox"> View job details
<input disabled="" type="checkbox"> Submit job applications
<input disabled="" type="checkbox"> Upload profile photos
<input disabled="" type="checkbox"> Receive AI scoring
<input disabled="" type="checkbox"> View application status
<input disabled="" type="checkbox"> Receive notifications
AI Integration
<input disabled="" type="checkbox"> Candidate scoring works (with/without OpenAI)
<input disabled="" type="checkbox"> Interview questions generated
<input disabled="" type="checkbox"> PDF generation works
<input disabled="" type="checkbox"> Fallback systems work when OpenAI unavailable
Security & Performance
<input disabled="" type="checkbox"> JWT authentication works
<input disabled="" type="checkbox"> File uploads are secure
<input disabled="" type="checkbox"> Database operations work
<input disabled="" type="checkbox"> Error handling works
<input disabled="" type="checkbox"> CORS configured properly
6. Troubleshooting Common Issues
Database Issues
# Reset database
rm hr_assist.db
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"


Docker Issues
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache


Port Conflicts
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Use different port
uvicorn main:app --port 8080

7. Performance Optimization
For Production
# Use multiple workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Use Gunicorn for production
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

Initialize the database:
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

Start the FastAPI server:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

Access the application:
Main app: http://localhost:8000
API documentation: http://localhost:8000/docs
The application should now run successfully with all dependencies properly installed.
