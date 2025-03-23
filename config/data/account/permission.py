from django.contrib.auth.backends import BaseBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import CustomUser


class PhoneAuthBackend(BaseBackend):
    def authenticate(self, request, phone=None, password=None):
        print(f"Attempting authentication for phone: {phone}")
        try:
            user = CustomUser.objects.get(phone=phone)
            if user.check_password(password):
                print("Authentication successful")
                return user
            elif user.is_archived:
                return Response({"Xodim arxivlanganligi sababli tizimga kirishi taqiqlanadi!"})

            else:
                print("Invalid password")
        except CustomUser.DoesNotExist:
            print("User does not exist")
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


# class RoleBasedPermission(BasePermission):
#     """
#     Custom permission class to handle role-based access control.
#     """
#
#     def has_permission(self, request, view):
#         user = request.user
#
#         # Ensure the user is authenticated
#         if not user.is_authenticated:
#             return False
#
#         # Determine the action being performed
#         view_action = getattr(view, "action", None)
#
#         # Administrator Permissions
#         if user.role == "ADMINISTRATOR":
#             if view_action in ["create", "destroy"]:
#                 # Restrict creating or deleting ADMINISTRATOR/DIRECTOR roles
#                 restricted_roles = ["ADMINISTRATOR", "DIRECTOR"]
#                 if "role" in request.data and request.data["role"] in restricted_roles:
#                     return False
#             return True  # Full access for administrators
#
#         # Director Permissions
#         if user.role == "DIRECTOR":
#             return True  # Directors have full access
#
#         # Moderator Permissions
#         if user.role == "MODERATOR":
#             if view_action in ["retrieve", "update", "partial_update"]:
#                 # Moderators can only access students they are assigned to
#                 student_id = view.kwargs.get("pk")
#                 if student_id:
#                     return Student.objects.filter(pk=student_id, moderator=user).exists()
#             return False
#
#         # Call Operator Permissions
#         if user.role == "CALL_OPERATOR":
#             if view_action in ["retrieve", "update", "partial_update"]:
#                 # Call operators can only access leads they are assigned to
#                 lead_id = view.kwargs.get("pk")
#                 if lead_id:
#                     return Lid.objects.filter(pk=lead_id, call_operator=user).exists()
#             return False
#
#         # Accounting Permissions
#         if user.role == "ACCOUNTING":
#             if view_action == "create" and "role" in request.data:
#                 # Accountants cannot create users
#                 return False
#             return True
#
#         # Teacher Permissions
#         if user.role == "TEACHER":
#             # Teachers can only retrieve or update their own data
#             return view_action in ["retrieve", "update", "partial_update"]
#
#         # Default to denying access for unknown roles
#         return False
#
#     def has_object_permission(self, request, view, obj):
#         """
#         Check object-level permissions for filial-level restrictions and specific role-based rules.
#         """
#         user = request.user
#
#         # Ensure object belongs to the user's filial
#         if hasattr(obj, "filial") and obj.filial != user.filial:
#             return False
#
#         # Additional object-level permissions for specific roles
#         if user.role == "MODERATOR" and isinstance(obj, Student):
#             # Moderators can only access students they are assigned to
#             return obj.moderator == user
#
#         if user.role == "CALL_OPERATOR" and isinstance(obj, Lid):
#             # Call operators can only access leads they are assigned to
#             return obj.call_operator == user
#
#         return True  # Allow access if no restrictions are violated



class FilialRestrictedQuerySetMixin:
    """
    Mixin to filter querysets by the user's filial and enforce data restrictions.
    """


    def get_queryset(self):
        # Get the base queryset from the view
        queryset = super().get_queryset()
        role = self.request.query_params.get('role', None)
        if role:
            return CustomUser.objects.filter(role=role)

        # Get the user's filial
        user = self.request.user
        user_filial = getattr(user, "filial", None)

        if user.role == "DIRECTOR":
            return queryset


        if not user_filial:
            return queryset.none()

        queryset = queryset.filter(filial__in=user_filial.all())

        return queryset

    def perform_create(self, serializer):
        """
        Automatically assign the user's filial during object creation.
        """
        user = self.request.user
        user_filial = getattr(user, "filial", None)

        if not user_filial:
            raise PermissionDenied("You do not have a valid filial assigned.")

        if user.role == "CALL_OPERATOR":
            return serializer.save()

        serializer.save(filial=user_filial)

