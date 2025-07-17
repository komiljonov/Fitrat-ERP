from django.urls import path

from .views import StuffRolesView, StuffList, CheckNumberApi, TT_Data, PasswordResetVerifyAPIView, \
    PasswordUpdateAPIView, PasswordResetRequestAPIView, CustomRefreshTokenView
from ..account.views import (
    CustomAuthToken,
    UserUpdateAPIView,
    LogoutAPIView,
    RegisterAPIView,
    UserList,
    UserInfo
)
urlpatterns = [
    path('', UserList.as_view(), name='user_list'),
    path('create', RegisterAPIView.as_view(), name='user_create'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('token', CustomAuthToken.as_view(), name='user_login'),
    path('tt/', TT_Data.as_view()),
    path('me/', UserInfo.as_view(), name='user-info'),
    path('refresh/', CustomRefreshTokenView.as_view(), name='user_refresh'),
    path('roles/', StuffRolesView.as_view(), name='stuff-roles'),
    path('check-number/', CheckNumberApi.as_view(), name='check-number'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetVerifyAPIView.as_view(), name='password_reset_done'),
    path('password-reset/done/', PasswordUpdateAPIView.as_view(), name='password_reset_complete'),
    path('<uuid:pk>/', StuffList.as_view(), name='user_info'),
    path('update/<uuid:pk>/', UserUpdateAPIView.as_view(), name='user_update'),
]
