import json

from django.db.models import Q
from django.http import JsonResponse
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
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from .models import Store, Strike, VersionUpdate
from .serializers import StoresSerializer, StudentAPPSerializer, StudentFinanceSerializer, StrikeSerializer, \
    VersionUpdateSerializer
from ..mastering.models import Mastering
from ..student.sms import SayqalSms
from ...finances.finance.models import Finance
from ...notifications.models import Notification
from ...notifications.serializers import NotificationSerializer
from ...parents.models import Relatives
from ...student.student.models import Student


class StoresListView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Store.objects.filter(has_expired=False)

        filial = self.request.GET.get('filial', None)

        seen = self.request.GET.get('seen', None)
        has_expired = self.request.GET.get('has_expired', None)

        if has_expired:
            queryset = queryset.filter(has_expired=has_expired.capitalize())
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

        action = self.request.GET.get('action', None)
        kind = self.request.GET.get('kind', None)
        payment_method = self.request.GET.get('payment_method', None)
        search = self.request.GET.get('search', None)

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
        id = self.request.GET.get('id', None)
        if id:
            return Strike.objects.filter(student__user__id=id)
        return Strike.objects.none()


class VersionUpdateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VersionUpdate.objects.all()
    serializer_class = VersionUpdateSerializer

    def get_queryset(self):
        app_name = self.request.GET.get('app_name', None)
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
        id = self.request.GET.get('id', None)
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
        course_is_language = {}

        for m in mastering_records:
            course = m.theme.course if m.theme and m.theme.course else None
            if not course:
                continue

            course_id = str(course.id)
            if course_id not in course_scores:
                course_is_language[course_id] = course.subject.is_language
                course_scores[course_id] = {
                    "course_name": course.name,
                    "course_id": course.id,
                    "exams": [],
                    "homeworks": [],
                }
                if course.subject.is_language:
                    course_scores[course_id].update({
                        "speaking": [],
                        "unit": [],
                        "mock": [],
                    })

            if m.test and m.test.type == "Offline" and m.choice == "Test":
                overall_scores["exams"].append(m.ball)
                course_scores[course_id]["exams"].append(m.ball)
            elif m.choice == "Speaking" and "speaking" in course_scores[course_id]:
                overall_scores["speaking"].append(m.ball)
                course_scores[course_id]["speaking"].append(m.ball)
            elif m.choice == "Unit_Test" and "unit" in course_scores[course_id]:
                overall_scores["unit"].append(m.ball)
                course_scores[course_id]["unit"].append(m.ball)
            elif m.choice == "Mock" and "mock" in course_scores[course_id]:
                overall_scores["mock"].append(m.ball)
                course_scores[course_id]["mock"].append(m.ball)
            else:
                overall_scores["homeworks"].append(m.ball)
                course_scores[course_id]["homeworks"].append(m.ball)

        def avg(values):
            return round(sum(values) / len(values), 2) if values else 0

        # Calculate global overall (you can adjust logic to exclude non-language categories if needed)
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
        for course_id, c in course_scores.items():
            is_language = course_is_language[course_id]

            course_result = {
                "course_id": c["course_id"],
                "course_name": c["course_name"],
                "exams": avg(c["exams"]),
                "homeworks": avg(c["homeworks"]),
            }

            total_parts = 2  # exams + homeworks
            total_score = course_result["exams"] + course_result["homeworks"]

            if is_language:
                course_result["speaking"] = avg(c["speaking"])
                course_result["unit"] = avg(c["unit"])
                course_result["mock"] = avg(c["mock"])
                total_score += course_result["speaking"] + course_result["unit"] + course_result["mock"]
                total_parts += 3

            course_result["overall"] = round(total_score / total_parts, 2)
            course_results.append(course_result)

        return Response({
            "student_id": student.id,
            "full_name": f"{student.first_name} {student.last_name}",
            "overall_learning": overall,
            "course_scores": course_results,
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
        import traceback
        print(traceback.format_exc())  # Logs the full traceback for debugging
        return JsonResponse({'error': str(e)}, status=500)

sms = SayqalSms()
class SendSmsToStudent(APIView):
    def post(self, request, *args, **kwargs):
        students = request.data.get("students", [])
        message = request.data.get("message", "")

        if not students or not message:
            return JsonResponse(
                {"error": "Missing 'students' list or 'message' text."},
                status=HTTP_400_BAD_REQUEST
            )

        sent_count = 0

        for student in students:
            relatives = Relatives.objects.filter(
                Q(lid__id=student) | Q(student__id=student)
            )
            if not relatives.exists():
                return JsonResponse(
                    {"error": "Parent not found"},
                    status=HTTP_400_BAD_REQUEST
                )

            for relative in relatives:
                if relative.phone:
                    sms.send_sms(relative.phone, message)
                    sent_count += 1

        return JsonResponse(
            {"count": sent_count, "message": "SMS sent successfully."},
            status=HTTP_200_OK
        )



class SendNotifToStudent(APIView):
    def post(self, request, *args, **kwargs):
        students = request.data.get("students", [])
        message = request.data.get("message", "")

        if not students or not message:
            return JsonResponse(
                {"error": "Missing 'students' list or 'message' text."},
                status=HTTP_400_BAD_REQUEST
            )

        sent_count = 0

        for student in students:
            relatives = Relatives.objects.filter(
                Q(lid__id=student) | Q(student__id=student)
            )
            if not relatives.exists():
                return JsonResponse(
                    {"error": "Parent not found"},
                    status=HTTP_400_BAD_REQUEST
                )

            for relative in relatives:
                if relative.user:
                    Notification.objects.create(
                        user=relative.user,
                        comment=message,
                        choice="Admin_Message",
                        come_from="Admin_Message"
                    )
        return JsonResponse(
            {"count": sent_count, "message": "Notifications sent successfully."},
            status=HTTP_200_OK
        )
