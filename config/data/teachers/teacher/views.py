from django.db.models import Q, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TeacherSerializer
from ...account.models import CustomUser
from ...account.permission import FilialRestrictedQuerySetMixin
from ...exam_results.models import MockExamResult
from ...lid.new_lid.models import Lid
from ...results.models import Results
from ...student.groups.models import Group, SecondaryGroup
from ...student.groups.serializers import GroupSerializer, SecondaryGroupSerializer
from ...student.homeworks.models import Homework_history
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.mastering.models import Mastering, MasteringTeachers
from ...student.mastering.serializers import StuffMasteringSerializer
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...student.studentgroup.serializers import StudentsGroupSerializer
from ...student.subject.models import GroupThemeStart


class TeacherList(FilialRestrictedQuerySetMixin, ListCreateAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    # permission_classes = (IsAuthenticated,)


class TeacherDetail(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)


class TeachersNoPGList(ListAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)


class TeacherScheduleView(ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter lessons for the logged-in teacher
        return Lesson.objects.filter(group__teacher=self.request.user
                                     ).order_by("day", "start_time")


class TeacherStatistics(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer

    def get(self, request, *args, **kwargs):
        teacher = request.user
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        filters = {}
        if start_date:
            filters = {"created_at__gte": start_date}
        if end_date:
            filters["created_at__lte"] = end_date

        # Get all student IDs under this teacher
        student_ids = StudentGroup.objects.filter(group__teacher=teacher).values_list("student_id", flat=True)

        # Annotate average mastering score per student
        student_averages = (
            Mastering.objects
            .filter(student__in=student_ids)
            .values('student')
            .annotate(avg_ball=Avg('ball'))
        )

        if student_averages:
            total_avg = sum(s["avg_ball"] for s in student_averages) / len(student_averages)
            total_avg_scaled = min(max(round(total_avg / 20), 1), 5)
            low_assimilation_count = sum(1 for s in student_averages if s["avg_ball"] <= 40)
        else:
            total_avg_scaled = None
            low_assimilation_count = 0

        # statistics = {
        #     "all_students": StudentGroup.objects.filter(group__teacher=teacher, **filters).count(),
        #     "new_students": StudentGroup.objects.filter(group__teacher=teacher,
        #                                                 student__student_stage_type="NEW_STUDENT", **filters).count(),
        #     "education_stopped_students": StudentGroup.objects.filter(group__teacher=teacher,
        #                                                               student__is_archived=True, **filters).count(),
        #     "active_students": StudentGroup.objects.filter(group__teacher=teacher,
        #                                                    student__student_stage_type="ACTIVE_STUDENT", **filters).count(),
        #     "complaints": Complaint.objects.filter(user=teacher, **filters).count(),
        #     "results": Results.objects.filter(teacher=teacher, status="Accepted", **filters).count(),
        #     "average_assimilation": total_avg_scaled,
        #     "low_assimilation": low_assimilation_count,
        # }

        statistics1 = {
            "first_lesson": StudentGroup.objects.filter(
                student__isnull=True,
                lid__lid_stage_type="ORDERED_LID",
                lid__is_archived=False,
                is_archived=False,
                group__teacher=teacher,
                lid__ordered_stages="BIRINCHI_DARS_BELGILANGAN",
                lid__is_student=False
            ).count(),

            # "first_lesson_archived": StudentGroup.objects.filter(
            #     Q(lid__is_archived=False) | Q(is_archived=False),
            #     student__isnull=True,
            #     lid__lid_stage_type="ORDERED_LID",
            #     lid__ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            #     lid__is_student=False,
            #     group__teacher=teacher
            # ).count(),
            "first_lesson_archived":Lid.objects.filter(
                lid_stage_type="ORDERED_LID",
                ordered_stages="BIRINCHI_DARS_BELGILANGAN",
                is_archived=True,
                is_student=False,
                lids_group__group__teacher=teacher,
            ).count(),
            "all_students": StudentGroup.objects.filter(group__teacher=teacher, **filters).count(),
            "new_students": StudentGroup.objects.filter(group__teacher=teacher,
                                                        student__student_stage_type="NEW_STUDENT", **filters).count(),
            "new_student_active": StudentGroup.objects.filter(group__teacher=teacher,
                                                              student__student_stage_type="ACTIVE_STUDENT",
                                                              student__new_student_date__isnull=False,
                                                              **filters).count(),
            "new_student_archived": StudentGroup.objects.filter(group__teacher=teacher,
                                                                student__student_stage_type="NEW_STUDENT",
                                                                student__is_archived=True, **filters).count(),
            "new_student_still": StudentGroup.objects.filter(group__teacher=teacher,
                                                             student__student_stage_type="NEW_STUDENT",
                                                             student__is_archived=False, **filters).count(),
            "active_students": StudentGroup.objects.filter(group__teacher=teacher, student__is_archived=False,
                                                           student__student_stage_type="ACTIVE_STUDENT",
                                                           **filters).count(),

            "results": Results.objects.filter(teacher=teacher, **filters).count(),
            "results_progress": Results.objects.filter(teacher=teacher, status="In_progress", **filters).count(),
            "results_accepted": Results.objects.filter(teacher=teacher, status="Accepted", **filters).count(),
            "results_rejected": Results.objects.filter(teacher=teacher, status="Rejected", **filters).count(),

            "average_assimilation": total_avg_scaled,
            "low_assimilation": low_assimilation_count,
        }

        return Response(statistics1)


class Teacher_StudentsView(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name")

    def get_queryset(self):

        status = self.request.GET.get("status", None)
        is_archived = self.request.GET.get("is_archived", None)

        group = StudentGroup.objects.filter(group__teacher=self.request.user,)

        if is_archived:
            group = group.filter(
                Q(lid__is_archived=is_archived.capitalize())  |  Q(
                    student__is_archived=is_archived.capitalize()))
        if status:
            group = group.filter(Q(student__student_stage_type=status) | Q(lid__lid_stage_type=status))
        if group:
            return group.distinct()
        return StudentGroup.objects.none()


class TeachersGroupsView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')
    ordering_fields = (
        "lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status', 'student_count')
    filterser_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')

    def get_queryset(self):
        status = self.request.GET.get("status")
        teacher_id = self.request.user.pk

        queryset = Group.objects.filter(
            Q(teacher__id=teacher_id) | Q(secondary_teacher__id=teacher_id)
        ).annotate(
            student_count=Count("student_groups")
        )
        if status:
            queryset = queryset.filter(status=status)

        # if ordering:
        #     queryset = queryset.order_by(ordering)

        return queryset.order_by("-student_count")


class AssistantTeachersView(ListAPIView):
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.GET.get("status")
        teacher_id = self.request.user.pk
        queryset = SecondaryGroup.objects.filter(teacher__id=teacher_id)
        if status:
            queryset = queryset.filter(status=status)
        ordering = self.request.GET.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class AssistantStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        filters = {}
        if start_date:
            filters["created_at__gte"] = start_date

        if end_date:
            filters["created_at__lte"] = end_date

        students = SecondaryStudentGroup.objects.filter(group__teacher=self.request.user, **filters).count()
        average_assimilation = None
        low_assimilation = None
        high_assimilation = None

        statistics = {
            "students": students,
            "average_assimilation": average_assimilation,
            "high_assimilation": high_assimilation,
            "low_assimilation": low_assimilation
        }
        return Response(statistics)


class TeacherMasteringStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MasteringTeachers.objects.all()
    serializer_class = StuffMasteringSerializer

    def get_queryset(self):
        queryset = MasteringTeachers.objects.filter(teacher=self.request.user)
        if queryset:
            return queryset
        return Mastering.objects.none()


class SecondaryGroupStatic(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        base_qs = SecondaryStudentGroup.objects.filter(group__teacher=request.user)

        all_count = base_qs.count()
        first_count = base_qs.filter(lid__isnull=False).count()
        new_student_count = base_qs.filter(student__student_stage_type="NEW_STUDENT").count()
        active_count = base_qs.filter(student__student_stage_type="ACTIVE_STUDENT").count()

        return Response({
            "all": all_count,
            "first": first_count,
            "new_student": new_student_count,
            "active": active_count
        })


class StudentsAvgLearning(APIView):
    def get(self, request, *args, **kwargs):
        group_id = request.query_params.get("group")

        if not group_id:
            return Response({"error": "group parameter is required"}, status=400)

        # Get the theme that marks the limit
        current_theme = GroupThemeStart.objects.filter(group__id=group_id).order_by('-created_at').first()

        student_groups = StudentGroup.objects.filter(
            group__id=group_id,
        ).select_related("student", "lid")

        student_ids = [sg.student.id for sg in student_groups if sg.student]
        lid_ids = [sg.lid.id for sg in student_groups if sg.lid]

        mastering_filter = Q(student__id__in=student_ids) | Q(lid__id__in=lid_ids)

        if current_theme and current_theme.theme:
            mastering_filter &= Q(theme__created_at__lte=current_theme.theme.created_at)

        mastering_records = Mastering.objects.filter(
            mastering_filter
        ).select_related("student", "lid", "test", "theme").distinct()

        results = []

        for sg in student_groups:
            target_id = sg.student.id if sg.student else sg.lid.id
            is_student = bool(sg.student)

            if is_student:
                student_record = mastering_records.filter(student__id=target_id)
                name = {
                    'full_name': f"{sg.student.first_name} {sg.student.last_name}",
                    "type": "student",
                    'is_archived': sg.student.is_archived,
                    'is_frozen': sg.student.is_frozen,
                    'frozen_date': sg.student.frozen_days,
                }
            else:
                student_record = mastering_records.filter(lid__id=target_id)
                name = {
                    'full_name': f"{sg.lid.first_name} {sg.lid.last_name}",
                    'type': 'lid',
                    'is_archived': sg.lid.is_archived,
                    'is_frozen': sg.lid.is_frozen,
                }

            exams, homeworks, speaking, unit, mock, mid_course, level = [], [], [], [], [], [], []

            for m in student_record:
                homework_id = Homework_history.objects.filter(
                    homework__theme=m.theme,
                    student=m.student,
                ).first()

                mock_data = None
                if m.mock:
                    mock_result = MockExamResult.objects.filter(student=m.student, mock=m.moc).first()
                    if mock_result:
                        mock_data = {
                            "id": mock_result.id,
                            "reading": mock_result.reading,
                            "listening": mock_result.listening,
                            "writing": mock_result.writing,
                            "speaking": mock_result.speaking,
                            "overall_score": mock_result.overall_score,
                            "updater": {
                                "id": mock_result.updater.id,
                                "full_name": f"{mock_result.updater.first_name} {mock_result.updater.last_name}",
                            } if mock_result.updater else None,
                            "created_at": mock_result.created_at.isoformat(),
                        }

                item = {
                    "theme": {
                        "id": m.theme.id,
                        "name": m.theme.title,
                    } if m.theme else None,
                    "homework_id": homework_id.id if homework_id else None,
                    "mastering_id": m.id if m.choice in ["Speaking", "Unit_Test", "Mock", "MidCourse",
                                                         "Level"] else None,
                    "title": m.test.title if m.test else "N/A",
                    "mock": mock_data if mock_data is not None else m.level_exam.id if m.level_exam else None,
                    "ball": m.ball,
                    "type": m.test.type if m.test else "unknown",
                    "updater": homework_id.updater.full_name if homework_id and homework_id.updater else
                    m.updater.full_name if m.choice in ["Speaking", "Unit_Test", "MidCourse",
                                                        "Level"] and m.updater else "N/A",
                    "created_at": m.created_at,
                }

                if m.test and m.test.type == "Offline" and m.choice == "Test":
                    exams.append(item)
                elif m.choice == "Speaking":
                    speaking.append(item)
                elif m.choice == "Unit_Test":
                    unit.append(item)
                elif m.choice == "Mock":
                    mock.append(item)
                elif m.choice == "MidCourse":
                    mid_course.append(item)
                elif m.choice == "Level":
                    level.append(item)
                else:
                    homeworks.append(item)

            def avg(lst):
                return round(sum(x['ball'] for x in lst) / len(lst), 2) if lst else 0

            overall_exam = avg(exams)
            overall_homework = avg(homeworks)
            overall_speaking = avg(speaking)
            overall_unit = avg(unit)
            overall_mock = avg(mock)
            overall_mid_course = avg(mid_course)
            overall_level = avg(level)

            all_parts = [overall_exam, overall_homework, overall_speaking, overall_unit, overall_mock,
                         overall_mid_course, overall_level]
            filled = [p for p in all_parts if p > 0]
            overall = round(sum(filled) / len(filled), 2) if filled else 0

            first_ball = sg.student.ball if is_student and sg.student.ball else 0

            results.append({
                "id": target_id,
                "user": name,
                "first_ball": first_ball,
                "exams": {"items": exams, "overall": overall_exam},
                "homeworks": {"items": homeworks, "overall": overall_homework},
                "speaking": {"items": speaking, "overall": overall_speaking},
                "unit_test": {"items": unit, "overall": overall_unit},
                "mock": {"items": mock, "overall": overall_mock},
                "mid_course": {"items": mid_course, "overall": overall_mid_course},
                "level": {"items": level, "overall": overall_level},
                "overall": overall
            })

        return Response(results)
