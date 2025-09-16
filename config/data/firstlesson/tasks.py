from django.db.models import Q


from celery import shared_task


from data.firstlesson.models import FirstLesson


@shared_task
def recreate_first_lesson():

    first_lessons = FirstLesson.objects.filter(
        Q(status="DIDNTCOME") | Q(status="PENDING"),
        is_archived=False,
    )

    for lesson in first_lessons:
        if lesson.lesson_number == 3:
            lesson.is_archived = True
            lesson.save()
            continue

        lesson.pk = None
        # lesson.date = 
