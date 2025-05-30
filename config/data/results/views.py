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

    def validate(self, attrs):
        """Main validation method"""
        # Call parent validation first
        attrs = super().validate(attrs)

        # Only validate if we have an instance with required fields
        if not (self.instance and self.instance.result_fk_name and
                self.instance.point and self.instance.who):
            return attrs

        try:
            # Check if ResultName exists
            result_name = ResultName.objects.filter(
                id=self.instance.result_fk_name.id,
                who=self.instance.who,
            ).first()

            if not result_name:
                raise serializers.ValidationError(
                    "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
                )

            # Get subject based on point type
            point_type = self.instance.point.point_type
            band_score = self.instance.band_score
            subject = None

            base_query = ResultSubjects.objects.filter(
                asos__name__icontains="ASOS_4",
                result=self.instance.point,
                result_type=self.instance.who,
            )

            if point_type in ["Percentage", "Ball"] and band_score is not None:
                subject = base_query.filter(from_point__lte=band_score).first()

            elif point_type == "Degree" and band_score:
                subject = base_query.filter(from_point__icontains=band_score).first()

            if not subject:
                raise serializers.ValidationError(
                    "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
                )

        except (AttributeError, ValueError, TypeError):
            raise serializers.ValidationError(
                "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
            )

        return attrs

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
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        if certification_type and status:
            queryset = queryset.filter(status=status, certificate_type=certification_type)
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
