from django.urls import include, path


urlpatterns = [path("employees/", include("data.employee.urls"))]
