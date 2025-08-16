from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from .models import LibraryCategory, Library
from .serializers import LibraryCategorySerializer, LibrarySerializer


# Create your views here.


class CategoryCreateAPIView(ListCreateAPIView):
    queryset = LibraryCategory.objects.all()
    serializer_class = LibraryCategorySerializer

    pagination_class = None

    def get_paginated_response(self, data):
        return Response({data})


class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = LibraryCategory.objects.all()
    serializer_class = LibraryCategorySerializer


class LibraryCreateAPIView(ListCreateAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

    def get_queryset(self):
        queryset = Library.objects.all()

        category = self.request.GET.get("category")
        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(title__icontains=search)
            )

        if category:
            queryset = queryset.filter(category__id=category)

        return queryset


class LibraryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
