

from django.urls import include, path
from django.conf.urls.static import static

from .views import CategoryCreateAPIView, CategoryRetrieveUpdateDestroyAPIView, LibraryRetrieveUpdateDestroyAPIView, \
    LibraryCreateAPIView

urlpatterns = [
    path("",LibraryCreateAPIView.as_view()),
    path("<uuid:pk>/",CategoryRetrieveUpdateDestroyAPIView.as_view()),

    path("category/",CategoryCreateAPIView.as_view()),
    path("category/<uuid:pk>/",CategoryRetrieveUpdateDestroyAPIView.as_view()),
]