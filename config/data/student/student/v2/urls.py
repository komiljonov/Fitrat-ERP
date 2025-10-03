from django.urls import path


from .views import NewStudentsStatsAPIView


urlpatterns = [
    path("stats/new_students", NewStudentsStatsAPIView.as_view())
]
