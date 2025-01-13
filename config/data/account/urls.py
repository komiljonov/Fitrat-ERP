
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView

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

    path('user-list',UserList.as_view(), name='user_list'),
    path('user-update/<int:id>/', UserUpdateAPIView.as_view(), name='user_update'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('user-info/<int:id>/',UserInfo.as_view(), name='user-info')
]

# urlpatterns += [
#     path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
#     path('api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
# ]

