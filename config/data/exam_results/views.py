from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView

from .models import UnitTest, UnitTestResult, QuizResult
from .serializers import UnitTestSerializer, UnitTestResultSerializer, QuizResultSerializer


class UnitTestListCreateAPIView(ListCreateAPIView):
    queryset = UnitTest.objects.all()
    serializer_class = UnitTestSerializer

    def get_queryset(self):
        queryset = UnitTest.objects.all()

        theme_after = self.request.GET.get('theme_after')
        quiz = self.request.GET.get('quiz')

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