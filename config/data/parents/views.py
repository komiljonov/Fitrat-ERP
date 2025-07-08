from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Relatives
from .serializers import RelativesSerializer


# Create your views here.

class ParentListView(ListCreateAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]



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

        students = Relatives.objects.all()

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
                    "phone" : student.student.phone,
                    "balance": student.student.balance,
                })
        return Response(students_data, status=status.HTTP_200_OK)