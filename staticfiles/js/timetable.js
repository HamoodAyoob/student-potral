// Timetable Specific JavaScript

$(document).ready(function() {
    // Initialize timetable
    initializeTimetable();
    
    // Load current time indicator
    updateCurrentTimeIndicator();
    
    // Update time indicator every minute
    setInterval(updateCurrentTimeIndicator, 60000);
    
    // Add hover effects
    addTimetableHoverEffects();
    
    // Initialize print functionality
    initializePrintTimetable();
});

// Initialize timetable
function initializeTimetable() {
    // Add current day highlighting
    highlightCurrentDay();
    
    // Add current period highlighting
    highlightCurrentPeriod();
    
    // Add subject color coding
    addSubjectColors();
    
    // Initialize responsive behavior
    initializeResponsiveTimetable();
}

// Highlight current day
function highlightCurrentDay() {
    var today = new Date();
    var currentDay = today.toLocaleDateString('en-US', { weekday: 'long' });
    
    // Find and highlight current day column
    $('.timetable th').each(function() {
        if ($(this).text().trim() === currentDay) {
            $(this).addClass('current-day-header');
            
            // Highlight the entire column
            var columnIndex = $(this).index();
            $('.timetable tbody tr').each(function() {
                $(this).find('td').eq(columnIndex).addClass('current-day-cell');
            });
        }
    });
}

// Highlight current period
function highlightCurrentPeriod() {
    var now = new Date();
    var currentTime = now.getHours() * 60 + now.getMinutes();
    
    // Define period times (in minutes from midnight)
    var periods = {
        '1': { start: 8 * 60 + 30, end: 9 * 60 + 25 },    // 8:30 - 9:25
        '2': { start: 9 * 60 + 25, end: 10 * 60 + 20 },   // 9:25 - 10:20
        '3': { start: 10 * 60 + 40, end: 11 * 60 + 35 },  // 10:40 - 11:35
        '4': { start: 11 * 60 + 35, end: 12 * 60 + 30 },  // 11:35 - 12:30
        '5': { start: 12 * 60 + 30, end: 13 * 60 + 30 }   // 12:30 - 1:30
    };
    
    // Check which period is current
    for (var period in periods) {
        if (currentTime >= periods[period].start && currentTime <= periods[period].end) {
            // Highlight current period row
            $('.timetable tbody tr').each(function() {
                var periodHeader = $(this).find('td').first().text().trim();
                if (periodHeader === period || periodHeader.includes(period)) {
                    $(this).addClass('current-period-row');
                    
                    // Add pulsing effect
                    $(this).addClass('pulse-animation');
                }
            });
            break;
        }
    }
}

// Update current time indicator
function updateCurrentTimeIndicator() {
    var now = new Date();
    var timeString = now.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
    
    // Update time display if exists
    if ($('#current-time').length) {
        $('#current-time').text(timeString);
    } else {
        // Add current time display
        $('.timetable-container').prepend(`
            <div class="current-time-display mb-3 text-center">
                <div class="badge bg-primary fs-6 p-3">
                    <i class="fas fa-clock me-2"></i>
                    Current Time: <span id="current-time">${timeString}</span>
                </div>
            </div>
        `);
    }
    
    // Re-highlight current period as time changes
    $('.current-period-row').removeClass('current-period-row pulse-animation');
    highlightCurrentPeriod();
}

// Add subject colors
function addSubjectColors() {
    var subjectColors = {
        'Software Engineering': '#dc3545',
        'Progressive Web Apps': '#28a745',
        'Deep Learning': '#007bff',
        'NLP': '#ffc107',
        'Principles of Virtualization': '#17a2b8',
        'Professional Development': '#6f42c1',
        'Mentorship': '#fd7e14'
    };
    
    $('.timetable-cell').each(function() {
        var cellText = $(this).text().trim();
        
        for (var subject in subjectColors) {
            if (cellText.includes(subject)) {
                $(this).css('border-left', `4px solid ${subjectColors[subject]}`);
                $(this).addClass('subject-cell');
                
                // Add subject icon
                var icon = getSubjectIcon(subject);
                if (!$(this).find('.subject-icon').length) {
                    $(this).prepend(`<div class="subject-icon mb-1">${icon}</div>`);
                }
                break;
            }
        }
        
        // Special handling for breaks and lunch
        if (cellText.toLowerCase().includes('break')) {
            $(this).addClass('break-cell');
            $(this).html('<i class="fas fa-coffee"></i><br>Break');
        } else if (cellText.toLowerCase().includes('lunch')) {
            $(this).addClass('lunch-cell');
            $(this).html('<i class="fas fa-utensils"></i><br>Lunch Break');
        }
    });
}

// Get subject icon
function getSubjectIcon(subject) {
    var icons = {
        'Software Engineering': '<i class="fas fa-code"></i>',
        'Progressive Web Apps': '<i class="fas fa-globe"></i>',
        'Deep Learning': '<i class="fas fa-brain"></i>',
        'NLP': '<i class="fas fa-language"></i>',
        'Principles of Virtualization': '<i class="fas fa-server"></i>',
        'Professional Development': '<i class="fas fa-briefcase"></i>',
        'Mentorship': '<i class="fas fa-user-tie"></i>'
    };
    
    return icons[subject] || '<i class="fas fa-book"></i>';
}

// Add hover effects
function addTimetableHoverEffects() {
    $('.timetable-cell').hover(
        function() {
            // Highlight row and column on hover
            var rowIndex = $(this).parent().index();
            var colIndex = $(this).index();
            
            // Highlight row
            $(this).parent().addClass('hover-row');
            
            // Highlight column
            $('.timetable tbody tr').each(function() {
                $(this).find('td').eq(colIndex).addClass('hover-column');
            });
            
            // Show tooltip with full subject info
            showSubjectTooltip($(this));
        },
        function() {
            // Remove highlights
            $('.hover-row').removeClass('hover-row');
            $('.hover-column').removeClass('hover-column');
            
            // Hide tooltip
            hideSubjectTooltip();
        }
    );
}

// Show subject tooltip
function showSubjectTooltip(element) {
    var cellText = element.text().trim();
    if (cellText && !cellText.includes('Break') && !cellText.includes('Lunch')) {
        var lines = cellText.split('\n');
        var subject = lines[0] || '';
        var teacher = lines[1] || '';
        
        var tooltipContent = `
            <div class="subject-tooltip">
                <strong>${subject}</strong><br>
                <small>Teacher: ${teacher}</small><br>
                <small>Room: LH 5, 3rd Floor</small>
            </div>
        `;
        
        if (!$('.subject-tooltip').length) {
            $('body').append(`<div class="tooltip-container">${tooltipContent}</div>`);
        }
        
        // Position tooltip
        $(document).mousemove(function(e) {
            $('.tooltip-container').css({
                left: e.pageX + 10,
                top: e.pageY + 10,
                display: 'block'
            });
        });
    }
}

// Hide subject tooltip
function hideSubjectTooltip() {
    $('.tooltip-container').remove();
}

// Initialize responsive timetable
function initializeResponsiveTimetable() {
    function adjustTimetableForMobile() {
        if (window.innerWidth < 768) {
            // Convert table to mobile-friendly format
            if (!$('.mobile-timetable').length) {
                createMobileTimetable();
            }
            $('.desktop-timetable').hide();
            $('.mobile-timetable').show();
        } else {
            $('.desktop-timetable').show();
            $('.mobile-timetable').hide();
        }
    }
    
    // Initial check
    adjustTimetableForMobile();
    
    // Check on window resize
    $(window).resize(adjustTimetableForMobile);
}

// Create mobile timetable
function createMobileTimetable() {
    var mobileHtml = '<div class="mobile-timetable">';
    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    days.forEach(function(day) {
        mobileHtml += `
            <div class="mobile-day-schedule mb-4">
                <h5 class="day-header bg-primary text-white p-3 mb-0 rounded-top">
                    <i class="fas fa-calendar-day me-2"></i>${day}
                </h5>
                <div class="periods-container bg-white rounded-bottom shadow-sm">
        `;
        
        // Add periods for this day
        for (var period = 1; period <= 5; period++) {
            var periodTime = getPeriodTime(period);
            var cellContent = getTimetableCellContent(day, period);
            
            if (cellContent) {
                mobileHtml += `
                    <div class="mobile-period-item p-3 border-bottom">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="period-info">
                                <div class="period-time text-muted small mb-1">
                                    Period ${period} • ${periodTime}
                                </div>
                                <div class="period-content">
                                    ${cellContent}
                                </div>
                            </div>
                            <div class="period-status">
                                ${getPeriodStatus(period)}
                            </div>
                        </div>
                    </div>
                `;
            }
        }
        
        mobileHtml += '</div></div>';
    });
    
    mobileHtml += '</div>';
    
    $('.timetable-container').append(mobileHtml);
}

// Get period time
function getPeriodTime(period) {
    var times = {
        1: '8:30 - 9:25',
        2: '9:25 - 10:20',
        3: '10:40 - 11:35',
        4: '11:35 - 12:30',
        5: '12:30 - 1:30'
    };
    return times[period] || '';
}

// Get timetable cell content
function getTimetableCellContent(day, period) {
    // This would normally come from your Django template data
    // For now, returning sample content
    var timetableData = {
        'Monday': {
            1: 'Software Engineering<br>Mrs. Priyanka',
            2: 'Progressive Web Apps<br>Ms. Gunasheela R',
            3: 'Deep Learning<br>Mrs. Ushanandini Balu',
            4: 'Principles of Virtualization<br>Trainer C',
            5: 'NLP<br>Ms. Anjana C'
        },
        // Add other days...
    };
    
    return timetableData[day] && timetableData[day][period] || '';
}

// Get period status
function getPeriodStatus(period) {
    var now = new Date();
    var currentTime = now.getHours() * 60 + now.getMinutes();
    
    var periods = {
        1: { start: 8 * 60 + 30, end: 9 * 60 + 25 },
        2: { start: 9 * 60 + 25, end: 10 * 60 + 20 },
        3: { start: 10 * 60 + 40, end: 11 * 60 + 35 },
        4: { start: 11 * 60 + 35, end: 12 * 60 + 30 },
        5: { start: 12 * 60 + 30, end: 13 * 60 + 30 }
    };
    
    if (periods[period]) {
        if (currentTime < periods[period].start - 30) {
            return '<span class="badge bg-light text-dark">Upcoming</span>';
        } else if (currentTime >= periods[period].start - 30 && currentTime < periods[period].start) {
            return '<span class="badge bg-warning">Starting Soon</span>';
        } else if (currentTime >= periods[period].start && currentTime <= periods[period].end) {
            return '<span class="badge bg-success">In Progress</span>';
        } else {
            return '<span class="badge bg-secondary">Completed</span>';
        }
    }
    
    return '';
}

// Initialize print functionality
function initializePrintTimetable() {
    // Add print button if not exists
    if (!$('#printTimetable').length) {
        $('.timetable-header, .page-header').append(`
            <button id="printTimetable" class="btn btn-outline-primary ms-2">
                <i class="fas fa-print me-1"></i>Print Timetable
            </button>
        `);
    }
    
    $('#printTimetable').on('click', function() {
        printTimetable();
    });
}

// Print timetable
function printTimetable() {
    var printWindow = window.open('', '_blank');
    var timetableHtml = $('.timetable-container').html();
    
    var printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>BCA 5th Semester - Batch 4 Timetable</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .mobile-timetable { display: none !important; }
                .current-time-display { display: none !important; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #000; padding: 10px; text-align: center; }
                th { background-color: #f0f0f0; font-weight: bold; }
                .break-cell { background-color: #f8f9fa; }
                .lunch-cell { background-color: #fff3cd; }
                .current-day-cell, .current-period-row { background-color: #e3f2fd; }
                .subject-icon { display: none; }
                h1 { text-align: center; color: #333; }
                .print-header { text-align: center; margin-bottom: 30px; }
                @media print {
                    body { margin: 0; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h1>BCA 5th Semester - Batch 4</h1>
                <h2>Class Timetable</h2>
                <p>Room: LH 5, 3rd Floor</p>
                <p>Printed on: ${new Date().toLocaleDateString('en-IN')}</p>
            </div>
            ${timetableHtml}
        </body>
        </html>
    `;
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(function() {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// Export timetable as image
function exportTimetableAsImage() {
    // This would require html2canvas library
    // For now, just show message
    showSuccessMessage('Export functionality will be available soon!');
}

// Get next class
function getNextClass() {
    var now = new Date();
    var currentDay = now.toLocaleDateString('en-US', { weekday: 'long' });
    var currentTime = now.getHours() * 60 + now.getMinutes();
    
    var periods = [
        { time: 8 * 60 + 30, label: 'Period 1 (8:30 AM)' },
        { time: 9 * 60 + 25, label: 'Period 2 (9:25 AM)' },
        { time: 10 * 60 + 40, label: 'Period 3 (10:40 AM)' },
        { time: 11 * 60 + 35, label: 'Period 4 (11:35 AM)' },
        { time: 12 * 60 + 30, label: 'Period 5 (12:30 PM)' }
    ];
    
    for (var i = 0; i < periods.length; i++) {
        if (currentTime < periods[i].time) {
            return {
                day: currentDay,
                period: i + 1,
                time: periods[i].label,
                subject: getTimetableCellContent(currentDay, i + 1)
            };
        }
    }
    
    return null;
}

// Show next class notification
function showNextClassNotification() {
    var nextClass = getNextClass();
    
    if (nextClass) {
        var notification = `
            <div class="alert alert-info alert-dismissible fade show next-class-alert" role="alert">
                <i class="fas fa-clock me-2"></i>
                <strong>Next Class:</strong> ${nextClass.subject} at ${nextClass.time}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        if (!$('.next-class-alert').length) {
            $('.timetable-container').prepend(notification);
        }
    }
}

// Initialize notification check
$(document).ready(function() {
    showNextClassNotification();
    
    // Update every 5 minutes
    setInterval(showNextClassNotification, 5 * 60 * 1000);
});

// Timetable search functionality
function initializeTimetableSearch() {
    $('#timetableSearch').on('input', function() {
        var searchTerm = $(this).val().toLowerCase();
        
        $('.timetable-cell').each(function() {
            var cellText = $(this).text().toLowerCase();
            var row = $(this).parent();
            
            if (cellText.includes(searchTerm) || searchTerm === '') {
                $(this).removeClass('search-hidden');
                row.show();
            } else {
                $(this).addClass('search-hidden');
            }
        });
        
        // Hide rows that have all cells hidden
        $('.timetable tbody tr').each(function() {
            var visibleCells = $(this).find('.timetable-cell').not('.search-hidden').length;
            if (visibleCells === 0 && searchTerm !== '') {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });
}

// Add search functionality on ready
$(document).ready(function() {
    if ($('#timetableSearch').length) {
        initializeTimetableSearch();
    }
});