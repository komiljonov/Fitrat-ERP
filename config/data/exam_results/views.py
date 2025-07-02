from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView

from .models import UnitTest, UnitTestResult, QuizResult, MockExam, MockExamResult
from .serializers import UnitTestSerializer, UnitTestResultSerializer, QuizResultSerializer, MockExamSerializer, \
    MockExamResultSerializer


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

    def get_queryset(self):
        queryset = QuizResult.objects.all()

        quiz = self.request.GET.get('quiz')
        student = self.request.GET.get('student')
        if quiz:
            queryset = queryset.filter(quiz__id=quiz)

        if student:
            queryset = queryset.filter(students__id=student)

        return queryset


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
