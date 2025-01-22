from .views import StudentGroupList,StudentGroupDetail,StudentGroupNopg
from django.urls import path

urlpatterns = [
    path('', StudentGroupList.as_view()),
    path('<uuid:pk>/', StudentGroupDetail.as_view()),
    path('no-pg/', StudentGroupNopg.as_view()),

]