# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from passlib.context import CryptContext
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .permission import FilialRestrictedQuerySetMixin
from .serializers import UserCreateSerializer, UserUpdateSerializer
from ..account.serializers import UserLoginSerializer, UserListSerializer, UserSerializer

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')



class RegisterAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    # permission_classes = [IsAuthenticated]  # Only authenticated users can create new users

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if the phone number already exists
        phone = serializer.validated_data['phone']
        if CustomUser.objects.filter(phone=phone).exists():
            return Response({'success': False, 'message': 'This phone number is already registered.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save the user (this calls the `create` method of the serializer)
        user = serializer.save()

        return Response({'success': True, 'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)


class UserList(FilialRestrictedQuerySetMixin,ListAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = CustomUser.objects.all().order_by('-created_at')
    serializer_class = UserListSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        if role:
            return CustomUser.objects.filter(role=role).order_by('-created_at')
        return CustomUser.objects.none().order_by('-created_at')



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
        filial = user.filial.pk if user.filial else None

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.pk,
            'phone': user.phone,
            'role': user.role,
            'filial': filial,
        }, status=status.HTTP_200_OK)


class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)



class StuffRolesView(ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('role','first_name','last_name')
    ordering_fields = ('role','first_name','last_name')
    filterset_fields = ('role','first_name','last_name')

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

