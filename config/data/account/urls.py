
from django.urls import path

from .views import StuffRolesView, StuffList, CheckNumberApi, TT_Data, PasswordResetAPIView, PasswordResetRequestAPIView
from ..account.views import (
    CustomAuthToken,
    UserUpdateAPIView,
    LogoutAPIView,
    RegisterAPIView,
    UserList,
    UserInfo
)

urlpatterns = [
    path('token', CustomAuthToken.as_view(), name='user_login'),
    path('create', RegisterAPIView.as_view(), name='user_create'),

    path("tt/",TT_Data.as_view()),

    path('',UserList.as_view(), name='user_list'),
    path('<uuid:pk>/', StuffList.as_view(), name='user_info'),
    path('update/<uuid:pk>/', UserUpdateAPIView.as_view(), name='user_update'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('me/',UserInfo.as_view(), name='user-info'),

    path('roles/',StuffRolesView.as_view(), name='stuff-roles'),
    path("check-number/",CheckNumberApi.as_view(), name='check-number'),

    path("password-reset/",PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path("password-reset/done/",PasswordResetAPIView.as_view(), name='password_reset_done'),
]
