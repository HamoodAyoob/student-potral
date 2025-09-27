// Yenepoya Portal - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSidebar();
    initDateTime();
    initNotifications();
    initLoadingStates();
    initFormValidation();
    initTimetable();
    initAttendance();
    initAssignments();
    
    // Add fade-in animation to content
    document.querySelector('.content-area')?.classList.add('fade-in');
});

// Sidebar Management
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            }
        });
        
        // Close sidebar on mobile when clicking outside
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('show');
            }
        });
    }
}

// Date and Time Display
function initDateTime() {
    const dateTimeElement = document.getElementById('currentDateTime');
    if (dateTimeElement) {
        updateDateTime();
        setInterval(updateDateTime, 1000); // Update every second
    }
    
    function updateDateTime() {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        dateTimeElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Notifications System
function initNotifications() {
    loadNotifications();
    setInterval(loadNotifications, 30000); // Check every 30 seconds
    
    // Handle notification dropdown toggle
    const notificationDropdown = document.getElementById('notificationDropdown');
    if (notificationDropdown) {
        // Hide badge when dropdown is clicked
        notificationDropdown.addEventListener('click', function() {
            hideNotificationBadge();
        });
        
        // Also hide badge when dropdown is shown via Bootstrap events
        notificationDropdown.addEventListener('show.bs.dropdown', function() {
            hideNotificationBadge();
        });
        
        // Hide badge when dropdown becomes visible
        notificationDropdown.addEventListener('shown.bs.dropdown', function() {
            hideNotificationBadge();
        });
    }
}

function loadNotifications() {
    fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
            updateNotificationUI(data.notifications);
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            // For testing - show mock notifications if API fails
            const mockNotifications = [
                {
                    id: 1,
                    title: 'New Assignment',
                    message: 'Software Engineering assignment has been posted',
                    type: 'assignment',
                    icon: 'fas fa-tasks',
                    time: new Date().toISOString()
                },
                {
                    id: 2,
                    title: 'Result Published', 
                    message: 'Your Deep Learning exam result is now available',
                    type: 'result',
                    icon: 'fas fa-chart-bar',
                    time: new Date(Date.now() - 3600000).toISOString()
                }
            ];
            updateNotificationUI(mockNotifications);
        });
}

function updateNotificationUI(notifications) {
    const notificationCount = document.getElementById('notificationCount');
    const notificationMenu = document.getElementById('notificationMenu');
    
    if (notificationCount) {
        if (notifications.length > 0) {
            notificationCount.textContent = notifications.length;
            notificationCount.style.display = 'flex';
            notificationCount.classList.remove('d-none');
        } else {
            notificationCount.style.display = 'none';
            notificationCount.classList.add('d-none');
        }
    }
    
    if (notificationMenu) {
        // Clear existing content except header
        const header = notificationMenu.querySelector('.dropdown-header');
        const divider = notificationMenu.querySelector('.dropdown-divider');
        notificationMenu.innerHTML = '';
        
        if (header) notificationMenu.appendChild(header);
        if (divider) notificationMenu.appendChild(divider);
        
        if (notifications.length > 0) {
            notifications.forEach(notification => {
                const item = createNotificationItem(notification);
                notificationMenu.appendChild(item);
            });
        } else {
            const emptyItem = document.createElement('li');
            emptyItem.className = 'text-center p-3 text-muted';
            emptyItem.innerHTML = '<i class="fas fa-bell-slash mb-2"></i><br>No notifications';
            notificationMenu.appendChild(emptyItem);
        }
    }
}

function hideNotificationBadge() {
    const notificationCount = document.getElementById('notificationCount');
    if (notificationCount) {
        console.log('Hiding notification badge'); // Debug log
        notificationCount.style.display = 'none';
        notificationCount.classList.add('d-none');
    }
}

function createNotificationItem(notification) {
    const li = document.createElement('li');
    li.className = 'notification-item';
    
    const colorClass = getNotificationColor(notification.type);
    
    li.innerHTML = `
        <div class="d-flex align-items-start gap-3">
            <div class="notification-icon ${colorClass}">
                <i class="${notification.icon}"></i>
            </div>
            <div class="flex-grow-1">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${formatNotificationTime(notification.time)}</div>
            </div>
        </div>
    `;
    
    return li;
}

function getNotificationColor(type) {
    const colors = {
        'assignment': 'text-primary',
        'result': 'text-success',
        'material': 'text-info',
        'doubt_reply': 'text-warning',
        'announcement': 'text-danger'
    };
    return colors[type] || 'text-secondary';
}

function formatNotificationTime(timeString) {
    const time = new Date(timeString);
    const now = new Date();
    const diffMs = now - time;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 60) {
        return `${diffMinutes} minutes ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hours ago`;
    } else {
        return time.toLocaleDateString();
    }
}

// Loading States
function initLoadingStates() {
    // Show loading overlay for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingOverlay();
        });
    });
    
    // Show loading for AJAX requests
    const ajaxLinks = document.querySelectorAll('[data-loading]');
    ajaxLinks.forEach(link => {
        link.addEventListener('click', function() {
            showLoadingOverlay();
        });
    });
}

function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('show');
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Form Validation and Enhancement
function initFormValidation() {
    // Add custom validation styles
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.toggle('is-valid', isValid);
    field.classList.toggle('is-invalid', !isValid);
}

// Timetable Enhancement
function initTimetable() {
    const timetableSelect = document.querySelector('select[name="batch"]');
    if (timetableSelect) {
        timetableSelect.addEventListener('change', function() {
            showLoadingOverlay();
            window.location.href = `?batch=${this.value}`;
        });
    }
    
    // Highlight current period
    highlightCurrentPeriod();
    setInterval(highlightCurrentPeriod, 60000); // Update every minute
}

function highlightCurrentPeriod() {
    const now = new Date();
    const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' });
    const currentTime = now.getHours() * 100 + now.getMinutes();
    
    // Period timings (24-hour format as numbers)
    const periods = {
        'Period 1': { start: 830, end: 925 },
        'Period 2': { start: 925, end: 1020 },
        'Break': { start: 1020, end: 1040 },
        'Period 3': { start: 1040, end: 1135 },
        'Period 4': { start: 1135, end: 1230 },
        'Period 5': { start: 1230, end: 1330 },
        'Lunch Break': { start: 1330, end: 1415 }
    };
    
    // Remove previous highlights
    document.querySelectorAll('.current-period').forEach(cell => {
        cell.classList.remove('current-period');
    });
    
    // Find and highlight current period
    Object.entries(periods).forEach(([period, timing]) => {
        if (currentTime >= timing.start && currentTime <= timing.end) {
            const cell = document.querySelector(`[data-day="${currentDay}"][data-period="${period}"]`);
            if (cell) {
                cell.classList.add('current-period');
            }
        }
    });
}

// Attendance Management
function initAttendance() {
    const subjectSelect = document.querySelector('select[name="subject"]');
    if (subjectSelect) {
        subjectSelect.addEventListener('change', function() {
            if (this.value) {
                loadStudentsForSubject(this.value);
            }
        });
    }
    
    // Select All / None functionality
    const selectAllBtn = document.getElementById('selectAll');
    const selectNoneBtn = document.getElementById('selectNone');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="student_"]');
            checkboxes.forEach(cb => cb.checked = true);
        });
    }
    
    if (selectNoneBtn) {
        selectNoneBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="student_"]');
            checkboxes.forEach(cb => cb.checked = false);
        });
    }
}

function loadStudentsForSubject(subjectId) {
    showLoadingOverlay();
    
    fetch(`/api/students-by-subject/?subject_id=${subjectId}`)
        .then(response => response.json())
        .then(data => {
            updateStudentsList(data.students);
            hideLoadingOverlay();
        })
        .catch(error => {
            console.error('Error loading students:', error);
            hideLoadingOverlay();
            showAlert('Error loading students. Please try again.', 'danger');
        });
}

function updateStudentsList(students) {
    const container = document.getElementById('studentsContainer');
    if (!container) return;
    
    if (students.length === 0) {
        container.innerHTML = '<p class="text-muted">No students found for this subject.</p>';
        return;
    }
    
    let html = `
        <div class="mb-3">
            <button type="button" class="btn btn-sm btn-outline-primary me-2" id="selectAll">Select All</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" id="selectNone">Select None</button>
        </div>
        <div class="row">
    `;
    
    students.forEach(student => {
        html += `
            <div class="col-md-6 col-lg-4 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="student${student.id}" " id="student${student.id}">
                    <label class="form-check-label" for="student${student.id}">
                        <strong>${student.id}</strong> - ${student.name}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Reinitialize select all/none buttons
    initAttendance();
}

// Assignment Management
function initAssignments() {
    // File upload enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            if (label && fileName) {
                label.textContent = fileName;
                label.classList.add('file-selected');
            }
        });
    });
    
    // Assignment submission modal
    initSubmissionModal();
}

function initSubmissionModal() {
    const submissionBtns = document.querySelectorAll('.submit-assignment-btn');
    submissionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const assignmentId = this.dataset.assignmentId;
            const assignmentTitle = this.dataset.assignmentTitle;
            showSubmissionModal(assignmentId, assignmentTitle);
        });
    });
}

function showSubmissionModal(assignmentId, assignmentTitle) {
    const modal = document.getElementById('submissionModal');
    if (modal) {
        const titleElement = modal.querySelector('.assignment-title');
        const hiddenInput = modal.querySelector('input[name="assignment_id"]');
        
        if (titleElement) titleElement.textContent = assignmentTitle;
        if (hiddenInput) hiddenInput.value = assignmentId;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.messages-container') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    
    const contentArea = document.querySelector('.content-area');
    if (contentArea && contentArea.firstChild) {
        contentArea.insertBefore(container, contentArea.firstChild);
    }
    
    return container;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('searchQuery');
    if (searchInput) {
        const debouncedSearch = debounce(performSearch, 300);
        searchInput.addEventListener('input', function() {
            debouncedSearch(this.value);
        });
    }
}

function performSearch(query) {
    if (query.length < 2) {
        clearSearchResults();
        return;
    }
    
    // Implementation depends on the current page
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('materials')) {
        searchMaterials(query);
    } else if (currentPage.includes('assignments')) {
        searchAssignments(query);
    }
    // Add more search implementations as needed
}

function clearSearchResults() {
    // Clear search highlighting and show all items
    document.querySelectorAll('.search-hidden').forEach(item => {
        item.classList.remove('search-hidden');
    });
    
    document.querySelectorAll('.search-highlight').forEach(item => {
        item.classList.remove('search-highlight');
    });
}

// Progress tracking
function updateProgress(selector, percentage) {
    const progressBar = document.querySelector(selector);
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
}

// Export functions for global access
window.YenepoyaPortal = {
    showAlert,
    showLoadingOverlay,
    hideLoadingOverlay,
    loadStudentsForSubject,
    updateProgress,
    formatFileSize
};

// Handle page visibility change to pause/resume updates
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause intensive operations when tab is not visible
        console.log('Page hidden - pausing updates');
    } else {
        // Resume operations when tab becomes visible
        console.log('Page visible - resuming updates');
        loadNotifications(); // Refresh notifications
    }
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

