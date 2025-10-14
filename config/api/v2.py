from django.urls import include, path


urlpatterns = [
    path("attendances/", include("data.student.attendance.v2.urls")),
    path("studentgroups/", include("data.student.studentgroup.v2.urls")),
    path("lessons/", include("data.student.lesson.v2.urls")),
    path("students/", include("data.student.student.v2.urls")),
    path("groups/", include("data.student.groups.v2.urls")),
    path("students/", include("data.student.student.v2.urls"))
]
