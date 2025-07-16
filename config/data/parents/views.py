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
            related_students = Relatives.objects.filter(user=user).values_list("student", flat=True)
            students = Student.objects.filter(id__in=related_students)

        if not students:
            return Response({"error": "Student(s) not found."}, status=404)

        def avg(values):
            return round(sum(values) / len(values), 2) if values else 0

        response_data = []

        for student in students:
            mastering_records = (
                Mastering.objects.filter(student=student)
                .select_related("test", "theme", "theme__course")
            )

            overall_scores = {
                "exams": [],
                "homeworks": [],
                "speaking": [],
                "unit": [],
                "mock": [],
            }

            course_scores = StudentGroup.objects.filter(student=student).values_list("group__course", flat=True)

            for m in mastering_records:
                course = m.theme.course if m.theme and m.theme.course else None
                if not course:
                    continue

                course_id = str(course.id)
                if course_id not in course_scores:
                    course_scores[course_id] = {
                        "course_name": course.name,
                        "course_id": course.id,
                        "exams": [],
                        "homeworks": [],
                        "speaking": [],
                        "unit": [],
                        "mock": [],
                    }

                if m.test and m.test.type == "Offline" and m.choice == "Test":
                    overall_scores["exams"].append(m.ball)
                    course_scores[course_id]["exams"].append(m.ball)
                elif m.choice == "Speaking":
                    overall_scores["speaking"].append(m.ball)
                    course_scores[course_id]["speaking"].append(m.ball)
                elif m.choice == "Unit_Test":
                    overall_scores["unit"].append(m.ball)
                    course_scores[course_id]["unit"].append(m.ball)
                elif m.choice == "Mock":
                    overall_scores["mock"].append(m.ball)
                    course_scores[course_id]["mock"].append(m.ball)
                else:
                    overall_scores["homeworks"].append(m.ball)
                    course_scores[course_id]["homeworks"].append(m.ball)

            overall = round(
                (
                        avg(overall_scores["exams"]) +
                        avg(overall_scores["homeworks"]) +
                        avg(overall_scores["speaking"]) +
                        avg(overall_scores["unit"]) +
                        avg(overall_scores["mock"])
                ) / 5,
                2,
            )

            course_results = []
            for c in course_scores.values():
                course_results.append({
                    "course_id": c["course_id"],
                    "course_name": c["course_name"],
                    "exams": avg(c["exams"]),
                    "homeworks": avg(c["homeworks"]),
                    "speaking": avg(c["speaking"]),
                    "unit": avg(c["unit"]),
                    "mock": avg(c["mock"]),
                    "overall": round(
                        (
                                avg(c["exams"]) +
                                avg(c["homeworks"]) +
                                avg(c["speaking"]) +
                                avg(c["unit"]) +
                                avg(c["mock"])
                        ) / 5,
                        2,
                    )
                })

            response_data.append({
                "student_id": student.id,
                "full_name": f"{student.first_name} {student.last_name}",
                "phone": student.phone,
                "balance": student.balance,
                "overall_learning": overall,
                "course_scores": course_results
            })

        return Response(response_data)
