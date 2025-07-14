from django.urls import path

from .views import FilialListCreate, FilialRetrieveUpdateDestroy, FilialListNoPG, UserFilialListCreate, \
    UserFilialRetrieveUpdateDestroy

urlpatterns = [
    path('', FilialListCreate.as_view(), name='filial-list-create'),
    path('<uuid:pk>/',FilialRetrieveUpdateDestroy.as_view(), name='filial-retrieve-update'),
    path('no-pg/',FilialListNoPG.as_view(), name='filial-list-no-pg'),

    path("users/",UserFilialListCreate.as_view(), name='filial-user-list-create'),
    path("users/<uuid:pk>",UserFilialRetrieveUpdateDestroy.as_view())

]