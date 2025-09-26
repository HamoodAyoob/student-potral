# Check in Django shell
from portal.models import Student, Subject, Teacher
teacher = Teacher.objects.get(user__username='your_teacher_username')
subject = Subject.objects.get(id=subject_id, teacher=teacher)
students = Student.objects.filter(semester=subject.semester)
print(f"Subject semester: {subject.semester}")
print(f"Students in that semester: {students.count()}")