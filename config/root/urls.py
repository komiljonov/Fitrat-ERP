"""
URL configuration for Fitrat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
import debug_toolbar
from debug_toolbar.toolbar import debug_toolbar_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Fitrat ERP API",
        default_version="v1",
        description="Project documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path("admin/", admin.site.urls),
    path("auth/", include("data.account.urls")),
    # path('dash/', include('django_plotly_dash.urls')),

    path("payme/", include("data.payme.urls")),

    path("tasks/", include("data.tasks.urls")),
    path("comments/", include("data.comments.urls")),

    path("filial/", include("data.department.filial.urls")),
    path('marketing/', include("data.department.marketing_channel.urls")),

    path('lid/', include("data.lid.new_lid.urls")),
    path('archived/', include('data.lid.archived.urls')),

    path('groups/', include('data.student.groups.urls')),
    path('add-group/', include('data.student.studentgroup.urls')),
    path('students/', include('data.student.student.urls')),
    path('lessons/', include('data.student.lesson.urls')),
    path('attendances/', include('data.student.attendance.urls')),
    path('subjects/', include('data.student.subject.urls')),
    path('courses/', include('data.student.course.urls')),
    path('quizzes/', include('data.student.quiz.urls')),
    path('mastering/', include('data.student.mastering.urls')),
    path('homework/', include('data.student.homeworks.urls')),
    path('appsettings/', include('data.student.appsettings.urls')),
    path('shop/', include('data.student.shop.urls')),

    path('results/', include('data.results.urls')),
    path('parents/', include('data.parents.urls')),
    path('teacher/', include('data.teachers.teacher.urls')),

    path('finance/', include('data.finances.finance.urls')),
    path('compensation/', include('data.finances.compensation.urls')),
    path('timetracker/', include('data.finances.timetracker.urls')),

    path('notifications/', include('data.notifications.urls')),

    path('upload/', include('data.upload.urls')),
    path('dashboard/', include('data.dashboard.urls')),

    path("docs<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui", ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += [
    path("api_docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui", ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += + debug_toolbar_urls()
