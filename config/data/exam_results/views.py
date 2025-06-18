from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView

from .models import UnitTest,UnitTestResult
from .serializers import UnitTestSerializer,UnitTestResultSerializer


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