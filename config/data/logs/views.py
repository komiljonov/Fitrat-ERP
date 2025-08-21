from datetime import timedelta

from rest_framework.generics import ListAPIView

from .models import Log
from .serializers import LogSerializer


# Create your views here.


class LogListView(ListAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_queryset(self):
        queryset = Log.objects.all()

        app = self.request.GET.get('app')
        model = self.request.GET.get('model')
        action = self.request.GET.get('action')
        model_action = self.request.GET.get('model_action')
        finance = self.request.GET.get('finance')
        lid = self.request.GET.get('lid')
        first_lessons = self.request.GET.get('first_lessons')
        student = self.request.GET.get('student')
        archive = self.request.GET.get('archive')
        account = self.request.GET.get('account')

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date:
            queryset = queryset.filter(
                start_date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                start_date__gte=start_date, end_date__lte=end_date + timedelta(days=1)
            )

        if app:
            queryset = queryset.filter(app=app)

        if model:
            queryset = queryset.filter(model=model)

        if action:
            queryset = queryset.filter(action=action)

        if model_action:
            queryset = queryset.filter(model_action=model_action)

        if finance:
            queryset = queryset.filter(
                finance__id=finance
            )

        if lid:
            queryset = queryset.filter(
                lid__id=lid
            )

        if first_lessons:
            queryset = queryset.filter(
                first_lessons__id=first_lessons
            )

        if student:
            queryset = queryset.filter(
                student__id=student
            )

        if archive:
            queryset = queryset.filter(
                Q(lid__id=archive) | Q(student__id=archive)
            )

        if account:
            queryset = queryset.filter(
                account__id=account
            )

        return queryset
