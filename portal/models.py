from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.safestring import mark_safe
import uuid

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    BATCH_CHOICES = [
        ('Batch 1', 'Batch 1'),
        ('Batch 2', 'Batch 2'),
        ('Batch 3', 'Batch 3'),
        ('Batch 4', 'Batch 4'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    campus_id = models.CharField(max_length=20, unique=True)
    registration_number = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(8)])
    batch = models.CharField(max_length=10, choices=BATCH_CHOICES, default='Batch 4')
    
    # Personal Information
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True)
    caste = models.CharField(max_length=50, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Parent Information
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    father_phone = models.CharField(max_length=15, blank=True)
    mother_phone = models.CharField(max_length=15, blank=True)
    parent_email = models.EmailField(blank=True)
    
    # Contact Information
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"{self.campus_id} - {self.user.get_full_name()}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    employee_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, default='BCA')
    qualification = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.employee_number} - {self.user.get_full_name()}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='subjects')
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=4)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TimeTable(models.Model):
    DAYS_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    
    PERIOD_CHOICES = [
        ('Period 1', '8:30 - 9:25'),
        ('Period 2', '9:25 - 10:20'),
        ('Break', '10:20 - 10:40'),
        ('Period 3', '10:40 - 11:35'),
        ('Period 4', '11:35 - 12:30'),
        ('Period 5', '12:30 - 1:30'),
        ('Lunch Break', '1:30 - 2:15'),
    ]
    
    batch = models.CharField(max_length=10, choices=Student.BATCH_CHOICES)
    day = models.CharField(max_length=10, choices=DAYS_CHOICES)
    period = models.CharField(max_length=15, choices=PERIOD_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    room = models.CharField(max_length=20, default='LH 5, 3rd Floor', blank=True)
    
    class Meta:
        unique_together = ['batch', 'day', 'period']
        ordering = ['day', 'period']
    
    def __str__(self):
        return f"{self.batch} - {self.day} - {self.period}"
        
    def is_break_period(self):
        return self.period in ['Break', 'Lunch Break']

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    period = models.CharField(max_length=15, choices=TimeTable.PERIOD_CHOICES)
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'date', 'period']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.campus_id} - {self.subject.name} - {self.date} - {status}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    question_file = models.FileField(upload_to='assignments/questions', blank=True, null=True)
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.title}"
    
    def is_overdue(self):
        return timezone.now() > self.due_date

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer_file = models.FileField(upload_to='assignments/submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def save(self, *args, **kwargs):
        if not self.pk and self.assignment.is_overdue():
            self.is_late = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.campus_id} - {self.assignment.title}"

class Doubt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='doubts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    question = models.TextField()
    asked_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.campus_id} - {self.title}"

class DoubtReply(models.Model):
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='replies')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    reply = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mark doubt as resolved when teacher replies
        self.doubt.is_resolved = True
        self.doubt.save()
    
    def __str__(self):
        return f"Reply to: {self.doubt.title}"

class Material(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('notes', 'Notes'),
        ('question_bank', 'Question Bank'),
        ('reference', 'Reference Material'),
        ('slides', 'Slides'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    description = models.TextField()
    file = models.FileField(upload_to='materials/')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.title}"

class ExamResult(models.Model):
    EXAM_TYPE_CHOICES = [
        ('internal_1', 'Internal Assessment 1'),
        ('internal_2', 'Internal Assessment 2'),
        ('internal_3', 'Internal Assessment 3'),
        ('semester', 'Semester End Exam'),
        ('assignment', 'Assignment'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=2, blank=True)
    published_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'exam_type']
    
    def save(self, *args, **kwargs):
        # Auto-calculate grade
        percentage = (float(self.marks_obtained) / float(self.total_marks)) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        elif percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.campus_id} - {self.subject.name} - {self.get_exam_type_display()} - {self.grade}"

class HallTicketRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hall_tickets')
    exam_name = models.CharField(max_length=100)
    exam_date = models.DateField()
    exam_type = models.CharField(max_length=20, choices=ExamResult.EXAM_TYPE_CHOICES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.campus_id} - {self.exam_name} - {self.status}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'New Assignment'),
        ('result', 'Result Published'),
        ('material', 'New Material'),
        ('announcement', 'Announcement'),
        ('doubt_reply', 'Doubt Reply'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Recipients
    students = models.ManyToManyField(Student, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    batch_filter = models.CharField(max_length=10, choices=Student.BATCH_CHOICES, blank=True)
    semester_filter = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class BulkUserImport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    file = models.FileField(upload_to='bulk_imports/',
                            help_text=mark_safe(
                                '''
                                <a href="/admin/portal/bulkuserimport/download-template/?user_type=student"
                                class="button"
                                style="margin-bottom:1em;margin-top:0.5em;display:inline-block;"
                                target="_blank">Download Student Template</a>
                                <a href="/admin/portal/bulkuserimport/download-template/?user_type=teacher"
                                class="button"
                                style="margin-bottom:1em;margin-left:0.5em;display:inline-block;"
                                target="_blank">Download Teacher Template</a>
                                '''
                            )
    )
    user_type = models.CharField(max_length=10, choices=UserProfile.USER_TYPE_CHOICES)
    default_password = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    total_records = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    
    def __str__(self):
        return f"Bulk Import - {self.user_type} - {self.status}"