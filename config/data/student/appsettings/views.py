import json

from django.http import JsonResponse
from icecream import ic
from django.views.decorators.csrf import csrf_exempt
from googletrans import Translator
from icecream import ic
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Store, Strike, VersionUpdate
from .serializers import StoresSerializer, StudentAPPSerializer, StudentFinanceSerializer, StrikeSerializer, \
    VersionUpdateSerializer
from ..mastering.models import Mastering
from ...finances.finance.models import Finance
from ...notifications.models import Notification
from ...notifications.serializers import NotificationSerializer
from ...student.student.models import Student


class StoresListView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Store.objects.all()

        filial = self.request.query_params.get('filial', None)

        seen = self.request.query_params.get('seen', None)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if seen:
            queryset = queryset.filter(seen=seen.capitalize())
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class StoreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentAPPSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__id'


class FinanceListView(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = StudentFinanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')

        action = self.request.query_params.get('action', None)
        kind = self.request.query_params.get('kind', None)
        payment_method = self.request.query_params.get('payment_method', None)
        search = self.request.query_params.get('search', None)

        queryset = Finance.objects.all()
        ic(id)
        if id:
            queryset = queryset.filter(student__user__id=id)

        if action:
            queryset = queryset.filter(action=action)

        if kind:
            queryset = queryset.filter(kind__id=kind)

        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        if search:
            queryset = queryset.filter(amount__icontains=search)

        return queryset


class StrikeListView(ListCreateAPIView):
    queryset = Strike.objects.all()
    serializer_class = StrikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        if id:
            return Strike.objects.filter(student__user__id=id)
        return Strike.objects.none()


class VersionUpdateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VersionUpdate.objects.all()
    serializer_class = VersionUpdateSerializer

    def get_queryset(self):
        app_name = self.request.query_params.get('app_name', None)
        if app_name:
            queryset = VersionUpdate.objects.filter(app_name=app_name).first()
            return queryset
        return VersionUpdate.objects.none()


class StudentNotificationsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    pagination_class = None

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        if id:
            return Notification.objects.filter(user__id=id)
        return Notification.objects.none()

    def get_paginated_response(self, data):
        return Response(data)


class StudentAvgAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        student = Student.objects.filter(user=user).first()

        if not student:
            return Response({"error": "Student not found."}, status=404)

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

        course_scores = {}

        for m in mastering_records:
            course = m.theme.course if m.theme and m.theme.course else None
            if not course:
                continue  # skip if course is missing

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

            item = {
                "id": m.id,
                "ball": m.ball,
                "title": m.test.title if m.test else None,
                "created_at": m.created_at,
                "theme": {
                    "id": m.theme.id if m.theme else None,
                    "name": m.theme.title if m.theme else None
                }
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

        def avg(values):
            return round(sum(values) / len(values), 2) if values else 0

        # Calculate overall
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

        # Prepare per-course averages
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

        return Response({
            "student_id": student.id,
            "full_name": f"{student.first_name} {student.last_name}",
            "overall_learning": overall,
            "course_scores": course_results
        })


translator = Translator()


@csrf_exempt
async def flask_translate_proxy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        text = data.get('text')
        src = data.get('source_lang')
        dest = data.get('target_lang')

        print(data, text, src, dest)

        if not text or not src or not dest:
            return JsonResponse({'error': 'Missing text/source_lang/target_lang'}, status=400)

        result = await translator.translate(text, src=src, dest=dest)

        return JsonResponse({
            'translated_text': result.text,
            'source_language': result.src,
            'target_language': result.dest
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
