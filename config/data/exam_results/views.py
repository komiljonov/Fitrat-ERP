from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UnitTest, UnitTestResult, QuizResult, MockExam, MockExamResult, LevelExam
from .serializers import UnitTestSerializer, UnitTestResultSerializer, QuizResultSerializer, MockExamSerializer, \
    MockExamResultSerializer, LevelExamSerializer
from ..results.models import Results
from ..upload.serializers import FileUploadSerializer


class UnitTestListCreateAPIView(ListCreateAPIView):
    queryset = UnitTest.objects.all()
    serializer_class = UnitTestSerializer

    def get_queryset(self):
        queryset = UnitTest.objects.all()

        group = self.request.GET.get('group')
        theme_after = self.request.GET.get('theme_after')
        quiz = self.request.GET.get('quiz')

        if group:
            queryset = queryset.filter(group__id=group)

        if theme_after:
            queryset = queryset.filter(theme_after__id=theme_after)

        if quiz:
            queryset = queryset.filter(quiz__id=quiz)

        return queryset


class UnitTestRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = UnitTest.objects.all()
    serializer_class = UnitTestSerializer


class UnitTestResultListCreateAPIView(ListCreateAPIView):
    queryset = UnitTestResult.objects.all()
    serializer_class = UnitTestResultSerializer

    def get_queryset(self):
        student = self.request.GET.get('student')
        unit = self.request.GET.get('unit')
        user = self.request.GET.get('user')

        qs = UnitTestResult.objects.all()

        if user:
            qs = qs.filter(student__user__id=user)
        if student:
            qs = qs.filter(student__id=student)
        if unit:
            qs = qs.filter(unit__id=unit)
        return qs


class QuizRestAPIView(ListCreateAPIView):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = QuizResult.objects.all()

        quiz = self.request.GET.get('quiz')
        student = self.request.GET.get('student')
        user = self.request.GET.get('user')

        if user:
            queryset = queryset.filter(student__user__id=user)
        if quiz:
            queryset = queryset.filter(quiz__id=quiz)
        if student:
            queryset = queryset.filter(students__id=student)

        return queryset.order_by("-created_at")

    def get_paginated_response(self, data):
        return Response(data)


class MockExamListCreateAPIView(ListCreateAPIView):
    queryset = MockExam.objects.all()
    serializer_class = MockExamSerializer

    def get_queryset(self):
        queryset = MockExam.objects.all()

        group = self.request.GET.get('group')
        course = self.request.GET.get('course')
        student = self.request.GET.get('student')
        option = self.request.GET.get('option')

        if group:
            queryset = queryset.filter(group__id=group)
        if course:
            queryset = queryset.filter(course__id=course)
        if student:
            queryset = queryset.filter(students__id=student)
        if option:
            queryset = queryset.filter(options__id=option)
        return queryset


class MockExamRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = MockExam.objects.all()
    serializer_class = MockExamSerializer


class MockExamResultListCreateAPIView(ListCreateAPIView):
    queryset = MockExamResult.objects.all()
    serializer_class = MockExamResultSerializer

    def get_queryset(self):
        queryset = MockExamResult.objects.all()

        student = self.request.GET.get('student')
        mock = self.request.GET.get('mock')

        if student:
            queryset = queryset.filter(student__id=student)
        if mock:
            queryset = queryset.filter(mock__id=mock)
        return queryset


class MockExamResultRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = MockExamResult.objects.all()
    serializer_class = MockExamResultSerializer


class StudentsResultsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        student = request.GET.get('student')
        status = request.GET.get('status')
        results = Results.objects.filter(results="Certificate", who="Student")

        fk_name = self.request.GET.get('fk_name')
        if fk_name:
            results = results.filter(result_fk_name__id=fk_name)

        if student:
            results = results.filter(student__id=student)

        if status:
            results = results.filter(status=status)

        results = results.prefetch_related("student", "upload_file")

        # Initialize paginator
        paginator = PageNumberPagination()
        paginator.page_size = 10

        paginated_results = paginator.paginate_queryset(results, request)

        serializer_context = {"request": request, "view": self}
        data = []

        for result in paginated_results:
            file = result.upload_file.first()
            file = FileUploadSerializer(file, context=serializer_context).data if file else None

            data.append({
                "id": result.id,
                "student_id": result.student.id,
                "fk_name": {
                    "id": result.result_fk_name.id,
                    "name": str(result.result_fk_name.name)
                } if result.result_fk_name else None,
                "full_name": f"{result.student.first_name} {result.student.last_name}",
                "student_photo": result.student.photo.url if result.student.photo else None,
                "type": result.results,
                "teacher": result.teacher.full_name if result.teacher else None,
                "status": result.status,
                "point": (
                    result.band_score
                ),
                "file": file
            })

        # Return paginated response
        return paginator.get_paginated_response(data)


class LevelExamListCreateAPIView(ListCreateAPIView):
    queryset = LevelExam.objects.all()
    serializer_class = LevelExamSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = LevelExam.objects.all()

        choice = self.request.GET.get('choice')
        group = self.request.GET.get('group')
        course = self.request.GET.get('course')
        subject = self.request.GET.get('subject')
        filial = self.request.GET.get('filial')

        if filial:
            queryset = queryset.filter(filial__id=filial)
        if choice:
            queryset = queryset.filter(choice=choice)
        if group:
            queryset = queryset.filter(group__id=group)
        if course:
            queryset = queryset.filter(course__id=course)
        if subject:
            queryset = queryset.filter(subject__id=subject)
        return queryset


class LevelExamRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = LevelExam.objects.all()
    serializer_class = LevelExamSerializer
    permission_classes = (IsAuthenticated,)
