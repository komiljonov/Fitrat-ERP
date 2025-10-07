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
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import (
    UserCreateSerializer,
    UserUpdateSerializer,
    CheckNumberSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
)
from .utils import build_weekly_schedule
from data.account.serializers import (
    UserLoginSerializer,
    UserListSerializer,
    UserSerializer,
)
from data.department.marketing_channel.models import ConfirmationCode
from data.finances.timetracker.hrpulse import HrPulseIntegration
from data.student.student.models import Student
from data.student.student.sms import SayqalSms

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class RegisterAPIView(CreateAPIView):
#     serializer_class = UserCreateSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         phone = serializer.validated_data["phone"]
#         if CustomUser.objects.filter(phone=phone).exists():
#             return Response(
#                 {"success": False, "message": "already_used_number"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = serializer.save()
#         user_serializer = UserCreateSerializer(user)

#         tt = HrPulseIntegration()

#         photo_id_data = tt.upload_tt_foto(user.photo.file) if user.photo else None
#         photo_id = photo_id_data.get("id") if photo_id_data else None

#         filial_ids = []
#         for filial in user.filial.all():

#             if filial.tt_filial is None:
#                 response = tt.get_filial({filial.name})

#                 tt_id = (
#                     response[0].get("id")
#                     if isinstance(response, list) and response
#                     else None
#                 )

#                 if tt_id:
#                     filial.tt_filial = tt_id
#                     filial.save()
#                 else:
#                     filial_tt = tt.create_filial({"name": filial.name})
#                     if filial_tt:
#                         filial.tt_filial = filial_tt.get("id")
#                         filial.save()

#             if filial.tt_filial:
#                 filial_ids.append(filial.tt_filial)

#         external_data = {
#             "image": photo_id,
#             "name": user.full_name,
#             "phone_number": user.phone,
#             "filials": filial_ids,
#             "salary": user.salary,
#             **build_weekly_schedule(user),
#             "lunch_time": None,
#         }

#         external_response = tt.create_data(external_data)
#         print(external_response)

#         if external_response and external_response.get("id"):
#             user.second_user = external_response["id"]
#             user.save()

#         return Response(
#             {
#                 "success": True,
#                 "user": user_serializer.data,
#                 "external_response": external_response,
#             },
#             status=status.HTTP_201_CREATED,
#         )


class RegisterAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        print("Start: Received request")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("Step 1: Serializer validated")

        phone = serializer.validated_data["phone"]
        if CustomUser.objects.filter(phone=phone).exists():
            print("Step 2: Phone already used")
            return Response(
                {"success": False, "message": "already_used_number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("Step 3: Saving user")
        user = serializer.save()
        user_serializer = UserCreateSerializer(user)
        print(f"Step 4: User saved: {user.id}")

        tt = HrPulseIntegration()
        print("Step 5: HrPulseIntegration instance created")

        if user.photo:
            print("Step 6: Uploading user photo")
            photo_id_data = tt.upload_tt_foto(user.photo.file)
            photo_id = photo_id_data.get("id") if photo_id_data else None
            print(f"Step 6: Photo uploaded, id: {photo_id}")
        else:
            print("Step 6: No photo to upload")
            photo_id = None

        filial_ids = []
        print("Step 7: Processing filials")
        for filial in user.filial.all():
            print(f"Processing filial: {filial.name}")

            if filial.tt_filial is None:
                print("  tt_filial is None, fetching from TT")
                response = tt.get_filial({filial.name})
                tt_id = (
                    response[0].get("id")
                    if isinstance(response, list) and response
                    else None
                )

                if tt_id:
                    print(f"  Found TT filial id: {tt_id}")
                    filial.tt_filial = tt_id
                    filial.save()
                else:
                    print("  TT filial not found, creating new")
                    filial_tt = tt.create_filial({"name": filial.name})
                    if filial_tt:
                        filial.tt_filial = filial_tt.get("id")
                        filial.save()
                        print(f"  Created TT filial id: {filial.tt_filial}")

            if filial.tt_filial:
                filial_ids.append(filial.tt_filial)

        print(f"Step 8: Filial IDs prepared: {filial_ids}")

        external_data = {
            "image": photo_id,
            "name": user.full_name,
            "phone_number": user.phone,
            "filials": filial_ids,
            "salary": user.salary,
            "wt_mode": "NIGHTMARE",
            **build_weekly_schedule(user),
            "lunch_time": None,
        }

        print("Step 9: Sending data to external system")
        external_response = tt.create_data(external_data)
        print(f"Step 10: External response received: {external_response}")

        if external_response and external_response.get("id"):
            print(f"Step 11: Saving external id to user: {external_response['id']}")
            user.second_user = external_response["id"]
            user.save()

        print("Step 12: Returning response")
        return Response(
            {
                "success": True,
                "user": user_serializer.data,
                "external_response": external_response,
            },
            status=status.HTTP_201_CREATED,
        )


class UserList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(
            *args,
            **kwargs,
            include_only=[
                "id",
                "first_name",
                "last_name",
                "full_name",
                "phone",
                "balance",
                "photo",
                "monitoring",
                "role",
                "calculate_penalties",
                "created_at",
            ],
        )

    def get_queryset(self):
        user = self.request.user
        filial = self.request.GET.get("filial", None)

        role = self.request.GET.get("role", None)

        is_archived = self.request.GET.get("is_archived", None)

        subject = self.request.GET.get("subject", None)

        search = self.request.GET.get("search", None)

        queryset = CustomUser.objects.filter().exclude(role__in=["Student", "Parents"])

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | Q(phone__icontains=search)
            )

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if subject:
            queryset = queryset.filter(teachers__subject__id=subject).order_by(
                "-created_at"
            )

        if role:
            queryset = queryset.filter(role=role).order_by("-created_at")

        return queryset


class TT_Data(APIView):
    def get(self, request):
        tt = HrPulseIntegration()
        tt_data = tt.get_data()
        count = 0

        if not tt_data:
            return Response(
                {"count": 0, "message": "No data from TT"}, status=status.HTTP_200_OK
            )

        # Collect all TT user phones to detect missing ones later
        tt_phones = set()
        tt_ids_by_phone = {}

        for user in tt_data:
            phone = (
                "+" + user["phone_number"]
                if not user["phone_number"].startswith("+")
                else user["phone_number"]
            )
            tt_phones.add(phone)
            tt_ids_by_phone[phone] = user["id"]

        for phone in tt_phones:
            ic(phone)

        for phone in tt_phones:
            if not CustomUser.objects.filter(phone=phone).exists():
                continue

            try:
                custom_user = CustomUser.objects.get(phone=phone)
                user_id = tt_ids_by_phone[phone]

                # ✅ Update second_user
                custom_user.second_user = user_id
                custom_user.save()

                # ✅ Ensure filials have tt_filial
                for filial in custom_user.filial.all():
                    if not filial.tt_filial:
                        existing_tt = tt.get_filial(filial.name)
                        if isinstance(existing_tt, list) and existing_tt:
                            tt_id = existing_tt[0].get("id")
                        elif isinstance(existing_tt, dict):
                            tt_id = existing_tt.get("id")
                        else:
                            tt_id = None

                        if not tt_id:
                            created_tt = tt.create_filial({"name": filial.name})
                            tt_id = created_tt.get("id") if created_tt else None

                        if tt_id:
                            filial.tt_filial = tt_id
                            filial.save()
                            ic(f"🆕 TT Filial created: {filial.name}")

                # ✅ Update photo or filials if needed
                update_payload = {}
                tt_user_filials = set(user.get("filials", []))
                local_tt_filials = set(
                    custom_user.filial.filter(tt_filial__isnull=False).values_list(
                        "tt_filial", flat=True
                    )
                )

                if not tt_user_filials or tt_user_filials != local_tt_filials:
                    update_payload["filials"] = list(local_tt_filials)

                if not user.get("image") and custom_user.photo:
                    uploaded = tt.upload_tt_foto(custom_user.photo.file)
                    if uploaded and uploaded.get("id"):
                        update_payload["image"] = uploaded["id"]
                        ic(f"📸 TT photo uploaded for {phone}")

                if update_payload:
                    ic(f"🔁 TT UPDATE: {update_payload}")
                    tt.update_data(user_id, update_payload)

                count += 1
                ic(f"✅ Updated user: {phone}")

            except Exception as e:
                ic(f"❌ Error processing user {phone}: {e}")
                continue

        # ✅ Now create missing TT users from our local DB
        custom_users = CustomUser.objects.exclude(
            phone__in=tt_phones, role__in=["Parents", "Student"]
        )

        for user in custom_users:
            try:
                photo_id_data = (
                    tt.upload_tt_foto(user.photo.file) if user.photo else None
                )
                photo_id = photo_id_data.get("id") if photo_id_data else None

                filial_ids = []
                for filial in user.filial.all():
                    if filial.tt_filial is None:
                        response = tt.get_filial(filial.name)
                        tt_id = (
                            response[0].get("id")
                            if isinstance(response, list) and response
                            else None
                        )
                        if not tt_id:
                            filial_tt = tt.create_filial({"name": filial.name})
                            tt_id = filial_tt.get("id") if filial_tt else None
                        if tt_id:
                            filial.tt_filial = tt_id
                            filial.save()
                    if filial.tt_filial:
                        filial_ids.append(filial.tt_filial)

                external_data = {
                    "image": photo_id,
                    "name": user.full_name,
                    "phone_number": user.phone,
                    "filials": filial_ids,
                    "salary": user.salary,
                    **build_weekly_schedule(user),
                    "lunch_time": None,
                }

                external_response = tt.create_data(external_data)
                if external_response and external_response.get("id"):
                    user.second_user = external_response["id"]
                    user.save()
                    ic(f"✅ Created TT user: {user.phone}")
                    count += 1

            except Exception as e:
                ic(f"❌ Failed to create TT user for {user.phone}: {e}")
                continue

        ic(count)
        return Response({"count": count}, status=status.HTTP_200_OK)


class CustomAuthToken(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")

        if not user:
            raise AuthenticationFailed("Invalid credentials or user does not exist.")

        if user.phone != "+998911111111":
            for token in OutstandingToken.objects.filter(user=user):
                try:
                    BlacklistedToken.objects.get_or_create(token=token)
                except Exception as e:
                    print(
                        f"[Token Blacklist Error] token_id={token.id}, error={str(e)}"
                    )
                    continue

        # ✅ Issue new tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        filial = list(user.filial.values_list("pk", flat=True))
        student_id = (
            Student.objects.filter(user=user.id).values_list("id", flat=True).first()
        )

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user.pk,
                "student_id": student_id,
                "phone": user.phone,
                "role": user.role,
                "filial": filial,
            },
            status=status.HTTP_200_OK,
        )


class CustomRefreshTokenView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            user_id = refresh["user_id"]
            user = CustomUser.objects.filter(id=user_id).first()

            if not user:
                raise AuthenticationFailed("User not found.")

            filial = list(user.filial.values_list("pk", flat=True))  # adjust if needed

            student_id = (
                Student.objects.filter(user=user.id)
                .values_list("id", flat=True)
                .first()
            )

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": str(refresh),  # optional: reuse or rotate
                    "user_id": user.pk,
                    "phone": user.phone,
                    "role": user.role,
                    "filial": filial,
                    "student_id": student_id,
                },
                status=status.HTTP_200_OK,
            )

        except TokenError as e:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


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
        responses={
            200: openapi.Response("Returns if phone exists", CheckNumberSerializer)
        },
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
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class UserInfo(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            user = CustomUser.objects.get(id=user.pk)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="User not found.")

        # Serialize the user data
        user_serializer = UserSerializer(user, context={"request": request})
        return Response(user_serializer.data)


class StuffRolesView(ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(
            *args,
            **kwargs,
            include_only=[
                "id",
                "first_name",
                "last_name",
                "full_name",
                "phone",
                "calculate_penalties",
                "balance",
                "subject",
                "filial",
                "role",
                "is_call_operator",
            ],
        )

    def get_queryset(self):
        subject = self.request.GET.get("subject")
        filial = self.request.GET.get("filial")
        role = self.request.GET.get("role")
        is_call_operator = self.request.GET.get("is_call_operator")
        search = self.request.GET.get("search")
        is_archived = self.request.GET.get("is_archived")

        queryset = CustomUser.objects.all().order_by("-created_at")

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
            queryset = queryset.filter(
                Q(is_call_center=is_call_operator_bool) | Q(role="CALL_OPERATOR")
            )

        return queryset.distinct().prefetch_related("filials")

    def get_paginated_response(self, data):
        return Response(data)


class StuffList(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        id = self.kwargs["pk"]
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
        role = serializer.validated_data["role"]

        print(phone, role)

        user = CustomUser.objects.filter(phone=phone, role=role).first()

        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        code = random.randint(10000, 99999)

        ConfirmationCode.objects.update_or_create(
            phone=phone, defaults={"code": code, "created_at": timezone.now()}
        )

        sms = SayqalSms()

        text = f""" Fitrat Student ilovasi — Parolni tiklash
                    Sizning raqamingiz: {phone}
                    Parolni tiklash kodingiz: {code}

                    Ushbu kodni hech kimga bermang. U faqat sizga mo‘ljallangan!

                    """
        print("Sending sms")
        try:

            sms.send_sms(phone, text)
        except Exception as e:
            return Response({"detail": "SMS sending failed."}, status=500)

        print("Sending sms")

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
                return Response(
                    {"detail": "Code expired."}, status=status.HTTP_400_BAD_REQUEST
                )
        except ConfirmationCode.DoesNotExist:
            return Response(
                {"detail": "Invalid confirmation code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                return Response(
                    {"detail": "Code expired."}, status=status.HTTP_400_BAD_REQUEST
                )
        except ConfirmationCode.DoesNotExist:
            return Response(
                {"detail": "Invalid confirmation code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(new_password)
        user.save()

        code_obj.delete()

        return Response(
            {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
        )
