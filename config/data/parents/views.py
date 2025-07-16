from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Relatives
from .serializers import RelativesSerializer
from ..notifications.models import Notification
from ..notifications.serializers import NotificationSerializer
from ..student.course.models import Course
from ..student.mastering.models import Mastering
from ..student.student.models import Student
from ..student.studentgroup.models import StudentGroup


# Create your views here.

class ParentListView(ListCreateAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.GET.get('user')

        queryset = Relatives.objects.all()

        if user:
            queryset = self.queryset.filter(user__id=user)
        return queryset


class ParentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]


class RelativesListNoPGView(ListAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class StudentsRelativesListView(ListAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        queryset = Relatives.objects.filter(Q(student__id=id) | Q(lid__id=id))
        return queryset


class ParentsStudentsAPIView(APIView):
    queryset = Relatives.objects.all()

    def get(self, request):

        phone = request.GET.get('phone')
        id = self.kwargs.get('pk')
        user = self.request.GET.get('user')

        students = Relatives.objects.all()

        if user:
            queryset = self.queryset.filter(user__id=user)
        if phone:
            students = students.filter(phone=phone)
        if id:
            students = students.filter(id=id)
        students_data = []
        if students:

            for student in students:
                students_data.append({
                    'id': student.student.id,
                    'full_name': f"{student.student.first_name} {student.student.last_name}",
                    "phone": student.student.phone,
                    "balance": student.student.balance,
                })
        return Response(students_data, status=status.HTTP_200_OK)


class ParentsNotificationsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__id'


class ParentRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__id'



class ParentStudentAvgAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        students = []

        if user.role == "Student":
            student = Student.objects.filter(user=user).first()
            if student:
                students = [student]

        elif user.role == "Parents":
            student_ids = Relatives.objects.filter(user=user).values_list("student", flat=True)
            students = Student.objects.filter(id__in=student_ids)

        if not students:
            return Response({"error": "Student(s) not found."}, status=404)

        def avg(values):
            return round(sum(values) / len(values), 2) if values else 0

        response_data = []

        for student in students:
            # 🔹 Get course IDs the student is enrolled in
            course_ids = (
                StudentGroup.objects
                .filter(student=student)
                .values_list("group__course_id", flat=True)
                .distinct()
            )

            # 🔹 Prepare course map for fast access
            course_map = {
                str(course.id): {
                    "course_id": course.id,
                    "course_name": course.name,
                    "exams": [],
                    "homeworks": [],
                    "speaking": [],
                    "unit": [],
                    "mock": [],
                }
                for course in Course.objects.filter(id__in=course_ids)
            }

            # 🔹 Filter Mastering records for student and those course themes only
            mastering_records = (
                Mastering.objects
                .filter(student=student)
                .select_related("test", "theme", "theme__course")
            )

            overall_scores = {
                "exams": [],
                "homeworks": [],
                "speaking": [],
                "unit": [],
                "mock": [],
            }

            for m in mastering_records:
                course = m.theme.course
                course_id = str(course.id)

                if course_id not in course_map:
                    continue  # skip unexpected records

                if m.test and m.test.type == "Offline" and m.choice == "Test":
                    overall_scores["exams"].append(m.ball)
                    course_map[course_id]["exams"].append(m.ball)
                elif m.choice == "Speaking":
                    overall_scores["speaking"].append(m.ball)
                    course_map[course_id]["speaking"].append(m.ball)
                elif m.choice == "Unit_Test":
                    overall_scores["unit"].append(m.ball)
                    course_map[course_id]["unit"].append(m.ball)
                elif m.choice == "Mock":
                    overall_scores["mock"].append(m.ball)
                    course_map[course_id]["mock"].append(m.ball)
                else:
                    overall_scores["homeworks"].append(m.ball)
                    course_map[course_id]["homeworks"].append(m.ball)

            overall = round(
                sum(avg(overall_scores[key]) for key in overall_scores) / 5,
                2
            )

            course_results = []
            for c in course_map.values():
                course_avg = {
                    "course_id": c["course_id"],
                    "course_name": c["course_name"],
                    "exams": avg(c["exams"]),
                    "homeworks": avg(c["homeworks"]),
                    "speaking": avg(c["speaking"]),
                    "unit": avg(c["unit"]),
                    "mock": avg(c["mock"]),
                }
                course_avg["overall"] = round(
                    sum(course_avg[k] for k in ["exams", "homeworks", "speaking", "unit", "mock"]) / 5,
                    2
                )
                course_results.append(course_avg)

            response_data.append({
                "student_id": student.id,
                "full_name": f"{student.first_name} {student.last_name}",
                "phone": student.phone,
                "balance": student.balance,
                "overall_learning": overall,
                "course_scores": course_results
            })

        return Response(response_data)


