
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView

from .views import StuffRolesView, StuffList
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
    # path('confirm-code', ConfirmationCodeAPIView.as_view(), name='confirm_code'),
    # path('forget-password', PasswordResetRequestView.as_view(), name='forget_password'),
    # path('reset-password/<str:uid>/<str:token>', PasswordResetView.as_view() ,name='reset-password-view'),

    path('',UserList.as_view(), name='user_list'),
    path('<uuid:pk>/', StuffList.as_view(), name='user_info'),
    path('<uuid:pk>/', UserUpdateAPIView.as_view(), name='user_update'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('me/',UserInfo.as_view(), name='user-info'),

    path('roles/',StuffRolesView.as_view(), name='stuff-roles')
]

# urlpatterns += [
#     path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
#     path('api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
# ]

