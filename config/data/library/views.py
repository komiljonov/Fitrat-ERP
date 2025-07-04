from django.shortcuts import render
from unicodedata import category

# Create your views here.

from .serializers import CategorySerializer,LibrarySerializer
from .models import Category,Library

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView

class CategoryCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LibraryCreateAPIView(ListCreateAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

    def get_queryset(self):
        queryset = Library.objects.all()

        category = self.request.GET.get('category')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(name__icontains=search)

        if category:
            queryset = queryset.filter(category__id=category)

        return queryset

class LibraryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
