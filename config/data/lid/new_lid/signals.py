import random
import string
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ..new_lid.models import Lid
from ...account.models import CustomUser
from ...command.admin import models
from ...finances.finance.models import SaleStudent
from ...logs.models import Log
from ...parents.models import Relatives
from ...student.attendance.models import Attendance
from ...student.student.models import Student
from ...student.student.sms import SayqalSms
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup

sms = SayqalSms()


# @receiver(post_save, sender=Lid)
# def on_creating_lid(sender, instance : Lid, created, **kwargs):
#     if created:
#         Log.objects.create(
#             app="Lid",
#             model="Lid",
#             action="Log",
#             model_action="Created",
#             lid=instance,
#         )
#     if not created:
#         Log.objects.create(
#             app="Lid",
#             model="Lid",
#             action="Log",
#             model_action="Updated",
#             lid=instance,
#         )


@receiver(pre_save, sender=Lid)
def on_pre_save(sender, instance, **kwargs):
    """
    Before saving a Lid instance, check if:
    - The lid_stage_type is changing from 'NEW_LID' to 'ORDERED_LID'
    - The call_operator field is None, then assign the first available call operator.
    """

    if not instance._state.adding:  # Ensure it's an update, not a new instance
        # Fetch previous value of `lid_stage_type` before update
        previous_instance = sender.objects.get(pk=instance.pk)

        if (
                previous_instance.lid_stage_type == "NEW_LID"
                and instance.lid_stage_type == "ORDERED_LID"
                and instance.call_operator is None
        ):
            call_operator = CustomUser.objects.filter(role="CALL_OPERATOR").first()
            if call_operator:
                instance.call_operator = call_operator  # Corrected assignment

                # Ensure atomic transaction to avoid partially updated data
                with transaction.atomic():
                    instance.save(update_fields=["call_operator"])


@receiver(post_save, sender=Lid)
def on_details_create(sender, instance: Lid, created, **kwargs):
    """
    Signal to create or update a Student when a Lid is created or updated,
    provided `is_student=True` and `phone_number` is available.
    """
    if not created:
        if instance.lid_stage_type == "NEW_LID":
            if instance.lid_stages == "YANGI_LEAD":
                instance.lid_stages = "KUTULMOQDA"

        if instance.lid_stage_type == "ORDERED_LID":
            if instance.ordered_date == None:
                instance.ordered_date = datetime.now()
            if instance.ordered_stages == "YANGI_BUYURTMA":
                instance.ordered_stages = "KUTULMOQDA"

        if instance.is_expired:
            instance.is_expired = False
            instance.save()

        if instance.is_student and instance.filial:
            password = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            student, student_created = Student.objects.get_or_create(
                phone=instance.phone_number,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "photo": instance.photo,
                    "password": make_password(password),
                    "middle_name": instance.middle_name,
                    "date_of_birth": instance.date_of_birth,
                    "education_lang": instance.education_lang,
                    "student_type": instance.student_type,
                    "edu_class": instance.edu_class,
                    "edu_level": instance.edu_level,
                    "subject": instance.subject,
                    "balance": instance.balance,
                    "ball": instance.ball,
                    "filial": instance.filial,
                    "marketing_channel": instance.marketing_channel,
                    "call_operator": instance.call_operator,
                    "service_manager": instance.service_manager,
                    "sales_manager": instance.sales_manager,
                    "new_student_date": datetime.now(),
                },
            )

            # sms.send_sms(
            #     number=student.phone,
            #     message=f"""
            #     Fitrat Student ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!
            #
            #     Login: {student.phone}
            #     Parol: {password}
            #
            #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
            #     """
            # )

            if not student_created:
                student.first_name = instance.first_name
                student.last_name = instance.last_name
                student.photo = instance.photo
                student.middle_name = instance.middle_name
                student.date_of_birth = instance.date_of_birth
                student.password = make_password(password)
                student.education_lang = instance.education_lang
                student.student_type = instance.student_type
                student.edu_class = instance.edu_class
                student.edu_level = instance.edu_level
                student.subject = instance.subject
                student.ball = instance.ball
                student.filial = instance.filial
                student.marketing_channel = instance.marketing_channel
                student.call_operator = instance.call_operator
                student.service_manager = instance.service_manager
                student.sales_manager = instance.sales_manager
                student.balance = (
                    instance.balance
                    if instance.balance == 0
                    else student.balance + instance.balance
                )
                student.save()

                # sms.send_sms(
                #     number=student.phone,
                #     message=f"""
                #     Fitrat Student ilovasida muvaffaqiyatli ma'lumotlaringiz yangilandi!
                #
                #     Login: {student.phone}
                #     Parol: {password}
                #
                #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                #     """
                # )

            StudentGroup.objects.filter(lid=instance).update(student=student, lid=None)

            if SecondaryStudentGroup.objects.filter(lid=instance):
                SecondaryStudentGroup.objects.filter(lid=instance).update(
                    student=student, lid=None
                )

            Attendance.objects.filter(lid=instance).update(student=student, lid=None)

            SaleStudent.objects.filter(lid=instance).update(student=student, lid=None)

            Relatives.objects.filter(lid=instance).update(student=student)
            # Archive the Lid
            post_save.disconnect(on_details_create, sender=Lid)
            instance.is_archived = True
            instance.save()
            post_save.connect(on_details_create, sender=Lid)

        else:
            if instance.filial is None:
                print(
                    "This lead's education branch is not updated, please add education branch."
                )

            post_save.disconnect(on_details_create, sender=Lid)
            instance.save()
            post_save.connect(on_details_create, sender=Lid)


@receiver(post_save, sender=Lid)
def on_expired_delete(sender, instance: Lid, created, **kwargs):
    if not created:
        if instance.is_expired:
            instance.is_expired = False
            instance.save()

    if created:
        if instance.lid_stage_type != None and instance.lid_stages == None:
            instance.lid_stages = "YANGI_LEAD"
            instance.save()


# Logs Lid catching
from django.db import models as dj_models


def _is_trackable_field(field: dj_models.Field) -> bool:
    """
    Track: concrete, editable, not auto, not M2M through fields.
    """
    if getattr(field, "auto_created", False):
        return False
    if getattr(field, "many_to_many", False):
        return False
    if not getattr(field, "editable", True):
        return False
    # You can exclude BaseModel common fields here if needed, e.g. updated_at
    if field.name in {"created_at", "updated_at"}:
        return False
    return True


def _human(model_instance, field: dj_models.Field, value):
    if value is None:
        return "—"

    # Choices: prefer display text if available
    get_display = None
    method_name = f"get_{field.name}_display"
    if hasattr(model_instance, method_name):
        get_display = getattr(model_instance, method_name)
    if get_display:
        try:
            return str(get_display())
        except Exception:
            pass

    # ForeignKey: show related object's string
    if isinstance(field, models.ForeignKey):
        try:
            return str(value) if value is not None else "—"
        except Exception:
            return f"{field.related_model.__name__}({getattr(model_instance, field.attname)})"

    # FileField/ImageField
    from django.db.models.fields.files import FieldFile
    if isinstance(value, FieldFile):
        return value.name or "—"

    # Decimal
    if isinstance(value, Decimal):
        try:
            return f"{value.quantize(Decimal('0.01'))}"
        except Exception:
            return str(value)

    # Date/DateTime
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)

    return str(value)


def _collect_changes(old_obj: Lid, new_obj: Lid):
    """
    Return dict: {field_name: (old_value, new_value)} for all changed fields.
    FK compare by *_id.
    """
    changes = {}
    for field in new_obj._meta.get_fields():
        if not _is_trackable_field(field):
            continue

        # For FKs, compare *_id to avoid fetching relations
        if isinstance(field, dj_models.ForeignKey):
            old_id = getattr(old_obj, f"{field.name}_id", None)
            new_id = getattr(new_obj, f"{field.name}_id", None)
            if old_id != new_id:
                # Render human-friendly using actual related values
                old_val = getattr(old_obj, field.name, None)
                new_val = getattr(new_obj, field.name, None)
                changes[field.name] = (old_val, new_val)
        else:
            old_val = getattr(old_obj, field.name, None)
            new_val = getattr(new_obj, field.name, None)
            if old_val != new_val:
                changes[field.name] = (old_val, new_val)
    return changes


def _format_changes_for_comment(inst: Lid, changes: dict) -> str:
    """
    Build a single-line comment string with all changes.
    """
    parts = []
    for fname, (old_v, new_v) in changes.items():
        field = inst._meta.get_field(fname)
        parts.append(f'{fname}: "{_human(inst, field, old_v)}" → "{_human(inst, field, new_v)}"')
    return "; ".join(parts) if parts else None


# --- Signals ---------------------------------------------------------------

@receiver(pre_save, sender=Lid)
def lid_cache_changes(sender, instance: Lid, **kwargs):
    """
    Before saving: compute diffs vs DB row and stash on instance.
    """
    instance._changes = {}
    if not instance.pk:
        # new row; no diffs yet
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    instance._changes = _collect_changes(old, instance)


@receiver(post_save, sender=Lid)
def lid_log_after_save(sender, instance: Lid, created, **kwargs):
    """
    After saving:
    - If created -> log Created
    - Else -> build a single log with all changed fields in comment
    """
    if created:
        Log.objects.create(
            app="Lid",
            model="Lid",
            action="Log",
            model_action="Created",
            lid=instance,
        )
        return

    changes = getattr(instance, "_changes", {}) or {}
    if not changes:
        # Nothing changed (or was updated via .update())
        return

    comment = _format_changes_for_comment(instance, changes)

    Log.objects.create(
        app="Lid",
        model="Lid",
        action="Log",
        model_action="Updated",
        lid=instance,
        comment=comment,
    )


# --- Optional: track M2M changes on Lid.file -------------------------------

@receiver(m2m_changed, sender=Lid.file.through)
def lid_file_m2m_changed(sender, instance: Lid, action, reverse, pk_set, **kwargs):
    """
    Logs additions/removals to the `file` M2M.
    """
    if action not in {"post_add", "post_remove"} or not pk_set:
        return

    verb = "added" if action == "post_add" else "removed"
    from data.upload.models import File
    try:
        files = File.objects.filter(pk__in=pk_set)
        listed = ", ".join(str(f) for f in files[:10])
        extra = "" if len(pk_set) <= 10 else f" (+{len(pk_set) - 10} more)"
        comment = f"M2M file {verb}: {listed}{extra}"
    except Exception:
        comment = f"M2M file {verb}: {len(pk_set)} items"

    Log.objects.create(
        app="Lid",
        model="Lid",
        action="Log",
        model_action="Updated",
        lid=instance,
        comment=comment,
    )
