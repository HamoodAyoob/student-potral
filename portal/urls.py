from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('timetable/', views.timetable, name='timetable'),
    path('attendance/', views.attendance, name='attendance'),
    path('api/students-by-subject/', views.get_students_by_subject, name='get_students_by_subject'),
    path('doubt_clearance/', views.doubt_clearance, name='doubt_clearance'),
    path('materials/', views.materials, name='materials'),
    path('materials/delete/<int:material_id>/', views.delete_material, name='delete_material'),
    path('hall_ticket/', views.hall_ticket, name='hall_ticket'),
    path('manage-hall-tickets/', views.manage_hall_tickets, name='manage_hall_tickets'),
    path('download-hall-ticket/<int:request_id>/', views.download_hall_ticket, name='download_hall_ticket'),
    path('generate-hall-ticket/<int:request_id>/', views.generate_hall_ticket_bulk, name='generate_hall_ticket_bulk'),
    path('exam_results/', views.exam_results, name='exam_results'),
    path('fees_management/', views.fees_management, name='fees_management'),

    # AJAX endpoints
    path('api/notifications/', views.get_notifications, name='api_notifications'),
    path('api/students-by-subject/', views.get_students_by_subject, name='api_students_by_subject'),
]