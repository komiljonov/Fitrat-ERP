from django.urls import include, path


urlpatterns = [
    path("employees/", include("data.employee.urls")),
    path("first_lessons/", include("data.firstlesson.urls")),
    path("archives/", include("data.archive.urls")),
    path("transactions/", include("data.student.transactions.urls"))
]
