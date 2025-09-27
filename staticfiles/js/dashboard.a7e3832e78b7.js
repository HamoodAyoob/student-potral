// Dashboard Specific JavaScript

$(document).ready(function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Load today's classes
    loadTodaysClasses();
    
    // Initialize stats counters
    initializeStatsCounters();
    
    // Load recent activities
    loadRecentActivities();
    
    // Initialize attendance chart
    initializeAttendanceChart();
});

// Initialize dashboard
function initializeDashboard() {
    // Animate cards on load
    $('.dashboard-card').each(function(index) {
        $(this).delay(index * 100).animate({
            opacity: 1,
            transform: 'translateY(0)'
        }, 500);
    });
    
    // Add hover effects to subject cards
    $('.subject-card').hover(
        function() {
            $(this).find('i').addClass('animated-icon');
        },
        function() {
            $(this).find('i').removeClass('animated-icon');
        }
    );
}

// Load today's classes
function loadTodaysClasses() {
    var today = new Date();
    var dayName = today.toLocaleDateString('en-US', { weekday: 'long' });
    var todayContainer = $('#todayClasses');
    var teacherContainer = $('#teacherSchedule');
    
    // Mock timetable data - in production, this would come from an API
    var timetable = {
        'Monday': [
            { time: '8:30-9:25', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'Principles of Virtualization', teacher: 'Trainer C', room: 'LH 5, 3rd Floor' },
            { time: '12:30-1:30', subject: 'NLP', teacher: 'Ms. Anjana C', room: 'LH 5, 3rd Floor' }
        ],
        'Tuesday': [
            { time: '8:30-9:25', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Principles of Virtualization', teacher: 'Trainer C', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'NLP', teacher: 'Ms. Anjana C', room: 'LH 5, 3rd Floor' },
            { time: '12:30-1:30', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' }
        ],
        'Wednesday': [
            { time: '8:30-9:25', subject: 'Professional Development', teacher: 'Amritha', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Principles of Virtualization', teacher: 'Trainer C', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' },
            { time: '12:30-1:30', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' }
        ],
        'Thursday': [
            { time: '8:30-9:25', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Professional Development', teacher: 'Amritha', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' },
            { time: '12:30-1:30', subject: 'Principles of Virtualization', teacher: 'Trainer C', room: 'LH 5, 3rd Floor' }
        ],
        'Friday': [
            { time: '8:30-9:25', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Professional Development', teacher: 'Amritha', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' }
        ],
        'Saturday': [
            { time: '8:30-9:25', subject: 'NLP', teacher: 'Ms. Anjana C', room: 'LH 5, 3rd Floor' },
            { time: '9:25-10:20', subject: 'Software Engineering', teacher: 'Mrs. Priyanka', room: 'LH 5, 3rd Floor' },
            { time: '10:40-11:35', subject: 'Progressive Web Apps', teacher: 'Ms. Gunasheela R', room: 'LH 5, 3rd Floor' },
            { time: '11:35-12:30', subject: 'Deep Learning', teacher: 'Mrs. Ushanandini Balu', room: 'LH 5, 3rd Floor' },
            { time: '12:30-1:30', subject: 'Mentorship', teacher: '', room: 'LH 5, 3rd Floor' }
        ]
    };
    
    var todaysClasses = timetable[dayName] || [];
    var currentTime = new Date();
    var currentHour = currentTime.getHours();
    var currentMinute = currentTime.getMinutes();
    var currentTimeInMinutes = currentHour * 60 + currentMinute;
    
    if (todaysClasses.length > 0) {
        var classesHtml = '';
        
        todaysClasses.forEach(function(classItem, index) {
            var startTime = classItem.time.split('-')[0];
            var startHour = parseInt(startTime.split(':')[0]);
            var startMinute = parseInt(startTime.split(':')[1]);
            var startTimeInMinutes = startHour * 60 + startMinute;
            
            var status = '';
            var statusClass = '';
            
            if (currentTimeInMinutes < startTimeInMinutes - 30) {
                status = 'Upcoming';
                statusClass = 'text-info';
            } else if (currentTimeInMinutes >= startTimeInMinutes - 30 && currentTimeInMinutes < startTimeInMinutes) {
                status = 'Starting Soon';
                statusClass = 'text-warning';
            } else if (currentTimeInMinutes >= startTimeInMinutes && currentTimeInMinutes < startTimeInMinutes + 55) {
                status = 'In Progress';
                statusClass = 'text-success';
            } else {
                status = 'Completed';
                statusClass = 'text-muted';
            }
            
            classesHtml += `
                <div class="todays-class mb-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="class-subject">${classItem.subject}</div>
                            <div class="class-teacher">${classItem.teacher}</div>
                            <small class="text-muted">${classItem.room}</small>
                        </div>
                        <div class="text-end">
                            <span class="class-time">${classItem.time}</span>
                            <div class="mt-1">
                                <small class="${statusClass}">${status}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (todayContainer.length) {
            todayContainer.html(classesHtml);
        }
        
        if (teacherContainer.length) {
            teacherContainer.html(classesHtml);
        }
    } else {
        var noClassHtml = '<p class="text-muted text-center">No classes scheduled for today</p>';
        
        if (todayContainer.length) {
            todayContainer.html(noClassHtml);
        }
        
        if (teacherContainer.length) {
            teacherContainer.html(noClassHtml);
        }
    }
}

// Initialize stats counters
function initializeStatsCounters() {
    // Counter animation for dashboard stats
    $('.dashboard-card h3').each(function() {
        var $this = $(this);
        var countTo = parseFloat($this.text());
        
        if (!isNaN(countTo)) {
            $this.text('0');
            
            $({ countNum: 0 }).animate({
                countNum: countTo
            }, {
                duration: 2000,
                easing: 'swing',
                step: function() {
                    if ($this.text().includes('%')) {
                        $this.text(Math.floor(this.countNum) + '%');
                    } else {
                        $this.text(Math.floor(this.countNum));
                    }
                },
                complete: function() {
                    if ($this.text().includes('%')) {
                        $this.text(countTo + '%');
                    } else {
                        $this.text(countTo);
                    }
                }
            });
        }
    });
}

// Load recent activities
function loadRecentActivities() {
    // Mock recent activities data
    var recentActivities = [
        {
            type: 'assignment',
            title: 'Software Engineering Assignment submitted',
            time: '2 hours ago',
            icon: 'fas fa-tasks',
            color: 'success'
        },
        {
            type: 'note',
            title: 'New Deep Learning notes uploaded',
            time: '4 hours ago',
            icon: 'fas fa-book',
            color: 'info'
        },
        {
            type: 'result',
            title: 'NLP Mid-term results published',
            time: '1 day ago',
            icon: 'fas fa-chart-bar',
            color: 'warning'
        },
        {
            type: 'doubt',
            title: 'Doubt about PWA resolved',
            time: '2 days ago',
            icon: 'fas fa-question-circle',
            color: 'primary'
        }
    ];
    
    var activitiesContainer = $('#recentActivities');
    if (activitiesContainer.length) {
        var activitiesHtml = '';
        
        recentActivities.forEach(function(activity) {
            activitiesHtml += `
                <div class="recent-activity-item">
                    <div class="d-flex align-items-center">
                        <div class="me-3">
                            <i class="${activity.icon} text-${activity.color}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">${activity.title}</div>
                            <small class="text-muted">${activity.time}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        activitiesContainer.html(activitiesHtml);
    }
}

// Initialize attendance chart
function initializeAttendanceChart() {
    var attendanceElement = document.querySelector('.attendance-circle');
    if (attendanceElement) {
        var percentage = parseFloat(attendanceElement.getAttribute('data-percentage')) || 0;
        var circle = attendanceElement.querySelector('.circle-progress');
        
        if (circle) {
            var radius = circle.r.baseVal.value;
            var circumference = radius * 2 * Math.PI;
            
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = circumference;
            
            // Animate the circle
            setTimeout(function() {
                var offset = circumference - (percentage / 100) * circumference;
                circle.style.strokeDashoffset = offset;
            }, 500);
        }
    }
}

// Refresh dashboard data
function refreshDashboard() {
    showLoading('.dashboard-content');
    
    // Simulate API call
    setTimeout(function() {
        hideLoading('.dashboard-content');
        loadTodaysClasses();
        loadRecentActivities();
        showSuccessMessage('Dashboard refreshed successfully');
    }, 1000);
}

// Export dashboard data
function exportDashboardData() {
    // Mock data for export
    var data = {
        student: {
            name: 'Current User',
            rollNumber: 'BCA123',
            semester: '5th',
            batch: 'Batch 4'
        },
        attendance: {
            percentage: 85.5,
            totalClasses: 120,
            presentClasses: 102
        },
        assignments: {
            total: 15,
            submitted: 12,
            pending: 3
        },
        subjects: [
            'Software Engineering',
            'Progressive Web Apps',
            'Deep Learning',
            'NLP',
            'Principles of Virtualization',
            'Professional Development'
        ]
    };
    
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "dashboard_data.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

// Print dashboard
function printDashboard() {
    window.print();
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialize dark mode from localStorage
$(document).ready(function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});

// Add click handlers for quick actions
$(document).ready(function() {
    // Refresh button
    $(document).on('click', '[data-action="refresh"]', function() {
        refreshDashboard();
    });
    
    // Export button
    $(document).on('click', '[data-action="export"]', function() {
        exportDashboardData();
    });
    
    // Print button
    $(document).on('click', '[data-action="print"]', function() {
        printDashboard();
    });
    
    // Dark mode toggle
    $(document).on('click', '[data-action="dark-mode"]', function() {
        toggleDarkMode();
    });
});