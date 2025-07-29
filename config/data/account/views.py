# Create your views here.
import random

from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from passlib.context import CryptContext
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import UserCreateSerializer, UserUpdateSerializer, CheckNumberSerializer, \
    PasswordResetRequestSerializer, PasswordResetVerifySerializer
from .utils import build_weekly_schedule
from ..account.serializers import UserLoginSerializer, UserListSerializer, UserSerializer
from ..department.marketing_channel.models import ConfirmationCode
from ..finances.timetracker.sinx import TimetrackerSinc
from ..student.student.models import Student
from ..student.student.sms import SayqalSms

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class RegisterAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        if CustomUser.objects.filter(phone=phone).exists():
            return Response({'success': False, 'message': 'already_used_number'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user_serializer = UserCreateSerializer(user)

        tt = TimetrackerSinc()

        print(user.photo.file)

        photo_id_data = tt.upload_tt_foto(user.photo.file)
        photo_id = photo_id_data.get("id") if photo_id_data else None

        print(photo_id)

        external_data = {
            "photo": photo_id,
            "name": user.full_name,
            "phone_number": user.phone,
            "filials": [],
            "salary": user.salary,
            **build_weekly_schedule(user),
            "lunch_time": None
        }


        external_response = tt.create_data(external_data)

        print(external_response)

        if external_response and external_response.get("id"):
            user.second_user = external_response.get("id")
            user.save()

        return Response({
            "success": True,
            "user": user_serializer.data,
            "external_response": external_response
        }, status=status.HTTP_201_CREATED)


class UserList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs,
                                include_only=["id", "first_name", "last_name", "full_name", "phone", "balance","photo",
                                              "monitoring", "role", "calculate_penalties", "created_at"])

    def get_queryset(self):
        user = self.request.user
        filial = self.request.query_params.get('filial', None)

        role = self.request.query_params.get('role', None)

        is_archived = self.request.query_params.get('is_archived', None)

        subject = self.request.query_params.get('subject', None)

        search = self.request.GET.get('search', None)

        queryset = CustomUser.objects.filter().exclude(role__in=["Student", "Parents"])

        if search:
            queryset = queryset.filter(full_name__icontains=search)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if subject:
            queryset = queryset.filter(teachers__subject__id=subject).order_by('-created_at')

        if role:
            queryset = queryset.filter(role=role).order_by('-created_at')

        return queryset


class TT_Data(APIView):
    def get(self, request):
        tt = TimetrackerSinc()
        tt_data = tt.get_data()

        count = 0
        if tt_data:

            for user in tt_data:
                ic(user)
                phone = "+" + user["phone_number"] if not user["phone_number"].startswith('+') else user["phone_number"]
                ic(phone)
                if user:
                    check = CustomUser.objects.filter(phone=phone).exists()
                    if check:
                        custom_user = CustomUser.objects.get(phone=phone)
                        try:
                            custom_user.second_user = user['id']
                            custom_user.save()
                        except Exception as e:
                            ic(e)
                            continue
                        count += 1
                        ic("updated")
                        if user:
                            continue
                else:
                    continue
            ic(count)

        return Response({"count": count}, status=status.HTTP_200_OK)


class CustomAuthToken(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')

        if not user:
            raise AuthenticationFailed("Invalid credentials or user does not exist.")

        if user.phone != "+998911111111":
            for token in OutstandingToken.objects.filter(user=user):
                try:
                    BlacklistedToken.objects.get_or_create(token=token)
                except Exception:
                    return Response({
                        "token has been blacklisted",
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # ✅ Issue new tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        filial = list(user.filial.values_list('pk', flat=True))
        student_id = Student.objects.filter(user=user.id).values_list('id', flat=True).first()

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.pk,
            "student_id": student_id,
            'phone': user.phone,
            'role': user.role,
            'filial': filial,
        }, status=status.HTTP_200_OK)


class CustomRefreshTokenView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            user_id = refresh['user_id']
            user = CustomUser.objects.filter(id=user_id).first()
            if not user:
                raise AuthenticationFailed("User not found.")

            filial = list(user.filial.values_list('pk', flat=True))  # adjust if needed
            student_id = Student.objects.filter(user=user.id).values_list('id', flat=True).first()

            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),  # optional: reuse or rotate
                'user_id': user.pk,
                'phone': user.phone,
                'role': user.role,
                'filial': filial,
                'student_id': student_id,
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer


class CheckNumberApi(APIView):
    """
    API to check if a phone number exists in the database.
    Accepts phone number from request body.
    """

    @swagger_auto_schema(
        request_body=CheckNumberSerializer,  # ✅ Adds request body documentation in Swagger
        responses={200: openapi.Response("Returns if phone exists", CheckNumberSerializer)}
    )
    def post(self, request):
        serializer = CheckNumberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data.get("phone")
        ic(phone)
        exists = CustomUser.objects.filter(phone=phone).exists()

        return Response({"exists": exists}, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserInfo(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            user = CustomUser.objects.get(id=user.pk)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="User not found.")

        # Serialize the user data
        user_serializer = UserSerializer(user, context={
            "request": request
        })
        return Response(user_serializer.data)


class StuffRolesView(ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(
            *args, **kwargs,
            include_only=[
                "id", "first_name", "last_name", "full_name", "phone", "calculate_penalties",
                "balance", "subject", "filial", "role", "is_call_operator"
            ]
        )

    def get_queryset(self):
        subject = self.request.query_params.get('subject')
        filial = self.request.query_params.get('filial')
        role = self.request.query_params.get('role')
        is_call_operator = self.request.query_params.get('is_call_operator')
        search = self.request.GET.get('search')
        is_archived = self.request.GET.get('is_archived')

        queryset = CustomUser.objects.all().order_by('-created_at')

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        if subject:
            queryset = queryset.filter(teachers_groups__course__subject_id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if role:
            if role == "CALL_OPERATOR":
                filters = Q(role="CALL_OPERATOR")
                if is_call_operator:
                    is_call_operator_bool = is_call_operator.lower() == "true"
                    filters |= Q(is_call_center=is_call_operator_bool)
                queryset = queryset.filter(filters)

            elif role == "ADMINISTRATOR":
                queryset = queryset.filter(role__in=["ADMINISTRATOR", "SERVICE_SALES"])

            else:
                queryset = queryset.filter(role=role)

        elif is_call_operator:
            # If role is not provided but is_call_operator is
            is_call_operator_bool = is_call_operator.lower() == "true"
            queryset = queryset.filter(Q(is_call_center=is_call_operator_bool) | Q(role="CALL_OPERATOR"))

        return queryset.distinct()

    def get_paginated_response(self, data):
        return Response(data)


class StuffList(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        id = self.kwargs['pk']
        if id:
            return CustomUser.objects.filter(id=id)
        else:
            return CustomUser.objects.none()

    def get_paginated_response(self, data):
        return Response(data)


class PasswordResetRequestAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]

        code = random.randint(10000, 99999)
        ConfirmationCode.objects.update_or_create(phone=phone, defaults={"code": code, "created_at": timezone.now()})

        sms = SayqalSms()

        text = f""" Fitrat Student ilovasi — Parolni tiklash
                    Sizning raqamingiz: {phone}
                    Parolni tiklash kodingiz: {code}
                    
                    Ushbu kodni hech kimga bermang. U faqat sizga mo‘ljallangan!
                    
                    """

        try:
            sms.send_sms(phone, text)
        except Exception as e:
            return Response({"detail": "SMS sending failed."}, status=500)

        return Response({"detail": "Confirmation code sent."})


class PasswordResetVerifyAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["confirmation_code"]

        try:
            code_obj = ConfirmationCode.objects.get(phone=phone, code=code)
            if not code_obj.is_valid():
                return Response({"detail": "Code expired."}, status=status.HTTP_400_BAD_REQUEST)
        except ConfirmationCode.DoesNotExist:
            return Response({"detail": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Code is valid."}, status=status.HTTP_200_OK)


class PasswordUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["confirmation_code"]
        new_password = serializer.validated_data["new_password"]

        try:
            code_obj = ConfirmationCode.objects.get(phone=phone, code=code)
            if not code_obj.is_valid():
                return Response({"detail": "Code expired."}, status=status.HTTP_400_BAD_REQUEST)
        except ConfirmationCode.DoesNotExist:
            return Response({"detail": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        code_obj.delete()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
