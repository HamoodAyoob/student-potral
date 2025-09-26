from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import ValidationError
import pandas as pd
import csv
from io import TextIOWrapper
from .models import *
from .forms import BulkImportForm

# Unregister the default User admin
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Information'

class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Teacher Information'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    
    def get_inlines(self, request, obj):
        inlines = [UserProfileInline]
        if obj and hasattr(obj, 'student'):
            inlines.append(StudentInline)
        elif obj and hasattr(obj, 'teacher'):
            inlines.append(TeacherInline)
        return inlines

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['campus_id', 'get_full_name', 'batch', 'semester', 'registration_number', 'phone']
    list_filter = ['batch', 'semester', 'gender', 'blood_group']
    search_fields = ['campus_id', 'registration_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['campus_id']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('campus_id', 'email', 'registration_number', 'semester', 'batch')
        }),
        ('Personal Information', {
            'fields': ('gender', 'date_of_birth', 'religion', 'caste', 'blood_group')
        }),
        ('Parent Information', {
            'fields': ('father_name', 'mother_name', 'father_phone', 'mother_phone', 'parent_email')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone')
        }),
    )
    
    actions = ['bulk_import_students']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='student_bulk_import'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='student_download_template'),
        ]
        return custom_urls + urls
    
    def download_template(self, request):
        headers = [
            'campus_id', 'registration_number', 'first_name', 'last_name', 'email', 'semester', 'batch', 'gender', 'phone', 'address'
        ]
        csv_content = ",".join(headers) + "\n"
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
        return response
    
    def bulk_import_view(self, request):
        if request.method == 'POST':
            form = BulkImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    self.process_bulk_import(request, form)
                    messages.success(request, 'Bulk import completed successfully!')
                except Exception as e:
                    messages.error(request, f'Error during import: {str(e)}')
                return HttpResponseRedirect(reverse('admin:portal_student_changelist'))
        else:
            form = BulkImportForm()
        
        return render(request, 'admin/bulk_import.html', {
            'form': form,
            'title': 'Bulk Import Students',
            'user_type': 'student'
        })
    
    def process_bulk_import(self, request, form):
        file = form.cleaned_data['file']
        default_password = form.cleaned_data['default_password']
        
        # Read the file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            raise ValidationError('Unsupported file format')
        
        success_count = 0
        error_count = 0
        errors = []

        full_name = str(row['name']).strip()
        if ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        else:
            first_name, last_name = full_name, ''
        
        for index, row in df.iterrows():
            try:
                # Create User
                user = User.objects.create_user(
                    username=row['campus_id'],
                    email=row['email'],
                    password=default_password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    user_type='student',
                    phone=row.get('phone', ''),
                    address=row.get('address', '')
                )
                
                # Create Student
                Student.objects.create(
                    user=user,
                    campus_id=row['campus_id'],
                    registration_number=row['registration_number'],
                    semester=row.get('semester', 5),
                    batch=row.get('batch', 'Batch 4'),
                    address=row.get('address', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', ''),
                )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Log results
        if errors:
            messages.warning(request, f"Import completed with {success_count} successes and {error_count} errors. Errors: {'; '.join(errors[:5])}")
        else:
            messages.success(request, f"Successfully imported {success_count} students")
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_message'] = (
            '<a href="{}?user_type=student">Download Student Import Template</a> | '
            '<a href="{}?user_type=teacher">Download Teacher Import Template</a>'
            ).format(
                reverse('admin:bulkuserimport_download_template'),
                reverse('admin:bulkuserimport_download_template')
            )
        return super().changelist_view(request, extra_context)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'get_full_name', 'department', 'qualification', 'phone']
    list_filter = ['department']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['employee_number']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='teacher_bulk_import'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='student_download_template'),
        ]
        return custom_urls + urls
    
    def download_template(self, request):
        headers = [
            'employee_number', 'first_name', 'last_name', 'email', 'qualification', 'department', 'phone', 'address'
        ]
        csv_content = ",".join(headers) + "\n"
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
        return response
            
    def bulk_import_view(self, request):
        if request.method == 'POST':
            form = BulkImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    self.process_teacher_bulk_import(request, form)
                    messages.success(request, 'Teacher bulk import completed successfully!')
                except Exception as e:
                    messages.error(request, f'Error during import: {str(e)}')
                return HttpResponseRedirect(reverse('admin:portal_teacher_changelist'))
        else:
            form = BulkImportForm()
        
        return render(request, 'admin/bulk_import.html', {
            'form': form,
            'title': 'Bulk Import Teachers',
            'user_type': 'teacher'
        })
    
    def process_teacher_bulk_import(self, request, form):
        file = form.cleaned_data['file']
        default_password = form.cleaned_data['default_password']
        
        # Read the file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            raise ValidationError('Unsupported file format')
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Create User
                user = User.objects.create_user(
                    username=row['employee_number'],
                    email=row['email'],
                    password=default_password,
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                
                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    user_type='teacher',
                    phone=row.get('phone', ''),
                    address=row.get('address', '')
                )
                
                # Create Teacher
                Teacher.objects.create(
                    user=user,
                    employee_number=row['employee_number'],
                    department=row.get('department', 'BCA'),
                    qualification=row['qualification'],
                    phone=row.get('phone', ''),
                    address=row.get('address', '')
                )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 1}: {str(e)}")
        
        if errors:
            messages.warning(request, f"Import completed with {success_count} successes and {error_count} errors. Errors: {'; '.join(errors[:5])}")
        else:
            messages.success(request, f"Successfully imported {success_count} teachers")

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'semester', 'teacher', 'credits']
    list_filter = ['semester', 'teacher']
    search_fields = ['code', 'name']
    ordering = ['semester', 'code']

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ['batch', 'day', 'period', 'subject', 'room']
    list_filter = ['batch', 'day', 'period']
    search_fields = ['batch', 'subject__name']
    ordering = ['batch', 'day', 'period']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter periods to exclude breaks for subject assignment
        if obj and obj.is_break_period():
            form.base_fields['subject'].required = False
        return form

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'period', 'is_present', 'marked_by']
    list_filter = ['date', 'is_present', 'subject', 'period']
    search_fields = ['student__campus_id', 'student__user__first_name', 'subject__name']
    date_hierarchy = 'date'
    ordering = ['-date', 'student']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'due_date', 'max_marks', 'created_at']
    list_filter = ['subject', 'teacher', 'due_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
    ordering = ['-created_at']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'marks', 'is_late']
    list_filter = ['assignment__subject', 'submitted_at', 'is_late', 'marks']
    search_fields = ['assignment__title', 'student__campus_id']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']

@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'subject', 'asked_at', 'is_resolved']
    list_filter = ['subject', 'is_resolved', 'asked_at']
    search_fields = ['title', 'student__campus_id', 'question']
    date_hierarchy = 'asked_at'
    ordering = ['-asked_at']

@admin.register(DoubtReply)
class DoubtReplyAdmin(admin.ModelAdmin):
    list_display = ['doubt', 'teacher', 'replied_at']
    list_filter = ['teacher', 'replied_at']
    search_fields = ['doubt__title', 'reply']
    date_hierarchy = 'replied_at'
    ordering = ['-replied_at']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'material_type', 'uploaded_at', 'is_active']
    list_filter = ['subject', 'teacher', 'material_type', 'uploaded_at', 'is_active']
    search_fields = ['title', 'description']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam_type', 'marks_obtained', 'total_marks', 'grade', 'published_at']
    list_filter = ['subject', 'exam_type', 'grade', 'published_at']
    search_fields = ['student__campus_id', 'student__user__first_name', 'subject__name']
    date_hierarchy = 'published_at'
    ordering = ['-published_at']

@admin.register(HallTicketRequest)
class HallTicketRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_name', 'exam_date', 'status', 'requested_at']
    list_filter = ['status', 'exam_type', 'exam_date']
    search_fields = ['student__campus_id', 'exam_name']
    date_hierarchy = 'requested_at'
    ordering = ['-requested_at']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='approved', processed_at=timezone.now())
        self.message_user(request, f'{updated} hall ticket requests approved.')
    approve_requests.short_description = 'Approve selected requests'
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected', processed_at=timezone.now())
        self.message_user(request, f'{updated} hall ticket requests rejected.')
    reject_requests.short_description = 'Reject selected requests'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'created_at', 'is_active']
    list_filter = ['notification_type', 'created_at', 'is_active', 'batch_filter', 'semester_filter']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    filter_horizontal = ['students', 'teachers']

@admin.register(BulkUserImport)
class BulkUserImportAdmin(admin.ModelAdmin):
    list_display = ['user_type', 'status', 'total_records', 'success_count', 'error_count', 'created_at']
    list_filter = ['user_type', 'status', 'created_at']
    readonly_fields = ['status', 'total_records', 'success_count', 'error_count', 'error_log', 'processed_at']
    ordering = ['-created_at']

    actions = ['process_pending_imports']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download-template/', self.admin_site.admin_view(self.download_template), name='bulkuserimport_download_template'),
        ]
        return custom_urls + urls
    
    def download_template(self, request):
        user_type = request.GET.get('user_type', 'student')
        if user_type == 'teacher':
            headers = ['employee_number', 'name', 'email', 'qualification', 'department', 'phone', 'address']
            filename = 'teacher_import_template.csv'
        else:
            headers = ['campus_id', 'registration_number', 'name', 'email', 'semester', 'batch', 'gender', 'phone', 'address']
            filename = 'student_import_template.csv'
        csv_content = ",".join(headers) + "\n"
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def process_pending_imports(self, request, queryset):
        """Process selected pending imports"""
        processed = 0
        for bulk_import in queryset.filter(status='pending'):
            try:
                # Process the import
                self.process_import(bulk_import)
                processed += 1
            except Exception as e:
                bulk_import.status = 'failed'
                bulk_import.error_log = str(e)
                bulk_import.save()
        
        messages.success(request, f'Successfully processed {processed} import(s)')
    
    process_pending_imports.short_description = 'Process selected pending imports'

    def process_import(self, bulk_import):
        """Process a single bulk import"""
        import pandas as pd
        from django.contrib.auth.models import User
        from portal.models import Student, Teacher, UserProfile
        from django.utils import timezone
        
        bulk_import.status = 'processing'
        bulk_import.save()
        
        try:
            # Read the uploaded file
            if bulk_import.file.name.endswith('.csv'):
                df = pd.read_csv(bulk_import.file.path)
            else:
                df = pd.read_excel(bulk_import.file.path)
            
            bulk_import.total_records = len(df)
            bulk_import.save()
            
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    if bulk_import.user_type == 'student':
                        self.create_student(row, bulk_import.default_password)
                    else:
                        self.create_teacher(row, bulk_import.default_password)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            bulk_import.success_count = success_count
            bulk_import.error_count = error_count
            bulk_import.error_log = '\n'.join(errors) if errors else ''
            bulk_import.status = 'completed'
            bulk_import.processed_at = timezone.now()
            bulk_import.save()
            
        except Exception as e:
            bulk_import.status = 'failed'
            bulk_import.error_log = str(e)
            bulk_import.processed_at = timezone.now()
            bulk_import.save()

    def create_student(self, row, default_password):
        """Create a student from row data"""
        from portal.models import Student, UserProfile

        full_name = str(row['name']).strip()
        if ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        else:
            first_name, last_name = full_name, ''
        
        user = User.objects.create_user(
            username=row['campus_id'],
            email=row['email'],
            password=default_password,
            first_name=first_name,
            last_name=last_name
        )
        
        UserProfile.objects.create(
            user=user,
            user_type='student',
            phone=row.get('phone', ''),
            address=row.get('address', '')
        )
        
        Student.objects.create(
            user=user,
            campus_id=row['campus_id'],
            registration_number=row['registration_number'],
            semester=row.get('semester', 5),
            batch=row.get('batch', 'Batch 4'),
            address=row.get('address', ''),
            phone=row.get('phone', ''),
            email=row.get('email', '')
        )

    def create_teacher(self, row, default_password):
        """Create a teacher from row data"""
        from portal.models import Teacher, UserProfile
        

        full_name = str(row['name']).strip()
        if ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        else:
            first_name, last_name = full_name, ''


        user = User.objects.create_user(
            username=row['employee_number'],
            email=row['email'],
            password=default_password,
            first_name=first_name,
            last_name=last_name
        )
        
        UserProfile.objects.create(
            user=user,
            user_type='teacher',
            phone=row.get('phone', ''),
            address=row.get('address', '')
        )
        
        Teacher.objects.create(
            user=user,
            employee_number=row['employee_number'],
            department=row.get('department', 'BCA'),
            qualification=row['qualification'],
            phone=row.get('phone', ''),
            address=row.get('address', ''),
            email=row.get('email', '')
        )



# Custom admin site configuration
admin.site.site_header = 'Yenepoya Portal Administration'
admin.site.site_title = 'Yenepoya Portal Admin'
admin.site.index_title = 'Welcome to Yenepoya Portal Administration'