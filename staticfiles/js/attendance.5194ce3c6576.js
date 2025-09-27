document.addEventListener('DOMContentLoaded', function() {
    const loadStudentsBtn = document.getElementById('loadStudentsBtn');
    const subjectSelect = document.querySelector('select[name="subject"]');
    const studentsSection = document.getElementById('studentsSection');
    const submitSection = document.getElementById('submitSection');
    const attendanceForm = document.getElementById('attendanceForm');
    
    // Initialize circle progress for student view
    initCircleProgress();
    
    if (loadStudentsBtn) {
        loadStudentsBtn.addEventListener('click', loadStudents);
    }
    
    function loadStudents() {
        const subjectId = subjectSelect.value;
        const date = document.querySelector('input[name="date"]').value;
        const period = document.querySelector('select[name="period"]').value;
        
        if (!subjectId || !date || !period) {
            alert('Please fill in all fields before loading students.');
            return;
        }
        
        showLoadingOverlay();
        
        fetch(`/api/students-by-subject/?subject_id=${subjectId}`)
            .then(response => response.json())
            .then(data => {
                displayStudents(data.students);
                studentsSection.style.display = 'block';
                submitSection.style.display = 'block';
                hideLoadingOverlay();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading students. Please try again.');
                hideLoadingOverlay();
            });
    }
    
    function displayStudents(students) {
        const container = document.getElementById('studentsContainer');
        
        if (students.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-users fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No students found for this subject.</p>
                </div>
            `;
            return;
        }
        
        // Sort students by registration_number instead of campus_id
        students.sort((a, b) => {
            const regA = a.registration_number || '';
            const regB = b.registration_number || '';
            return regA.localeCompare(regB);
        });
        
        let html = '<div class="students-grid">';
        
        students.forEach(student => {
            html += `
                <div class="student-item" data-student-id="${student.id}">
                    <div class="student-info">
                        <div class="student-details">
                            <h6>${student.name}</h6>
                            <div class="student-id">
                                <span class="registration-number">${student.registration_number || 'N/A'}</span>
                                <span class="registration-separator">•</span>
                                <span class="campus-id">${student.campus_id}</span>
                            </div>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input attendance-checkbox" 
                                   type="checkbox" 
                                   name="student${student.id}" 
                                   id="student${student.id}"
                                   value="on"
                                   onchange="updateStudentItemStyle(this)">
                            <label class="form-check-label" for="student${student.id}">
                                Present
                            </label>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        // Initialize select all/none buttons
        initializeAttendanceControls();
        
        // Add debug info
        console.log('Students loaded:', students.length);
        console.log('Sample student object:', students[0]);
    }
    
    function initializeAttendanceControls() {
        const selectAllBtn = document.getElementById('selectAllBtn');
        const selectNoneBtn = document.getElementById('selectNoneBtn');
        
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', function() {
                const checkboxes = document.querySelectorAll('.attendance-checkbox');
                checkboxes.forEach(cb => {
                    cb.checked = true;
                    updateStudentItemStyle(cb);
                });
                console.log('Selected all students');
            });
        }
        
        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', function() {
                const checkboxes = document.querySelectorAll('.attendance-checkbox');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    updateStudentItemStyle(cb);
                });
                console.log('Deselected all students');
            });
        }
    }
    
    window.updateStudentItemStyle = function(checkbox) {
        const studentItem = checkbox.closest('.student-item');
        const studentId = studentItem.getAttribute('data-student-id');
        
        if (checkbox.checked) {
            studentItem.classList.add('present');
            studentItem.classList.remove('absent');
            console.log(`Student ${studentId} marked as PRESENT`);
        } else {
            studentItem.classList.add('absent');
            studentItem.classList.remove('present');
            console.log(`Student ${studentId} marked as ABSENT`);
        }
    };
    
    function initCircleProgress() {
        const circles = document.querySelectorAll('.circle-progress');
        circles.forEach(circle => {
            const percentage = parseFloat(circle.dataset.percentage);
            const degrees = (percentage / 100) * 360;
            
            let color = '#ef4444'; // red
            if (percentage >= 75) color = '#10b981'; // green
            else if (percentage >= 60) color = '#f59e0b'; // yellow
            
            circle.style.setProperty('--progress-deg', degrees + 'deg');
            circle.style.setProperty('--progress-color', color);
        });
    }
    
    // Cancel button functionality
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            studentsSection.style.display = 'none';
            submitSection.style.display = 'none';
        });
    }
    
    // Form submission with debugging
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', function(e) {
            const formData = new FormData(attendanceForm);
            
            // Debug: Log form data
            console.log('Form submission data:');
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }
            
            // Count selected students
            const checkedBoxes = document.querySelectorAll('.attendance-checkbox:checked');
            console.log(`Submitting attendance for ${checkedBoxes.length} present students`);
            
            // Verify checkbox names - now using registration numbers
            checkedBoxes.forEach(cb => {
                console.log(`Checkbox name: ${cb.name}, value: ${cb.value}, checked: ${cb.checked}`);
            });
            
            showLoadingOverlay();
        });
    }
});

// Helper functions
function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}