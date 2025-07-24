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

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the troubleshooting section above
