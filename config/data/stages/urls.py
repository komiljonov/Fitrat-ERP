from django.urls import path

from .views import NewLidStagesViewSet,NewLidNoPG,NewLidStagesRetrive

urlpatterns = [
    path('',NewLidStagesViewSet.as_view(), name='new-lid-stages'),
    path('<uuid:pk>/',NewLidStagesRetrive.as_view(), name='new-lid-stages-retrive'),
    path('no-pg/',NewLidNoPG.as_view(), name='new-lid-stages-nopg'),
]