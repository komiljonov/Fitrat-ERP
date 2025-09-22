from django.db import transaction
from django.db.models import Q
from django.utils import timezone  # NEW


from celery import shared_task

from data.firstlesson.models import FirstLesson
from data.student.studentgroup.models import StudentGroup

from data.student.groups.utils import next_lesson_date


@shared_task
def recreate_first_lesson():
    """
    Recreate next 'first lesson' for all active lessons with status in {PENDING, DIDNTCOME}.
    - If lesson_number >= 3 → archive and stop retrying.
    - Otherwise clone the row (pk=None), bump lesson_number, reset status to PENDING,
      move all StudentGroup links (formerly pointing to old lesson) to the new lesson,
      and (optionally) archive the old row.
    """

    qs = (
        FirstLesson.objects.filter(
            Q(status__in=["PENDING", "DIDNTCOME"]),
            is_archived=False,
            date__lt=timezone.now(),
        )
        .select_related("group")
        .order_by("id")  # deterministic
    )

    for orig in qs.iterator(chunk_size=500):
        # One-row transactional lock to avoid duplicate work across workers
        with transaction.atomic():
            try:
                orig = FirstLesson.objects.select_for_update(skip_locked=True).get(
                    pk=orig.pk
                )
            except FirstLesson.DoesNotExist:
                continue  # it was processed by another worker

            # Re-check current state after lock
            if (
                orig.is_archived
                or orig.status not in {"PENDING", "DIDNTCOME"}
                or orig.date >= timezone.now()  # NEW: skip if lesson is in the future
            ):
                continue

            attempts = getattr(orig, "lesson_number", 1)
            if attempts >= 3:
                # Max attempts reached → archive and stop
                orig.is_archived = True
                orig.save(update_fields=["is_archived", "updated_at"])
                continue

            # Pull group's scheduled weekdays (1=Mon..7=Sun)
            weekdays = list(
                orig.group.scheduled_day_type.values_list("index", flat=True)
            )
            if not weekdays:
                # No schedule → nothing to recreate
                continue

            # Compute next strictly-after date
            next_dt = next_lesson_date(orig.date, weekdays)
            if not next_dt:
                # Defensive (shouldn't happen if weekdays non-empty)
                continue

            # --- Clone via pk=None ---
            old_pk = orig.pk

            # If you have unique fields (slug/code), regenerate them before save.
            orig.pk = None
            orig.id = None  # defensive
            orig.date = next_dt
            orig.status = "PENDING"
            setattr(orig, "lesson_number", attempts + 1)
            orig.is_archived = False
            orig.save()  # now 'orig' refers to the NEW row

            new_lesson = orig  # for clarity

            # Repoint all StudentGroup records from the OLD lesson to the NEW one
            StudentGroup.objects.filter(first_lesson_id=old_pk).update(
                first_lesson=new_lesson
            )

            # (Optional but typical) archive the previous attempt so only the newest is active
            FirstLesson.objects.filter(pk=old_pk).update(
                is_archived=True, archived_at=timezone.now()
            )
