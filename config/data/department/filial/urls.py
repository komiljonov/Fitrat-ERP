from django.urls import path

from .views import FilialListCreate, FilialRetrieveUpdateDestroy,FilialListNoPG

urlpatterns = [
    path('', FilialListCreate.as_view(), name='filial-list-create'),
    path('<uuid:pk>/',FilialRetrieveUpdateDestroy.as_view(), name='filial-retrieve-update'),
    path('no-pg/',FilialListNoPG.as_view(), name='filial-list-no-pg'),
]