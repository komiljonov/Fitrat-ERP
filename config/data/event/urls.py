from django.urls import include, path

from data.event.views import EventListCreate, EventDetail

urlpatterns = [
    path("",EventListCreate.as_view()),
    path("<uuid:pk>/",EventDetail.as_view()),
]