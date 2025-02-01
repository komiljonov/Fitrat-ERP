from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.


from .serializers import ParentSerializer
from .models import Parent

class ParentListView(ListCreateAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (SearchFilter, OrderingFilter,DjangoFilterBackend)

    search_fields = ('fathers_name','mothers_name','fathers_phone',)
    ordering_fields = ('fathers_name','mothers_name','fathers_phone','mothers_phone')
    filterset_fields = ('fathers_name','mothers_name','fathers_phone','mothers_phone')


class ParentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]



class ParentListNoPGView(ListAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class StudentsParentListView(ListAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        queryset = Parent.objects.filter(Q(student__id=id) | Q(lid__id=id))
        return queryset
