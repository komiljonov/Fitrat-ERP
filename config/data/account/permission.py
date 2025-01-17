from django.contrib.auth.backends import BaseBackend
from rest_framework.permissions import BasePermission, DjangoModelPermissions

from ..account.models import CustomUser
from rest_framework.permissions import BasePermission
from .models import CustomUser
from ..student.student.models import Student
from ..lid.new_lid.models import Lid

# from .models import UserRole
#
# class IsAdminPermission(BasePermission):
#     def has_permission(self, request, view):
#         try:
#             admin_role = UserRole.objects.get(user=request.user).role.name
#         except UserRole.DoesNotExist:
#             return False
#         return admin_role.lower() == "admin"


class PhoneAuthBackend(BaseBackend):
    def authenticate(self, request, phone=None, password=None):
        print(f"Attempting authentication for phone: {phone}")
        try:
            user = CustomUser.objects.get(phone=phone)
            if user.check_password(password):
                print("Authentication successful")
                return user
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



class RoleBasedPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return False

        # Handle views without the `action` attribute
        view_action = getattr(view, "action", None)

        # Administrator Permissions
        if user.role == "ADMINISTRATOR":
            if view_action in ["create", "destroy"]:
                if "role" in request.data and request.data["role"] in ["ADMINISTRATOR", "DIRECTOR"]:
                    return False
            return True

        # Director Permissions
        if user.role == "DIRECTOR":
            return True

        # Moderator Permissions
        if user.role == "MODERATOR":
            if view_action in ["retrieve", "update", "partial_update"]:
                # Check if the moderator is assigned to the student
                student_id = view.kwargs.get("pk")
                if student_id:
                    return Student.objects.filter(pk=student_id, moderator=user).exists()
            return False

        # Call Operator Permissions
        if user.role == "CALL_OPERATOR":
            if view_action in ["retrieve", "update", "partial_update"]:
                # Check if the lead is assigned to the call operator
                lead_id = view.kwargs.get("pk")
                if lead_id:
                    return Lid.objects.filter(pk=lead_id, call_operator=user).exists()
            return False

        # Accounting Permissions
        if user.role == "ACCOUNTING":
            if view_action == "create" and "role" in request.data:
                return False  # Cannot create users
            return True

        # Teacher Permissions
        if user.role == "TEACHER":
            return view_action in ["retrieve", "update", "partial_update"]

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions for filial-level restrictions.
        """
        user = request.user

        # All roles can only access data related to their filial(s)
        if hasattr(obj, "filial") and obj.filial != user.filial:
            return False

        return True



