from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Results
# Create your views here.
from .serializers import UniversityResultsSerializer, CertificationResultsSerializer, StudentResultsSerializer, \
    OtherResultsSerializer, ResultsSerializer, NationalSerializer


class UniversityResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        teacher = self.request.user
        status = self.request.query_params.get('status')

        queryset = Results.objects.all()

        if teacher:
            queryset = Results.objects.filter(teacher=teacher)

        if status:
            queryset = queryset.filter(status=status)
        return queryset


class CertificationResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset


class UniversityResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]


class CertificationResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]


class UniversityResultsNoPg(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class CertificationResultsNoPg(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)

    def get_paginated_response(self, data):
        return Response(data)


class ResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = StudentResultsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,SearchFilter)
    search_fields = ["student__fist_name", "student__last_name","teacher__full_name"]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.GET.get('status')
        type = self.request.GET.get('type')
        filial = self.request.GET.get('filial')
        teacher = self.request.GET.get('teacher')
        results = self.request.GET.get('results')
        nations = self.request.GET.get('nations')
        res_name = self.request.GET.get('res_name')
        who = self.request.GET.get('who')
        university_type = self.request.GET.get('university_type')
        university_entering_type = self.request.GET.get('university_entering_type')
        degree = self.request.GET.get('degree')
        level = self.request.GET.get('level')

        if level:
            queryset = queryset.filter(level=level)
        if degree:
            queryset = queryset.filter(degree=degree)
        if university_type:
            queryset = queryset.filter(university_type=university_type)
        if university_entering_type:
            queryset = queryset.filter(university_entering_type=university_entering_type)
        if who:
            queryset = queryset.filter(who=who)
        if res_name:
            queryset = queryset.filter(result_fk_name__id=res_name)
        if nations:
            queryset = queryset.filter(nations__id=nations)
        if results:
            queryset = queryset.filter(results=results)
        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(results=type)
        if filial:
            queryset = queryset.filter(filial__id__in=filial)
        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        return queryset

class OtherResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = OtherResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.GET.get('status')
        results = self.request.GET.get('results')
        degree = self.request.GET.get('degree')

        if results:
            queryset = queryset.filter(results=results)
        if degree:
            queryset = queryset.filter(degree=degree)

        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.GET.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class OtherResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = OtherResultsSerializer
    permission_classes = [IsAuthenticated]


class ResultsView(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(filial__in=self.request.user.filial.all())
        status = self.request.query_params.get('status')
        type = self.request.query_params.get('type')
        filial = self.request.query_params.get('filial')
        teacher = self.request.query_params.get('teacher')
        results = self.request.GET.get('results')
        nations = self.request.GET.get('nations')
        res_name = self.request.GET.get('res_name')
        who = self.request.GET.get('who')

        if who:
            queryset = queryset.filter(who=who)
        if res_name:
            queryset = queryset.filter(result_fk_name__id=res_name)
        if nations:
            queryset = queryset.filter(nations__id=nations)
        if results:
            queryset = queryset.filter(results=results)
        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(results=type)
        if filial:
            queryset = queryset.filter(filial__id__in=filial)
        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        return queryset


class ResultsRetrieveAPIView(RetrieveUpdateAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    permission_classes = [IsAuthenticated]



class NationalSertificateApi(ListCreateAPIView):
    serializer_class = NationalSerializer
    permission_classes = [IsAuthenticated]
    queryset = Results.objects.all()

    def get_queryset(self):
        queryset = Results.objects.filter(filial__in=self.request.user.filial.all())
        status = self.request.query_params.get('status')
        type = self.request.query_params.get('type')

        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(results=type)
        return queryset


class ResultStudentListAPIView(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = StudentResultsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):

        student = self.request.query_params.get('id')
        status = self.request.query_params.get('status')
        type = self.request.query_params.get('type')
        filial = self.request.query_params.get('filial')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = Results.objects.all()


        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date,created_at__lte=end_date)
        if filial:
            queryset = Results.objects.filter(filial__id=filial)
        if student:
            queryset = queryset.filter(student__id=student)

        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(results=type)
        return queryset
