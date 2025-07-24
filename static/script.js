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
    
    // Dashboard tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Modal controls
    document.getElementById('create-job-btn').addEventListener('click', () => openJobModal());
    document.getElementById('close-job-modal').addEventListener('click', () => closeJobModal());
    document.getElementById('cancel-job').addEventListener('click', () => closeJobModal());
    document.getElementById('close-application-modal').addEventListener('click', () => closeApplicationModal());
    document.getElementById('cancel-application').addEventListener('click', () => closeApplicationModal());
    
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
    
    const userData = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        full_name: document.getElementById('reg-fullname').value,
        user_type: document.getElementById('reg-usertype').value,
        password: document.getElementById('reg-password').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            showSection('login');
            // Clear form
            document.getElementById('register-form').reset();
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
        console.error('Registration error:', error);
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
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
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
function openJobModal(jobId = null) {
    const modal = document.getElementById('job-modal');
    const title = document.getElementById('job-modal-title');
    const form = document.getElementById('job-form');
    
    if (jobId) {
        title.textContent = 'Edit Job';
        // Load job data for editing
        loadJobForEdit(jobId);
    } else {
        title.textContent = 'Create New Job';
        form.reset();
    }
    
    modal.style.display = 'block';
}

function closeJobModal() {
    document.getElementById('job-modal').style.display = 'none';
}

async function handleJobSubmit(e) {
    e.preventDefault();
    showLoading(true);
    
    const jobData = {
        title: document.getElementById('job-title').value,
        description: document.getElementById('job-description').value,
        experience_years: parseInt(document.getElementById('job-experience').value),
        relevant_experience: document.getElementById('job-relevant-exp').value,
        skills: document.getElementById('job-skills').value,
        work_location: document.getElementById('job-location').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/jobs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(jobData)
        });
        
        if (response.ok) {
            showToast('Job created successfully!', 'success');
            closeJobModal();
            loadJobs();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to create job', 'error');
        }
    } catch (error) {
        showToast('Failed to create job', 'error');
        console.error('Job creation error:', error);
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
function applyForJob(jobId) {
    document.getElementById('application-job-id').value = jobId;
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
                ${app.ai_score >= 5 && app.status === 'applied' ? 
                    `<button class="btn btn-success" onclick="shortlistCandidate(${app.id})">Shortlist</button>` : 
                    ''
                }
                ${app.status === 'shortlisted' ? 
                    `<button class="btn btn-primary" onclick="downloadQuestions(${app.id})">Download Questions</button>
                     <button class="btn btn-secondary" onclick="scheduleInterview(${app.id})">Schedule Interview</button>` : 
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
            viewJobApplications(document.getElementById('application-job-id').value);
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
function editJob(jobId) {
    showToast('Edit job feature coming soon!', 'info');
}

function viewJobDetails(jobId) {
    showToast('Job details view coming soon!', 'info');
}

function loadMyApplications() {
    showToast('My applications feature coming soon!', 'info');
}

function scheduleInterview(applicationId) {
    showToast('Interview scheduling feature coming soon!', 'info');
}
