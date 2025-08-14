// API Base URL
const API_BASE = '/api';

// Global state
let currentUser = null;
let currentSection = 'home';
let authToken = localStorage.getItem('authToken');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    
    // Check if user is already logged in
    if (authToken) {
        verifyToken();
    }
});

function initializeApp() {
    // Show home section by default
    showSection('home');
}

function setupEventListeners() {
    // Navigation
    document.getElementById('login-btn').addEventListener('click', () => showSection('login'));
    document.getElementById('register-btn').addEventListener('click', () => showSection('register'));
    document.getElementById('hero-login').addEventListener('click', () => showSection('login'));
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Form switches
    document.getElementById('switch-to-register').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('register');
    });
    document.getElementById('switch-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('login');
    });
    
    // Forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('job-form').addEventListener('submit', handleJobSubmit);
    document.getElementById('application-form').addEventListener('submit', handleApplicationSubmit);
    document.getElementById('interview-form').addEventListener('submit', handleInterviewSchedule);
    document.getElementById('interview-result-form').addEventListener('submit', handleInterviewResult);
    document.getElementById('candidate-selection-form').addEventListener('submit', handleCandidateSelection);
    document.getElementById('willingness-form').addEventListener('submit', handleWillingnessConfirmation);
    document.getElementById('job-closure-form').addEventListener('submit', handleJobClosure);
    
    // Dashboard tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.getAttribute('data-tab');
            switchTab(tabName, e.target);
        });
    });
    
    // Modal controls
    document.getElementById('create-job-btn').addEventListener('click', () => openJobModal());
    document.getElementById('close-job-modal').addEventListener('click', () => closeJobModal());
    document.getElementById('cancel-job').addEventListener('click', () => closeJobModal());
    document.getElementById('close-application-modal').addEventListener('click', () => closeApplicationModal());
    document.getElementById('cancel-application').addEventListener('click', () => closeApplicationModal());
    
    // Interview modal controls
    document.getElementById('close-interview-modal').addEventListener('click', () => closeInterviewModal());
    document.getElementById('cancel-interview').addEventListener('click', () => closeInterviewModal());
    document.getElementById('interview-form').addEventListener('submit', handleInterviewSubmit);
    
    // Profile button
    document.getElementById('view-profile-btn').addEventListener('click', () => openProfileModal());
    
    // User type selection handler
    document.getElementById('reg-usertype').addEventListener('change', (e) => {
        const adminCodeGroup = document.getElementById('admin-code-group');
        const adminCodeInput = document.getElementById('reg-admin-code');
        
        if (e.target.value === 'hr') {
            adminCodeGroup.style.display = 'block';
            adminCodeInput.required = true;
        } else {
            adminCodeGroup.style.display = 'none';
            adminCodeInput.required = false;
            adminCodeInput.value = '';
        }
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    showLoading(true);
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = {
                username: username,
                user_type: data.user_type,
                user_id: data.user_id
            };
            
            showToast('Login successful!', 'success');
            updateNavigation();
            
            // Redirect to appropriate dashboard
            if (data.user_type === 'hr') {
                showSection('hr-dashboard');
                loadJobs();
            } else {
                showSection('candidate-dashboard');
                loadJobsForCandidate();
            }
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
        console.error('Login error:', error);
    } finally {
        showLoading(false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    showLoading(true);
    
    const userType = document.getElementById('reg-usertype').value;
    const adminCode = document.getElementById('reg-admin-code').value;
    
    // Enhanced validation for admin code
    if (userType === 'hr') {
        if (!adminCode) {
            showToast('Admin secret code is required for HR registration.', 'error');
            showLoading(false);
            return;
        }
        if (adminCode !== 'xxxxx') {
            showToast('Invalid admin secret code. Please contact administrator for the correct code.', 'error');
            showLoading(false);
            return;
        }
    }
    
    // Validate other required fields
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const fullName = document.getElementById('reg-fullname').value;
    const password = document.getElementById('reg-password').value;
    
    if (!username || !email || !fullName || !password) {
        showToast('Please fill in all required fields.', 'error');
        showLoading(false);
        return;
    }
    
    const userData = {
        username: username,
        email: email,
        full_name: fullName,
        user_type: userType,
        password: password,
        admin_code: userType === 'hr' ? adminCode : null
    };
    
    try {
        console.log('Sending registration data:', { ...userData, password: '[HIDDEN]', admin_code: userType === 'hr' ? '[PROVIDED]' : null });
        
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login with your credentials.', 'success');
            showSection('login');
            // Clear form
            document.getElementById('register-form').reset();
            document.getElementById('admin-code-group').style.display = 'none';
        } else {
            console.error('Registration failed:', data);
            showToast(data.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed. Please check your connection and try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function verifyToken() {
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            updateNavigation();
            
            // Redirect to appropriate dashboard
            if (userData.user_type === 'hr') {
                showSection('hr-dashboard');
                loadJobs();
            } else {
                showSection('candidate-dashboard');
                loadJobsForCandidate();
            }
        } else {
            // Invalid token
            logout();
        }
    } catch (error) {
        console.error('Token verification error:', error);
        logout();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateNavigation();
    showSection('home');
    showToast('Logged out successfully', 'success');
}

function updateNavigation() {
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const userMenu = document.getElementById('user-menu');
    const userName = document.getElementById('user-name');
    
    if (currentUser) {
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        userMenu.style.display = 'flex';
        userName.textContent = currentUser.full_name || currentUser.username;
    } else {
        loginBtn.style.display = 'block';
        registerBtn.style.display = 'block';
        userMenu.style.display = 'none';
    }
}

// Section navigation
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
    }
}

// Tab switching
function switchTab(tabName, clickedElement = null) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
        
        // Load content based on tab
        if (tabName === 'jobs' && currentUser?.user_type === 'hr') {
            loadJobs();
        } else if (tabName === 'applications' && currentUser?.user_type === 'hr') {
            loadApplications();
        } else if (tabName === 'available-jobs' && currentUser?.user_type === 'candidate') {
            loadJobsForCandidate();
        } else if (tabName === 'my-applications' && currentUser?.user_type === 'candidate') {
            loadMyApplications();
        } else if (tabName === 'notifications' || tabName === 'inbox') {
            loadNotifications();
        }
    }
}

// Job management functions
async function loadJobs() {
    if (!authToken) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/jobs`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const jobs = await response.json();
            displayJobs(jobs, 'jobs-grid');
        } else {
            showToast('Failed to load jobs', 'error');
        }
    } catch (error) {
        showToast('Failed to load jobs', 'error');
        console.error('Load jobs error:', error);
    } finally {
        showLoading(false);
    }
}

async function loadJobsForCandidate() {
    if (!authToken) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/jobs`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const jobs = await response.json();
            displayJobsForCandidate(jobs, 'candidate-jobs-grid');
        } else {
            showToast('Failed to load jobs', 'error');
        }
    } catch (error) {
        showToast('Failed to load jobs', 'error');
        console.error('Load jobs error:', error);
    } finally {
        showLoading(false);
    }
}

function displayJobs(jobs, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (jobs.length === 0) {
        container.innerHTML = '<p>No jobs found.</p>';
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-location"><i class="fas fa-map-marker-alt"></i> ${job.work_location}</p>
                </div>
                <span class="job-status ${job.is_active ? 'active' : 'inactive'}">
                    ${job.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>
            
            <p class="job-description">${job.description}</p>
            
            <div class="job-details">
                <div class="job-detail">
                    <i class="fas fa-clock"></i>
                    <span>${job.experience_years} years experience</span>
                </div>
                <div class="job-detail">
                    <i class="fas fa-calendar"></i>
                    <span>Posted ${formatDate(job.created_at)}</span>
                </div>
            </div>
            
            <div class="job-skills">
                <strong>Required Skills:</strong>
                <div class="skills-list">
                    ${job.skills.split(',').map(skill => 
                        `<span class="skill-tag">${skill.trim()}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="job-actions">
                <button class="btn btn-secondary" onclick="editJob(${job.id})">Edit</button>
                <button class="btn btn-primary" onclick="viewJobApplications(${job.id})">
                    View Applications
                </button>
                <button class="btn btn-danger" onclick="deleteJob(${job.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function displayJobsForCandidate(jobs, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (jobs.length === 0) {
        container.innerHTML = '<p>No jobs available.</p>';
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-location"><i class="fas fa-map-marker-alt"></i> ${job.work_location}</p>
                </div>
                <span class="job-status active">Active</span>
            </div>
            
            <p class="job-description">${job.description}</p>
            
            <div class="job-details">
                <div class="job-detail">
                    <i class="fas fa-clock"></i>
                    <span>${job.experience_years} years experience</span>
                </div>
                <div class="job-detail">
                    <i class="fas fa-calendar"></i>
                    <span>Posted ${formatDate(job.created_at)}</span>
                </div>
            </div>
            
            <div class="job-skills">
                <strong>Required Skills:</strong>
                <div class="skills-list">
                    ${job.skills.split(',').map(skill => 
                        `<span class="skill-tag">${skill.trim()}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="job-actions">
                <button class="btn btn-secondary" onclick="viewJobDetails(${job.id})">View Details</button>
                <button class="btn btn-primary" onclick="applyForJob(${job.id})">Apply Now</button>
            </div>
        </div>
    `).join('');
}

// Job modal functions
function openJobModal(jobData = null) {
    const modal = document.getElementById('job-modal');
    const title = document.getElementById('job-modal-title');
    const form = document.getElementById('job-form');
    
    if (jobData) {
        title.textContent = 'Edit Job';
        // Pre-fill form with job data
        document.getElementById('job-title').value = jobData.title || '';
        document.getElementById('job-description').value = jobData.description || '';
        document.getElementById('job-experience').value = jobData.experience_years || '';
        document.getElementById('job-relevant-exp').value = jobData.relevant_experience || '';
        document.getElementById('job-skills').value = jobData.skills || '';
        document.getElementById('job-location').value = jobData.work_location || '';
        
        // Store job ID for editing
        form.dataset.jobId = jobData.id;
    } else {
        title.textContent = 'Create New Job';
        form.reset();
        delete form.dataset.jobId;
    }
    
    modal.style.display = 'block';
}

function closeJobModal() {
    document.getElementById('job-modal').style.display = 'none';
}

async function handleJobSubmit(e) {
    e.preventDefault();
    showLoading(true);
    
    const form = e.target;
    const jobId = form.dataset.jobId;
    const isEditing = !!jobId;
    
    const jobData = {
        title: document.getElementById('job-title').value,
        description: document.getElementById('job-description').value,
        experience_years: parseInt(document.getElementById('job-experience').value),
        relevant_experience: document.getElementById('job-relevant-exp').value,
        skills: document.getElementById('job-skills').value,
        work_location: document.getElementById('job-location').value,
        salary_range: document.getElementById('job-salary').value || null,
        employment_type: document.getElementById('job-type').value,
        number_of_vacancies: parseInt(document.getElementById('job-vacancies').value),
        application_deadline: document.getElementById('job-deadline').value || null
    };
    
    try {
        const url = isEditing ? `${API_BASE}/jobs/${jobId}` : `${API_BASE}/jobs`;
        const method = isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(jobData)
        });
        
        if (response.ok) {
            showToast(`Job ${isEditing ? 'updated' : 'created'} successfully!`, 'success');
            closeJobModal();
            loadJobs();
            // Set minimum date for deadline field for future use
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('job-deadline').min = tomorrow.toISOString().split('T')[0];
        } else {
            const error = await response.json();
            showToast(error.detail || `Failed to ${isEditing ? 'update' : 'create'} job`, 'error');
        }
    } catch (error) {
        showToast(`Failed to ${isEditing ? 'update' : 'create'} job`, 'error');
        console.error('Job submission error:', error);
    } finally {
        showLoading(false);
    }
}

async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job?')) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showToast('Job deleted successfully!', 'success');
            loadJobs();
        } else {
            showToast('Failed to delete job', 'error');
        }
    } catch (error) {
        showToast('Failed to delete job', 'error');
        console.error('Job deletion error:', error);
    } finally {
        showLoading(false);
    }
}

// Application functions
async function applyForJob(jobId) {
    document.getElementById('application-job-id').value = jobId;
    
    // Auto-fill user data if available
    if (authToken && currentUser) {
        try {
            const response = await fetch(`${API_BASE}/profile`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                
                // Auto-fill the form fields
                if (profile.full_name) {
                    document.getElementById('app-name').value = profile.full_name;
                }
                if (profile.email) {
                    document.getElementById('app-email').value = profile.email;
                }
                if (profile.phone) {
                    document.getElementById('app-phone').value = profile.phone;
                }
                if (profile.address) {
                    document.getElementById('app-address').value = profile.address;
                }
            }
        } catch (error) {
            console.log('Could not auto-fill profile data:', error);
        }
    }
    
    document.getElementById('application-modal').style.display = 'block';
}

function closeApplicationModal() {
    document.getElementById('application-modal').style.display = 'none';
}

async function handleApplicationSubmit(e) {
    e.preventDefault();
    showLoading(true);
    
    const formData = new FormData();
    formData.append('job_id', document.getElementById('application-job-id').value);
    formData.append('name', document.getElementById('app-name').value);
    formData.append('email', document.getElementById('app-email').value);
    formData.append('phone', document.getElementById('app-phone').value);
    formData.append('address', document.getElementById('app-address').value);
    formData.append('experience_years', document.getElementById('app-experience').value);
    formData.append('relevant_experience', document.getElementById('app-relevant-exp').value);
    formData.append('skills', document.getElementById('app-skills').value);
    formData.append('education', document.getElementById('app-education').value);
    formData.append('projects', document.getElementById('app-projects').value);
    formData.append('preferred_location', document.getElementById('app-preferred-location').value);
    formData.append('photo', document.getElementById('app-photo').files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/applications`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Application submitted successfully! Your AI score: ${result.ai_score}/10`, 'success');
            closeApplicationModal();
            document.getElementById('application-form').reset();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to submit application', 'error');
        }
    } catch (error) {
        showToast('Failed to submit application', 'error');
        console.error('Application submission error:', error);
    } finally {
        showLoading(false);
    }
}

// Load all applications for HR dashboard
async function loadApplications() {
    if (!authToken) return;
    
    showLoading(true);
    try {
        // First get all jobs created by this HR user
        const jobsResponse = await fetch(`${API_BASE}/jobs`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!jobsResponse.ok) {
            showToast('Failed to load applications', 'error');
            return;
        }
        
        const jobs = await jobsResponse.json();
        let allApplications = [];
        
        // Get applications for each job
        for (const job of jobs) {
            try {
                const appResponse = await fetch(`${API_BASE}/jobs/${job.id}/applications`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                if (appResponse.ok) {
                    const applications = await appResponse.json();
                    // Add job title to each application for display
                    applications.forEach(app => {
                        app.job_title = job.title;
                    });
                    allApplications = allApplications.concat(applications);
                }
            } catch (error) {
                console.error(`Error loading applications for job ${job.id}:`, error);
            }
        }
        
        displayApplications(allApplications);
        
    } catch (error) {
        showToast('Failed to load applications', 'error');
        console.error('Load applications error:', error);
    } finally {
        showLoading(false);
    }
}

async function viewJobApplications(jobId) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/applications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const applications = await response.json();
            displayApplications(applications);
            switchTab('applications');
        } else {
            showToast('Failed to load applications', 'error');
        }
    } catch (error) {
        showToast('Failed to load applications', 'error');
        console.error('Load applications error:', error);
    } finally {
        showLoading(false);
    }
}

function displayApplications(applications) {
    const container = document.getElementById('applications-list');
    if (!container) return;
    
    if (applications.length === 0) {
        container.innerHTML = '<p>No applications found.</p>';
        return;
    }
    
    container.innerHTML = applications.map(app => `
        <div class="application-card">
            <div class="application-header">
                <div class="candidate-info">
                    <img src="/uploads/${app.photo_path.split('/').pop()}" alt="Candidate Photo" class="candidate-photo" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMzAiIGZpbGw9IiNlZWVlZWUiLz4KPHN2ZyB4PSIxNSIgeT0iMTAiIHdpZHRoPSIzMCIgaGVpZ2h0PSI0MCI+CjxjaXJjbGUgY3g9IjE1IiBjeT0iMTIiIHI9IjgiIGZpbGw9IiM5OTk5OTkiLz4KPHBhdGggZD0ibTUgMzVjMC04IDctMTUgMTUtMTVzMTUgNyAxNSAxNXoiIGZpbGw9IiM5OTk5OTkiLz4KPC9zdmc+Cjwvc3ZnPg=='" />
                    <div class="candidate-details">
                        <h4>${app.name}</h4>
                        <p>${app.email} | ${app.phone}</p>
                        <p>${app.experience_years} years experience</p>
                        ${app.job_title ? `<p><strong>Applied for:</strong> ${app.job_title}</p>` : ''}
                    </div>
                </div>
                <div class="application-score">
                    <div class="score-circle ${getScoreClass(app.ai_score)}">
                        ${app.ai_score.toFixed(1)}
                    </div>
                    <small>AI Score</small>
                </div>
            </div>
            
            <div class="application-details">
                <div class="detail-item">
                    <span class="detail-label">Skills:</span>
                    <span class="detail-value">${app.skills}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Education:</span>
                    <span class="detail-value">${app.education}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">${app.preferred_location}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">${app.status}</span>
                </div>
            </div>
            
            <div class="job-actions">
                ${app.status === 'applied' ? 
                    `<button class="btn btn-success" onclick="shortlistCandidate(${app.id})">Shortlist</button>
                     <button class="btn btn-danger" onclick="rejectCandidate(${app.id})">Reject</button>` : 
                    ''
                }
                ${app.status === 'shortlisted' ? 
                    `<button class="btn btn-primary" onclick="downloadQuestions(${app.id})">Download Questions</button>
                     <button class="btn btn-secondary" onclick="scheduleInterview(${app.id})">Schedule Interview</button>
                     <button class="btn btn-danger" onclick="rejectCandidate(${app.id})">Reject</button>` : 
                    ''
                }
                ${app.status === 'interview_scheduled' ? 
                    `<span class="status-message"><i class="fas fa-calendar-check"></i> Interview Scheduled</span>
                     <button class="btn btn-primary" onclick="downloadQuestions(${app.id})">Download Questions</button>` : 
                    ''
                }
                ${app.status === 'rejected' ? 
                    `<span class="status-message rejected"><i class="fas fa-times-circle"></i> Application Rejected</span>` : 
                    ''
                }
            </div>
        </div>
    `).join('');
}

function getScoreClass(score) {
    if (score >= 7) return 'score-high';
    if (score >= 5) return 'score-medium';
    return 'score-low';
}

async function shortlistCandidate(applicationId) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/shortlist`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showToast('Candidate shortlisted successfully!', 'success');
            // Reload applications to update status
            loadApplications();
        } else {
            showToast('Failed to shortlist candidate', 'error');
        }
    } catch (error) {
        showToast('Failed to shortlist candidate', 'error');
        console.error('Shortlist error:', error);
    } finally {
        showLoading(false);
    }
}

async function rejectCandidate(applicationId) {
    if (!confirm('Are you sure you want to reject this candidate? This action cannot be undone.')) {
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/reject`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showToast('Candidate rejected successfully!', 'success');
            // Reload applications to update status
            loadApplications();
        } else {
            showToast('Failed to reject candidate', 'error');
        }
    } catch (error) {
        showToast('Failed to reject candidate', 'error');
        console.error('Reject error:', error);
    } finally {
        showLoading(false);
    }
}

async function downloadQuestions(applicationId) {
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/questions/pdf`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `interview_questions_${applicationId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showToast('Interview questions downloaded!', 'success');
        } else {
            showToast('Failed to download questions', 'error');
        }
    } catch (error) {
        showToast('Failed to download questions', 'error');
        console.error('Download error:', error);
    }
}

// Notification functions
async function loadNotifications() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/notifications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const notifications = await response.json();
            displayNotifications(notifications);
        } else {
            showToast('Failed to load notifications', 'error');
        }
    } catch (error) {
        showToast('Failed to load notifications', 'error');
        console.error('Load notifications error:', error);
    }
}

function displayNotifications(notifications) {
    const containerId = currentUser.user_type === 'hr' ? 'notifications-list' : 'candidate-notifications-list';
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = '<p>No notifications found.</p>';
        return;
    }
    
    container.innerHTML = notifications.map(notification => `
        <div class="notification-card ${notification.is_read ? 'read' : 'unread'}">
            <div class="notification-header">
                <span class="notification-title">${notification.title}</span>
                <span class="notification-time">${formatDate(notification.created_at)}</span>
            </div>
            <div class="notification-message">${notification.message}</div>
            ${notification.webex_link ? 
                `<div style="margin-top: 1rem;">
                    <strong>Meeting Link:</strong> 
                    <a href="${notification.webex_link}" target="_blank" class="btn btn-primary btn-sm">Join Meeting</a>
                </div>` : 
                ''
            }
        </div>
    `).join('');
}

// Utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
        if (container.contains(toast)) {
            container.removeChild(toast);
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// Additional helper functions for features not yet implemented
async function editJob(jobId) {
    if (!authToken) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const job = await response.json();
            openJobModal(job);
        } else {
            showToast('Failed to load job details for editing', 'error');
        }
    } catch (error) {
        showToast('Failed to load job details for editing', 'error');
        console.error('Edit job error:', error);
    } finally {
        showLoading(false);
    }
}

function viewJobDetails(jobId) {
    if (!authToken) return;
    
    showLoading(true);
    fetch(`${API_BASE}/jobs/${jobId}`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    })
    .then(response => response.json())
    .then(job => {
        // Create a modal or expand view to show job details
        const modal = createJobDetailsModal(job);
        document.body.appendChild(modal);
        modal.style.display = 'block';
    })
    .catch(error => {
        showToast('Failed to load job details', 'error');
        console.error('Job details error:', error);
    })
    .finally(() => {
        showLoading(false);
    });
}

function createJobDetailsModal(job) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'job-details-modal';
    
    // Helper function to escape HTML
    const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${escapeHtml(job.title)}</h3>
                <span class="close" onclick="closeJobDetailsModal()">&times;</span>
            </div>
            <div class="job-details-content">
                <div class="detail-section">
                    <h4>Job Description</h4>
                    <p>${escapeHtml(job.description)}</p>
                </div>
                <div class="detail-section">
                    <h4>Requirements</h4>
                    <p><strong>Experience:</strong> ${job.experience_years} years</p>
                    <p><strong>Skills:</strong> ${escapeHtml(job.skills)}</p>
                    <p><strong>Location:</strong> ${escapeHtml(job.work_location)}</p>
                </div>
                ${job.relevant_experience ? `
                <div class="detail-section">
                    <h4>Preferred Experience</h4>
                    <p>${escapeHtml(job.relevant_experience)}</p>
                </div>
                ` : ''}
                <div class="detail-section">
                    <h4>Job Information</h4>
                    <p><strong>Posted:</strong> ${formatDate(job.created_at)}</p>
                    <p><strong>Job ID:</strong> #${job.id}</p>
                </div>
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="closeJobDetailsModal()">Close</button>
                ${currentUser?.user_type === 'candidate' ? 
                    `<button class="btn btn-primary" onclick="closeJobDetailsModal(); applyForJob(${job.id})">Apply Now</button>` : 
                    ''
                }
            </div>
        </div>
    `;
    
    return modal;
}

function closeJobDetailsModal() {
    const modal = document.getElementById('job-details-modal');
    if (modal) {
        modal.remove();
    }
}

async function loadMyApplications() {
    if (!authToken) {
        showToast('Please log in to view your applications', 'error');
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/my-applications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const applications = await response.json();
            displayMyApplications(applications);
        } else {
            const errorData = await response.text();
            console.error('Response error:', response.status, errorData);
            showToast(`Failed to load applications (${response.status})`, 'error');
        }
    } catch (error) {
        showToast('Failed to load applications', 'error');
        console.error('Load my applications error:', error);
    } finally {
        showLoading(false);
    }
}

function displayMyApplications(applications) {
    const container = document.getElementById('my-applications-list');
    if (!container) return;
    
    if (applications.length === 0) {
        container.innerHTML = '<div class="no-data"><p>You haven\'t applied to any jobs yet.</p></div>';
        return;
    }
    
    container.innerHTML = applications.map(app => `
        <div class="application-card">
            <div class="application-header">
                <div class="job-info">
                    <h4>${app.job_title}</h4>
                    <p><i class="fas fa-map-marker-alt"></i> ${app.job_location}</p>
                    <p><i class="fas fa-clock"></i> Applied: ${formatDate(app.applied_at)}</p>
                </div>
                <div class="application-score">
                    <div class="score-circle ${getScoreClass(app.ai_score)}">
                        ${app.ai_score.toFixed(1)}
                    </div>
                    <small>AI Score</small>
                </div>
            </div>
            
            <div class="application-status">
                <span class="status-badge status-${app.status.toLowerCase()}">${app.status.charAt(0).toUpperCase() + app.status.slice(1)}</span>
            </div>
            
            <div class="application-details">
                <div class="detail-item">
                    <span class="detail-label">Skills:</span>
                    <span class="detail-value">${app.skills}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Experience:</span>
                    <span class="detail-value">${app.experience_years} years</span>
                </div>
            </div>
            
            <div class="job-actions">
                <button class="btn btn-secondary" onclick="viewJobDetails(${app.job_id})">View Job</button>
                ${app.status === 'shortlisted' ? 
                    '<span class="status-message"><i class="fas fa-star"></i> Congratulations! You have been shortlisted.</span>' : 
                    ''
                }
            </div>
        </div>
    `).join('');
}

function scheduleInterview(applicationId) {
    document.getElementById('interview-application-id').value = applicationId;
    document.getElementById('interview-modal').style.display = 'block';
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('interview-date').min = today;
}

function closeInterviewModal() {
    document.getElementById('interview-modal').style.display = 'none';
    document.getElementById('interview-form').reset();
}

async function handleInterviewSubmit(e) {
    e.preventDefault();
    showLoading(true);
    
    const applicationId = document.getElementById('interview-application-id').value;
    const interviewData = {
        interview_date: document.getElementById('interview-date').value,
        interview_time: document.getElementById('interview-time').value,
        timezone: document.getElementById('interview-timezone').value,
        platform: document.getElementById('interview-platform').value,
        meeting_link: document.getElementById('interview-link').value,
        meeting_password: document.getElementById('interview-password').value,
        notes: document.getElementById('interview-notes').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/schedule-interview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(interviewData)
        });
        
        if (response.ok) {
            showToast('Interview scheduled successfully!', 'success');
            closeInterviewModal();
            loadApplications(); // Reload to update status
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to schedule interview', 'error');
        }
    } catch (error) {
        showToast('Failed to schedule interview', 'error');
        console.error('Interview scheduling error:', error);
    } finally {
        showLoading(false);
    }
}

// Profile management functions
async function openProfileModal() {
    if (!authToken) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const profile = await response.json();
            createProfileModal(profile);
        } else {
            showToast('Failed to load profile', 'error');
        }
    } catch (error) {
        showToast('Failed to load profile', 'error');
        console.error('Profile load error:', error);
    } finally {
        showLoading(false);
    }
}

function createProfileModal(profile) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'profile-modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>My Profile</h3>
                <span class="close" onclick="closeProfileModal()">&times;</span>
            </div>
            <form id="profile-form">
                <div class="form-group">
                    <label for="profile-username">Username</label>
                    <input type="text" id="profile-username" value="${profile.username}" readonly>
                </div>
                <div class="form-group">
                    <label for="profile-fullname">Full Name</label>
                    <input type="text" id="profile-fullname" value="${profile.full_name}" readonly>
                </div>
                <div class="form-group">
                    <label for="profile-email">Email</label>
                    <input type="email" id="profile-email" value="${profile.email || ''}" required>
                </div>
                <div class="form-group">
                    <label for="profile-phone">Phone</label>
                    <input type="tel" id="profile-phone" value="${profile.phone || ''}" placeholder="Enter your phone number">
                </div>
                <div class="form-group">
                    <label for="profile-address">Address</label>
                    <textarea id="profile-address" rows="3" placeholder="Enter your address">${profile.address || ''}</textarea>
                </div>
                <div class="form-group">
                    <label for="profile-usertype">User Type</label>
                    <input type="text" id="profile-usertype" value="${profile.user_type}" readonly>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeProfileModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Profile</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'block';
    
    // Add form submit handler
    document.getElementById('profile-form').addEventListener('submit', handleProfileUpdate);
}

function closeProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal) {
        modal.remove();
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    showLoading(true);
    
    const formData = new FormData();
    formData.append('email', document.getElementById('profile-email').value);
    formData.append('phone', document.getElementById('profile-phone').value);
    formData.append('address', document.getElementById('profile-address').value);
    
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            showToast('Profile updated successfully!', 'success');
            closeProfileModal();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to update profile', 'error');
        }
    } catch (error) {
        showToast('Failed to update profile', 'error');
        console.error('Profile update error:', error);
    } finally {
        showLoading(false);
    }
}

// Enhanced Interview Scheduling with Conflict Detection
async function handleInterviewSchedule(e) {
    e.preventDefault();
    showLoading(true);
    
    const applicationId = document.getElementById('interview-application-id').value;
    const interviewData = {
        interview_type: document.getElementById('interview-type').value,
        interview_date: document.getElementById('interview-date').value,
        interview_time: document.getElementById('interview-time').value,
        duration_minutes: parseInt(document.getElementById('interview-duration').value),
        timezone: document.getElementById('interview-timezone').value,
        platform: document.getElementById('interview-platform').value,
        meeting_link: document.getElementById('interview-link').value,
        meeting_password: document.getElementById('interview-password').value || null,
        notes: document.getElementById('interview-notes').value || null
    };
    
    try {
        // First check for conflicts
        const conflictResponse = await fetch(`${API_BASE}/interviews/conflicts?interview_date=${interviewData.interview_date}&interview_time=${interviewData.interview_time}&duration_minutes=${interviewData.duration_minutes}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (conflictResponse.ok) {
            const conflictData = await conflictResponse.json();
            if (conflictData.has_conflict) {
                const confirmSchedule = confirm(`Interview conflict detected!\n\nYou already have an interview with ${conflictData.conflict_details.candidate_name} from ${conflictData.conflict_details.interview_start} to ${conflictData.conflict_details.interview_end}.\n\nDo you want to schedule anyway?`);
                if (!confirmSchedule) {
                    showLoading(false);
                    return;
                }
            }
        }
        
        // Proceed with scheduling
        const response = await fetch(`${API_BASE}/applications/${applicationId}/schedule-interview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(interviewData)
        });
        
        if (response.ok) {
            showToast('Interview scheduled successfully!', 'success');
            closeInterviewModal();
            loadApplications();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to schedule interview', 'error');
        }
    } catch (error) {
        showToast('Failed to schedule interview', 'error');
        console.error('Interview scheduling error:', error);
    } finally {
        showLoading(false);
    }
}

// Interview Result Handler
async function handleInterviewResult(e) {
    e.preventDefault();
    showLoading(true);
    
    const interviewId = document.getElementById('interview-result-id').value;
    const resultData = {
        result: document.getElementById('interview-result').value,
        feedback: document.getElementById('interview-feedback').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/interviews/${interviewId}/update-result`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(resultData)
        });
        
        if (response.ok) {
            showToast('Interview result updated successfully!', 'success');
            closeInterviewResultModal();
            loadApplications();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to update interview result', 'error');
        }
    } catch (error) {
        showToast('Failed to update interview result', 'error');
        console.error('Interview result update error:', error);
    } finally {
        showLoading(false);
    }
}

// Candidate Selection Handler
async function handleCandidateSelection(e) {
    e.preventDefault();
    showLoading(true);
    
    const applicationId = document.getElementById('selection-application-id').value;
    const selectionData = {
        salary_offered: document.getElementById('salary-offered').value || null,
        start_date: document.getElementById('start-date').value || null,
        willingness_deadline_days: parseInt(document.getElementById('willingness-deadline-days').value),
        notes: document.getElementById('selection-notes').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/select-candidate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(selectionData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast('Candidate selected successfully! Job offer sent.', 'success');
            closeCandidateSelectionModal();
            loadApplications();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to select candidate', 'error');
        }
    } catch (error) {
        showToast('Failed to select candidate', 'error');
        console.error('Candidate selection error:', error);
    } finally {
        showLoading(false);
    }
}

// Willingness Confirmation Handler
async function handleWillingnessConfirmation(e) {
    e.preventDefault();
    showLoading(true);
    
    const applicationId = document.getElementById('willingness-application-id').value;
    const confirmed = document.querySelector('input[name="willingness"]:checked').value === 'true';
    const willingnessData = {
        confirmed: confirmed,
        notes: document.getElementById('willingness-notes').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/applications/${applicationId}/confirm-willingness`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(willingnessData)
        });
        
        if (response.ok) {
            showToast(`Job offer ${confirmed ? 'accepted' : 'declined'} successfully!`, 'success');
            closeWillingnessModal();
            loadApplications();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to submit response', 'error');
        }
    } catch (error) {
        showToast('Failed to submit response', 'error');
        console.error('Willingness confirmation error:', error);
    } finally {
        showLoading(false);
    }
}

// Job Closure Handler
async function handleJobClosure(e) {
    e.preventDefault();
    showLoading(true);
    
    const jobId = document.getElementById('closure-job-id').value;
    const closeData = {
        reason: document.getElementById('closure-reason').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/close`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(closeData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Job closed successfully! ${result.applications_affected} candidates notified.`, 'success');
            closeJobClosureModal();
            loadJobs();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to close job', 'error');
        }
    } catch (error) {
        showToast('Failed to close job', 'error');
        console.error('Job closure error:', error);
    } finally {
        showLoading(false);
    }
}

// Modal close functions
function closeInterviewResultModal() {
    document.getElementById('interview-result-modal').style.display = 'none';
}

function closeCandidateSelectionModal() {
    document.getElementById('candidate-selection-modal').style.display = 'none';
}

function closeWillingnessModal() {
    document.getElementById('willingness-modal').style.display = 'none';
}

function closeJobClosureModal() {
    document.getElementById('job-closure-modal').style.display = 'none';
}

// Initialize minimum date for job deadline
document.addEventListener('DOMContentLoaded', function() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const jobDeadlineField = document.getElementById('job-deadline');
    if (jobDeadlineField) {
        jobDeadlineField.min = tomorrow.toISOString().split('T')[0];
    }
});
