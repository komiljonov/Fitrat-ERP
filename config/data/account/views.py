# Create your views here.
import re
import urllib

from django.db.models import Q
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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import UserCreateSerializer, UserUpdateSerializer, CheckNumberSerializer
from ..account.serializers import UserLoginSerializer, UserListSerializer, UserSerializer

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')



class RegisterAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if the phone number already exists
        phone = serializer.validated_data['phone']
        if CustomUser.objects.filter(phone=phone).exists():
            return Response({'success': False, 'message': 'already_used_number'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save the user (this calls the `create` method of the serializer)
        user = serializer.save()

        # Serialize the user to return a JSON response
        user_serializer = UserCreateSerializer(user)

        return Response({"user": user_serializer.data, 'success': True, 'message': 'User created successfully.'},
                        status=status.HTTP_201_CREATED)


class UserList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs,
                                include_only=["id", "first_name", "last_name", "full_name", "phone", "balance",
                                            "role","created_at"])

    def get_queryset(self):
        user = self.request.user
        filial = self.request.query_params.get('filial', None)

        role = self.request.query_params.get('role', None)

        is_archived = self.request.query_params.get('is_archived', None)

        subject = self.request.query_params.get('subject', None)
        queryset = CustomUser.objects.filter().exclude(role__in=["Student","Parents"])

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if subject:
            queryset = queryset.filter(teachers__subject__id=subject).order_by('-created_at')

        if role:
            queryset = queryset.filter(role=role).order_by('-created_at')

        return queryset


class CustomAuthToken(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Validate serializer data
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Get the validated user
        user = serializer.validated_data.get('user')
        if not user:
            raise AuthenticationFailed("Invalid credentials or user does not exist.")

        # Generate Refresh and Access Tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        filial = list(user.filial.values_list('pk', flat=True))  # Get a list of filial IDs

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.pk,
            'phone': user.phone,
            'role': user.role,
            'filial': filial,
        }, status=status.HTTP_200_OK)

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
        user_serializer = UserSerializer(user,context ={
            "request": request
        })
        return Response(user_serializer.data)



class StuffRolesView(ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('role', 'first_name', 'last_name')
    ordering_fields = ('role', 'first_name', 'last_name')
    filterset_fields = ('role', 'first_name', 'last_name')

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(
            *args, **kwargs,
            include_only=[
                "id", "first_name", "last_name", "full_name", "phone",
                "balance", "subject", "filial", "role", "is_call_operator"
            ]
        )

    def get_queryset(self):
        subject = self.request.query_params.get('subject')
        filial = self.request.query_params.get('filial')
        role = self.request.query_params.get('role')
        is_call_operator = self.request.query_params.get('is_call_operator')

        queryset = CustomUser.objects.all().order_by('-created_at')

        if subject:
            queryset = queryset.filter(teachers_groups__course__subject_id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if is_call_operator and is_call_operator.lower() == 'true':
            if role:
                queryset = queryset.filter(Q(is_call_center=True) | Q(role=role))
            else:
                queryset = queryset.filter(is_call_center=True)
        elif role:
            queryset = queryset.filter(role=role)

        return queryset.distinct()

    def get_paginated_response(self, data):
        return Response(data)


class StuffList(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)

    def get_queryset(self):
        id = self.kwargs['pk']
        if id:
            return CustomUser.objects.filter(id=id)
        else:
            return CustomUser.objects.none()

    def get_paginated_response(self, data):
        return Response(data)

