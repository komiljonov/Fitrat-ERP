from rest_framework_simplejwt.tokens import RefreshToken

from config.data.account.models import CustomUser


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    print("Refresh Token:", refresh)  # Debug
    print("Access Token:", refresh.access_token)  # Debug
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
get_tokens_for_user(user=CustomUser.objects.first() )