"""
URL configuration for khalifa project.

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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

schema_view = get_schema_view(
    openapi.Info(
        title="Fitrat ERP API",
        default_version="v1",
        description="Project documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("data.account.urls")),

    path("tasks/", include("data.tasks.urls")),
    path("comments/", include("data.comments.urls")),
    path("dubl/", include("data.dubl.urls")),

    path("filial/", include("data.department.filial.urls")),
    path('marketing/', include("data.department.marketing_channel.urls")),

    path('lid/', include("data.lid.new_lid.urls")),
    path('archived/', include('data.lid.archived.urls')),

    path('stages/',include("data.stages.urls")),


    path("docs<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]


urlpatterns += [
    path("api_docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)