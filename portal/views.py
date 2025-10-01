from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
from .models import *
from .forms import *

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            campus_id = form.cleaned_data['campus_id']
            password = form.cleaned_data['password']
            
            # Try to find student or teacher by campus_id/employee_number
            user = None
            try:
                # Check if it's a student
                student = Student.objects.get(campus_id=campus_id)
                user = authenticate(request, username=student.user.username, password=password)
            except Student.DoesNotExist:
                try:
                    # Check if it's a teacher
                    teacher = Teacher.objects.get(employee_number=campus_id)
                    user = authenticate(request, username=teacher.user.username, password=password)
                except Teacher.DoesNotExist:
                    messages.error(request, 'Invalid credentials. Please check your Campus ID/Employee Number and password.')
                    return render(request, 'login.html', {'form': form})
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials. Please check your Campus ID/Employee Number and password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'current_time': timezone.now(),
    }
    
    if hasattr(request.user, 'student'):
        # Student dashboard
        student = request.user.student
        
        # Get attendance summary
        attendance_records = Attendance.objects.filter(student=student)
        total_classes = attendance_records.count()
        present_classes = Attendance.objects.filter(student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get pending assignments
        pending_assignments = Assignment.objects.filter(
            subject__semester=student.semester,
            due_date__gte=timezone.now()
        ).exclude(submissions__student=student)
        
        # Get unresolved doubts
        unresolved_doubts = Doubt.objects.filter(student=student, is_resolved=False).count()
        
        # Get recent materials
        recent_materials = Material.objects.filter(
            subject__semester=student.semester,
            is_active=True
        ).order_by('-uploaded_at')[:5]
        
        # Get recent results
        recent_results = ExamResult.objects.filter(student=student).order_by('-published_at')[:3]
        
        context.update({
            'is_student': True,
            'student': student,
            'attendance_percentage': round(attendance_percentage, 1),
            'pending_assignments': pending_assignments,
            'pending_assignments_count': pending_assignments.count(),
            'unresolved_doubts': unresolved_doubts,
            'recent_materials': recent_materials,
            'recent_results': recent_results,
        })
        
    elif hasattr(request.user, 'teacher'):
        # Teacher dashboard
        teacher = request.user.teacher
        subjects = Subject.objects.filter(teacher=teacher)
        
        # Get pending doubts
        pending_doubts = Doubt.objects.filter(subject__teacher=teacher, is_resolved=False).count()
        
        # Get recent assignments
        recent_assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')[:5]
        
        # Get recent submissions
        recent_submissions = AssignmentSubmission.objects.filter(
            assignment__teacher=teacher
        ).order_by('-submitted_at')[:5]
        
        context.update({
            'is_teacher': True,
            'teacher': teacher,
            'subjects': subjects,
            'subjects_count': subjects.count(),
            'pending_doubts': pending_doubts,
            'recent_assignments': recent_assignments,
            'recent_submissions': recent_submissions,
        })
    
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    if hasattr(request.user, 'student'):
        if request.method == 'POST':
            form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.student, user=request.user)
            if form.is_valid():
                # Update user fields
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.save()
                
                # Update student fields
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        else:
            form = ProfileUpdateForm(instance=request.user.student, user=request.user)
        
        return render(request, 'profile.html', {'form': form, 'is_student': True})
    
    elif hasattr(request.user, 'teacher'):
        if request.method == 'POST':
            form = TeacherProfileUpdateForm(request.POST, instance=request.user.teacher, user=request.user)
            if form.is_valid():
                # Update user fields
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.save()
                
                # Update teacher fields
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        else:
            form = TeacherProfileUpdateForm(instance=request.user.teacher, user=request.user)
        
        return render(request, 'profile.html', {'form': form, 'is_teacher': True})

@login_required
def timetable(request):
    if hasattr(request.user, 'student'):
        batch = request.user.student.batch
    else:
        batch = request.GET.get('batch', 'Batch 4')
    
    # Get timetable data for the specific batch
    timetable_entries = TimeTable.objects.filter(batch=batch).select_related('subject')
    
    # Organize timetable data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = ['Period 1', 'Period 2', 'Break', 'Period 3', 'Period 4', 'Period 5', 'Lunch Break']
    
    timetable = {}
    for day in days:
        timetable[day] = {}
        for period in periods:
            try:
                entry = timetable_entries.get(day=day, period=period)
                timetable[day][period] = entry
            except TimeTable.DoesNotExist:
                timetable[day][period] = None
    
    # Get available batches for filter
    available_batches = TimeTable.objects.values_list('batch', flat=True).distinct()
    
    context = {
        'timetable': timetable,
        'days': days,
        'periods': periods,
        'current_batch': batch,
        'available_batches': available_batches,
        'is_student': hasattr(request.user, 'student'),
    }
    
    return render(request, 'timetable.html', context)

@login_required
def attendance(request):
    if hasattr(request.user, 'student'):
        # Student attendance view
        student = request.user.student
        subjects = Subject.objects.filter(semester=student.semester)
        
        attendance_data = []
        for subject in subjects:
            total = Attendance.objects.filter(student=student, subject=subject).count()
            present = Attendance.objects.filter(student=student, subject=subject, is_present=True).count()
            percentage = (present / total * 100) if total > 0 else 0
            
            attendance_data.append({
                'subject': subject,
                'total': total,
                'present': present,
                'percentage': round(percentage, 1)
            })
        
        # Get recent attendance records
        recent_attendance = Attendance.objects.filter(student=student).order_by('-date', '-period')[:20]
        
        context = {
            'is_student': True,
            'attendance_data': attendance_data,
            'recent_attendance': recent_attendance,
        }
        
    else:
        # Teacher attendance marking
        teacher = request.user.teacher
        subjects = Subject.objects.filter(teacher=teacher)
        
        if request.method == 'POST':
            form = AttendanceForm(request.POST)
            form.fields['subject'].queryset = subjects
            
            if form.is_valid():
                date = form.cleaned_data['date']
                subject = form.cleaned_data['subject']
                period = form.cleaned_data['period']
                
                # Get all students for the semester - ORDERED BY REGISTRATION NUMBER
                students = Student.objects.filter(semester=subject.semester).order_by('registration_number')
                
                for student in students:
                    # CHANGED: Use registration_number instead of campus_id
                    checkbox_name = f"student{student.id}"
                    is_present = checkbox_name in request.POST
                    
                    # Update or create attendance record
                    Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=date,
                        period=period,
                        defaults={
                            'is_present': is_present,
                            'marked_by': teacher
                        }
                    )
                
                messages.success(request, f'Attendance marked successfully for {subject.name} on {date}')
                return redirect('attendance')
        else:
            form = AttendanceForm()
            form.fields['subject'].queryset = subjects
        
        # Get students for selected subject - ORDERED BY REGISTRATION NUMBER
        selected_subject_id = request.GET.get('subject')
        students = []
        if selected_subject_id:
            try:
                subject = Subject.objects.get(id=selected_subject_id, teacher=teacher)
                students = Student.objects.filter(semester=subject.semester).order_by('registration_number')
            except Subject.DoesNotExist:
                pass
        
        context = {
            'is_teacher': True,
            'form': form,
            'subjects': subjects,
            'students': students,
            'selected_subject_id': selected_subject_id,
        }
    
    return render(request, 'attendance.html', context)

@login_required
def assignments(request):
    if hasattr(request.user, 'student'):
        # Student assignments view
        student = request.user.student
        assignments = Assignment.objects.filter(
            subject__semester=student.semester
        ).order_by('-due_date')
        
        # Check submission status for each assignment
        for assignment in assignments:
            try:
                assignment.submission = AssignmentSubmission.objects.get(
                    assignment=assignment, student=student
                )
                assignment.is_submitted = True
            except AssignmentSubmission.DoesNotExist:
                assignment.is_submitted = False
                assignment.submission = None
        
        if request.method == 'POST':
            assignment_id = request.POST.get('assignment_id')
            assignment = get_object_or_404(Assignment, id=assignment_id)
            
            form = AssignmentSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission, created = AssignmentSubmission.objects.get_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={'answer_file': form.cleaned_data['answer_file']}
                )
                
                if not created:
                    submission.answer_file = form.cleaned_data['answer_file']
                    submission.submitted_at = timezone.now()
                    submission.save()
                
                messages.success(request, 'Assignment submitted successfully!')
                return redirect('assignments')
        
        context = {
            'is_student': True,
            'assignments': assignments,
        }
        
    else:
        # Teacher assignments management
        teacher = request.user.teacher
        
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES)
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
            
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.teacher = teacher
                assignment.save()
                messages.success(request, 'Assignment created successfully!')
                return redirect('assignments')
        else:
            form = AssignmentForm()
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
        
        assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
        
        # Get submission statistics
        for assignment in assignments:
            total_students = Student.objects.filter(semester=assignment.subject.semester).count()
            submitted_count = assignment.submissions.count()
            assignment.submission_stats = {
                'total': total_students,
                'submitted': submitted_count,
                'pending': total_students - submitted_count
            }
        
        context = {
            'is_teacher': True,
            'form': form,
            'assignments': assignments,
        }
    
    return render(request, 'assignments.html', context)

@login_required
def doubt_clearance(request):
    if hasattr(request.user, 'student'):
        # Student doubt posting
        student = request.user.student
        
        if request.method == 'POST':
            form = DoubtForm(request.POST)
            form.fields['subject'].queryset = Subject.objects.filter(semester=student.semester)
            
            if form.is_valid():
                doubt = form.save(commit=False)
                doubt.student = student
                doubt.save()
                messages.success(request, 'Your doubt has been posted successfully!')
                return redirect('doubt_clearance')
        else:
            form = DoubtForm()
            form.fields['subject'].queryset = Subject.objects.filter(semester=student.semester)
        
        doubts = Doubt.objects.filter(student=student).order_by('-asked_at')
        
        context = {
            'is_student': True,
            'form': form,
            'doubts': doubts,
        }
        
    else:
        # Teacher doubt resolution
        teacher = request.user.teacher
        
        if request.method == 'POST':
            doubt_id = request.POST.get('doubt_id')
            doubt = get_object_or_404(Doubt, id=doubt_id, subject__teacher=teacher)
            
            form = DoubtReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.doubt = doubt
                reply.teacher = teacher
                reply.save()
                messages.success(request, 'Reply posted successfully!')
                return redirect('doubt_clearance')
        
        doubts = Doubt.objects.filter(subject__teacher=teacher).order_by('is_resolved', '-asked_at')
        
        context = {
            'is_teacher': True,
            'doubts': doubts,
        }
    
    return render(request, 'doubt_clearance.html', context)

@login_required
def materials(request):
    if hasattr(request.user, 'student'):
        # Student materials view
        student = request.user.student

        print("""student semester: {student.semester}""")
        materials = Material.objects.filter(
            subject__semester=student.semester,
            is_active=True
        ).order_by('-uploaded_at')
        
        # Group materials by type
        notes = materials.filter(material_type='notes')
        question_banks = materials.filter(material_type='question_bank')
        references = materials.filter(material_type='reference')
        slides = materials.filter(material_type='slides')
        
        context = {
            'is_student': True,
            'notes': notes,
            'question_banks': question_banks,
            'references': references,
            'slides': slides,
        }
        
    else:
        # Teacher materials management
        teacher = request.user.teacher
        
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
            
            if form.is_valid():
                material = form.save(commit=False)
                material.teacher = teacher
                material.save()
                messages.success(request, 'Material uploaded successfully!')
                return redirect('materials')
        else:
            form = MaterialForm()
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
        
        materials = Material.objects.filter(teacher=teacher).order_by('-uploaded_at')
        
        context = {
            'is_teacher': True,
            'form': form,
            'notes': materials,
        }
    
    return render(request, 'materials.html', context)

@login_required
def delete_material(request, material_id):
    """Delete material - only teachers can delete their own materials"""
    if not hasattr(request.user, 'teacher'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        material = Material.objects.get(id=material_id, teacher=request.user.teacher)
        material_title = material.title
        
        # Delete the file from storage if it exists
        if material.file:
            material.file.delete(save=False)
        
        material.delete()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True, 'message': f'Material "{material_title}" deleted successfully!'})
        else:
            messages.success(request, f'Material "{material_title}" deleted successfully!')
            return redirect('materials')
            
    except Material.DoesNotExist:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'error': 'Material not found or access denied'}, status=404)
        else:
            messages.error(request, 'Material not found or access denied.')
            return redirect('materials')


@login_required
def hall_ticket(request):
    # Only students can access hall tickets
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Access denied. Only students can request hall tickets.')
        return redirect('dashboard')
    
    student = request.user.student
    
    if request.method == 'POST':
        form = HallTicketRequestForm(request.POST)
        if form.is_valid():
            hall_ticket = form.save(commit=False)
            hall_ticket.student = student
            hall_ticket.save()
            messages.success(request, 'Hall ticket request submitted successfully!')
            return redirect('hall_ticket')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = HallTicketRequestForm()
    
    requests = HallTicketRequest.objects.filter(student=student).order_by('-requested_at')
    
    context = {
        'form': form,
        'requests': requests,
    }
    
    return render(request, 'hall_ticket.html', context)


@login_required
def manage_hall_tickets(request):
    """Teacher view to manage hall ticket requests"""
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied. Only teachers can access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        ticket_request = get_object_or_404(HallTicketRequest, id=request_id)
        ticket_request.status = action
        ticket_request.remarks = remarks
        ticket_request.processed_by = request.user.teacher
        ticket_request.processed_at = timezone.now()
        ticket_request.save()
        
        messages.success(request, f'Hall ticket request {action} successfully!')
        return redirect('manage_hall_tickets')
    
    # Get all requests
    all_requests = HallTicketRequest.objects.all().select_related('student__user').order_by('-requested_at')
    
    # Calculate counts
    pending_count = all_requests.filter(status='pending').count()
    approved_count = all_requests.filter(status='approved').count()
    rejected_count = all_requests.filter(status='rejected').count()
    
    context = {
        'is_teacher': True,
        'requests': all_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'manage_hall_tickets.html', context)

@login_required
def download_hall_ticket(request, request_id):
    """Generate and download hall ticket PDF for approved requests"""
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get the hall ticket request
    ticket_request = get_object_or_404(
        HallTicketRequest,
        id=request_id,
        student=request.user.student,
        status='approved'
    )
    
    student = ticket_request.student
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hall_ticket_{student.campus_id}.pdf"'
    
    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Set up the page
    y_position = height - 50
    
    # Header - University Name
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y_position, "YENEPOYA")
    y_position -= 20
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, y_position, "(Deemed to be University)")
    y_position -= 15
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, y_position, "University Road, Deralakatte, Mangalore - 575018")
    y_position -= 30
    
    # Institution Name
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y_position, "Name of the institution: Yenepoya Institute of Arts Science Commerce & Management Campus B")
    y_position -= 30
    
    # Exam Title
    exam_title = f"{student.semester} Semester BCA - Examination - {ticket_request.exam_date.strftime('%B %Y')}"
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, y_position, exam_title)
    y_position -= 40
    
    # Student Details Section
    p.setFont("Helvetica-Bold", 11)
    left_margin = 50
    
    # Registration Number
    p.drawString(left_margin, y_position, f"Reg No: {student.registration_number}")
    y_position -= 20
    
    # Name
    p.drawString(left_margin, y_position, f"Name: {student.user.get_full_name()}")
    y_position -= 20
    
    # Gender
    gender_display = student.get_gender_display() if student.gender else "Not Specified"
    p.drawString(left_margin, y_position, f"Gender: {gender_display}")
    y_position -= 20
    
    # Campus ID
    p.drawString(left_margin, y_position, f"Campus ID: {student.campus_id}")
    y_position -= 40
    
    # Subjects Table
    # Get subjects for the student's semester
    subjects = Subject.objects.filter(semester=student.semester).order_by('code')
    
    # Create table data
    table_data = [
        ['Paper Code', 'Subject/Paper Name', 'Invigilator Sign']
    ]
    
    for subject in subjects:
        table_data.append([
            subject.code,
            f"{subject.name} - [Theory]",
            '.'
        ])
    
    # Create the table
    table = Table(table_data, colWidths=[1.5*inch, 4*inch, 1.5*inch])
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Draw the table
    table.wrapOn(p, width, height)
    table.drawOn(p, left_margin, y_position - len(table_data) * 25)
    
    # Move y_position down past the table
    y_position -= (len(table_data) * 25 + 60)
    
    # Footer Section
    p.setFont("Helvetica", 10)
    
    # Signature line for candidate
    p.drawString(left_margin, y_position, "Signature of the Candidate:")
    p.line(left_margin + 160, y_position, left_margin + 300, y_position)
    
    # Controller of Examination
    p.drawString(width - 250, y_position, "Controller of Examination,")
    y_position -= 15
    p.drawString(width - 250, y_position, "Yenepoya (Deemed to be University)")
    
    # Add a note at the bottom
    y_position = 50
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, y_position, 
                        f"Generated on: {timezone.now().strftime('%d-%m-%Y %I:%M %p')}")
    
    # Finalize the PDF
    p.showPage()
    p.save()
    
    return response


@login_required
def generate_hall_ticket_bulk(request, request_id):
    """Teacher view to generate hall ticket PDF for a student"""
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get the hall ticket request
    ticket_request = get_object_or_404(
        HallTicketRequest,
        id=request_id,
        status='approved'
    )
    
    student = ticket_request.student
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="hall_ticket_{student.campus_id}.pdf"'
    
    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Set up the page
    y_position = height - 50
    
    # Header - University Name
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y_position, "YENEPOYA")
    y_position -= 20
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, y_position, "(Deemed to be University)")
    y_position -= 15
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, y_position, "University Road, Deralakatte, Mangalore - 575018")
    y_position -= 30
    
    # Institution Name
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y_position, "Name of the institution: Yenepoya Institute of Arts Science Commerce & Management Campus B")
    y_position -= 30
    
    # Exam Title
    exam_title = f"{student.semester} Semester BCA - Examination - {ticket_request.exam_date.strftime('%B %Y')}"
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, y_position, exam_title)
    y_position -= 40
    
    # Student Details Section
    p.setFont("Helvetica-Bold", 11)
    left_margin = 50
    
    # Registration Number
    p.drawString(left_margin, y_position, f"Reg No: {student.registration_number}")
    y_position -= 20
    
    # Name
    p.drawString(left_margin, y_position, f"Name: {student.user.get_full_name()}")
    y_position -= 20
    
    # Gender
    gender_display = student.get_gender_display() if student.gender else "Not Specified"
    p.drawString(left_margin, y_position, f"Gender: {gender_display}")
    y_position -= 20
    
    # Campus ID
    p.drawString(left_margin, y_position, f"Campus ID: {student.campus_id}")
    y_position -= 40
    
    # Subjects Table
    subjects = Subject.objects.filter(semester=student.semester).order_by('code')
    
    # Create table data
    table_data = [
        ['Paper Code', 'Subject/Paper Name', 'Invigilator Sign']
    ]
    
    for subject in subjects:
        table_data.append([
            subject.code,
            f"{subject.name} - [Theory]",
            '.'
        ])
    
    # Create the table
    table = Table(table_data, colWidths=[1.5*inch, 4*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Draw the table
    table.wrapOn(p, width, height)
    table.drawOn(p, left_margin, y_position - len(table_data) * 25)
    
    # Move y_position down past the table
    y_position -= (len(table_data) * 25 + 60)
    
    # Footer Section
    p.setFont("Helvetica", 10)
    
    # Signature line for candidate
    p.drawString(left_margin, y_position, "Signature of the Candidate:")
    p.line(left_margin + 160, y_position, left_margin + 300, y_position)
    
    # Controller of Examination
    p.drawString(width - 250, y_position, "Controller of Examination,")
    y_position -= 15
    p.drawString(width - 250, y_position, "Yenepoya (Deemed to be University)")
    
    # Add a note at the bottom
    y_position = 50
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, y_position, 
                        f"Generated on: {timezone.now().strftime('%d-%m-%Y %I:%M %p')}")
    
    # Finalize the PDF
    p.showPage()
    p.save()
    
    return response

@login_required
def exam_results(request):
    if hasattr(request.user, 'student'):
        # Student results view
        student = request.user.student
        results = ExamResult.objects.filter(student=student).order_by('-published_at')
        
        # Group results by subject
        subjects = {}
        for result in results:
            if result.subject.name not in subjects:
                subjects[result.subject.name] = []
            subjects[result.subject.name].append(result)
        
        # Calculate overall statistics
        total_results = results.count()
        avg_percentage = 0
        if total_results > 0:
            total_percentage = sum((float(r.marks_obtained) / float(r.total_marks)) * 100 for r in results)
            avg_percentage = round(total_percentage / total_results, 1)
        
        context = {
            'is_student': True,
            'results': results,
            'subjects': subjects,
            'total_results': total_results,
            'avg_percentage': avg_percentage,
        }
        
    else:
        # Teacher results management
        teacher = request.user.teacher
        
        if request.method == 'POST':
            form = ExamResultForm(request.POST)
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
            form.fields['student'].queryset = Student.objects.filter(
                semester__in=Subject.objects.filter(teacher=teacher).values_list('semester', flat=True)
            )
            
            if form.is_valid():
                result = form.save(commit=False)
                result.published_by = teacher
                result.save()
                messages.success(request, 'Result published successfully!')
                return redirect('exam_results')
        else:
            form = ExamResultForm()
            form.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
            form.fields['student'].queryset = Student.objects.filter(
                semester__in=Subject.objects.filter(teacher=teacher).values_list('semester', flat=True)
            )
        
        results = ExamResult.objects.filter(published_by=teacher).order_by('-published_at')
        
        context = {
            'is_teacher': True,
            'form': form,
            'results': results,
        }
    
    return render(request, 'exam_results.html', context)

@login_required
def fees_management(request):
    # Under construction page
    context = {
        'is_student': hasattr(request.user, 'student'),
        'is_teacher': hasattr(request.user, 'teacher'),
    }
    return render(request, 'fees_management.html', context)

# AJAX Views for real-time features

@login_required
def get_notifications(request):
    """Get notifications for the current user"""
    notifications = []
    
    if hasattr(request.user, 'student'):
        student = request.user.student
        
        # Get recent assignments
        recent_assignments = Assignment.objects.filter(
            subject__semester=student.semester,
            created_at__gte=timezone.now() - timedelta(days=7)
        )[:3]
        
        for assignment in recent_assignments:
            notifications.append({
                'title': f'New Assignment: {assignment.title}',
                'message': f'Subject: {assignment.subject.name}',
                'type': 'assignment',
                'time': assignment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-tasks',
                'color': 'primary'
            })
        
        # Get recent results
        recent_results = ExamResult.objects.filter(
            student=student,
            published_at__gte=timezone.now() - timedelta(days=7)
        )[:3]
        
        for result in recent_results:
            notifications.append({
                'title': f'Result Published: {result.subject.name}',
                'message': f'Grade: {result.grade}',
                'type': 'result',
                'time': result.published_at.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-chart-bar',
                'color': 'success'
            })
        
        # Get recent materials
        recent_materials = Material.objects.filter(
            subject__semester=student.semester,
            uploaded_at__gte=timezone.now() - timedelta(days=7)
        )[:3]
        
        for material in recent_materials:
            notifications.append({
                'title': f'New Material: {material.title}',
                'message': f'Subject: {material.subject.name}',
                'type': 'material',
                'time': material.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-book',
                'color': 'info'
            })
        
        # Get doubt replies
        recent_replies = DoubtReply.objects.filter(
            doubt__student=student,
            replied_at__gte=timezone.now() - timedelta(days=7)
        )[:3]
        
        for reply in recent_replies:
            notifications.append({
                'title': f'Doubt Replied: {reply.doubt.title}',
                'message': f'Teacher: {reply.teacher.user.get_full_name()}',
                'type': 'doubt_reply',
                'time': reply.replied_at.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-reply',
                'color': 'warning'
            })
    
    elif hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        
        # Get recent doubts
        recent_doubts = Doubt.objects.filter(
            subject__teacher=teacher,
            is_resolved=False,
            asked_at__gte=timezone.now() - timedelta(days=7)
        )[:5]
        
        for doubt in recent_doubts:
            notifications.append({
                'title': f'New Doubt: {doubt.title}',
                'message': f'From: {doubt.student.user.get_full_name()}',
                'type': 'doubt',
                'time': doubt.asked_at.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-question-circle',
                'color': 'warning'
            })
    
    # Sort by time (newest first)
    notifications.sort(key=lambda x: x['time'], reverse=True)
    
    return JsonResponse({'notifications': notifications[:10]})

@login_required
def get_students_by_subject(request):
    """AJAX view to get students for a specific subject (for attendance marking)"""
    subject_id = request.GET.get('subject_id')
    
    if not subject_id or not hasattr(request.user, 'teacher'):
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        subject = Subject.objects.get(id=subject_id, teacher=request.user.teacher)
        # CHANGED: Order by registration_number instead of campus_id
        students = Student.objects.filter(semester=subject.semester).order_by('registration_number')
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'campus_id': student.campus_id,
                'registration_number': student.registration_number,
                'name': student.user.get_full_name(),
            })
        
        return JsonResponse({'students': students_data})
        
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)
    
@login_required
def assignment_submissions(request, assignment_id):
    """View assignment submissions for teachers"""
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user.teacher)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    # Get all students for this semester to show who hasn't submitted
    all_students = Student.objects.filter(semester=assignment.subject.semester)
    submitted_students = submissions.values_list('student_id', flat=True)
    pending_students = all_students.exclude(id__in=submitted_students)
    
    if request.method == 'POST':
        # Handle grading
        submission_id = request.POST.get('submission_id')
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback')
        
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        submission.marks = marks
        submission.feedback = feedback
        submission.save()
        
        messages.success(request, 'Submission graded successfully!')
        return redirect('assignment_submissions', assignment_id=assignment_id)
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'pending_students': pending_students,
        'total_students': all_students.count(),
        'submitted_count': submissions.count(),
    }
    
    return render(request, 'assignment_submissions.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

# Error handlers
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)