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
from ...results.models import Results
from ...student.groups.models import Group, SecondaryGroup
from ...student.groups.serializers import GroupSerializer, SecondaryGroupSerializer
from ...student.homeworks.models import Homework_history
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.mastering.models import Mastering, MasteringTeachers
from ...student.mastering.serializers import StuffMasteringSerializer
from ...student.student.models import Student
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...student.studentgroup.serializers import StudentsGroupSerializer
from ...lid.new_lid.models import Lid

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
            "first_lesson": Lid.objects.filter(
                lid_stage_type="ORDERED_LID",
                is_archived=False,
                lids_group__group__teacher=teacher,
                ordered_stages="BIRINCHI_DARS_BELGILANGAN",
                is_student=False
            ).count(),
            "first_lesson_archived" : Lid.objects.filter(
                lid_stage_type="ORDERED_LID",
                is_archived=True,
                lids_group__group__teacher=teacher,
                ordered_stages="BIRINCHI_DARS_BELGILANGAN",
                is_student=False,
            ).count(),
            "all_students": StudentGroup.objects.filter(group__teacher=teacher, **filters).count(),
            "new_students": StudentGroup.objects.filter(group__teacher=teacher,
                                                        student__student_stage_type="NEW_STUDENT", **filters).count(),
            "new_student_active" : StudentGroup.objects.filter(group__teacher=teacher,student__student_stage_type="ACTIVE_STUDENT",
                                                               student__new_student_date__isnull=False, **filters).count(),
            "new_student_archived" : StudentGroup.objects.filter(group__teacher=teacher,student__student_stage_type="NEW_STUDENT",
                                                                 student__is_archived=True, **filters).count(),
            "new_student_still" : StudentGroup.objects.filter(group__teacher=teacher,student__student_stage_type="NEW_STUDENT",
                                                              student__is_archived=False, **filters).count(),

            "active_students": StudentGroup.objects.filter(group__teacher=teacher,student__is_archived=False,
                                                           student__student_stage_type="ACTIVE_STUDENT",
                                                           **filters).count(),

            "results": Results.objects.filter(teacher=teacher, **filters).count(),
            "results_progress" : Results.objects.filter(teacher=teacher,status="In_progress", **filters).count(),
            "results_accepted" : Results.objects.filter(teacher=teacher,status="Accepted", **filters).count(),
            "results_rejected" : Results.objects.filter(teacher=teacher,status="Rejected",**filters).count(),

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

        students = self.request.GET.get("status", None)

        group = StudentGroup.objects.filter(group__teacher=self.request.user)

        if students:
            group = group.filter(student__student_stage_type=students)
        if group:
            return group
        return StudentGroup.objects.none()


class TeachersGroupsView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')
    ordering_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status', 'student_count')
    filterser_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')

    def get_queryset(self):
        status = self.request.GET.get("status")
        teacher_id = self.request.user.pk  # Get the teacher ID
        # ordering = self.request.GET.get("ordering")

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

        students = SecondaryStudentGroup.objects.filter(group__teacher=self.request.user,**filters).count()
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

        student_groups = StudentGroup.objects.filter(
            group__id=group_id,
        ).select_related("student", "lid").distinct()

        student_ids = [sg.student.id for sg in student_groups if sg.student]
        lid_ids = [sg.lid.id for sg in student_groups if sg.lid]

        mastering_records = Mastering.objects.filter(
            Q(student__id__in=student_ids) | Q(lid__id__in=lid_ids)
        ).select_related("student", "lid", "test")

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

            exams = []
            homeworks = []
            speaking = []
            unit = []
            mock=[]

            for m in student_record:
                homework_id = Homework_history.objects.filter(
                    homework__theme=m.theme,
                    student=m.student,
                ).first()

                mock_records_data = None
                if m.mock:
                    mock_result = MockExamResult.objects.filter(student=m.student, mock=m.mock).first()
                    if mock_result:
                        mock_records_data = {
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

                theme_data = {
                    "id": m.theme.id,
                    "name": m.theme.title,
                } if m.theme else None

                # full_name = getattr(mock_records_data.get("updater"), "full_name", "Unknown")
                item = {
                    "theme" : theme_data,
                    "homework_id": homework_id.id if homework_id else None,
                    "mastering_id": m.id if m.choice in ["Speaking","Unit_Test","Mock"] else None,
                    "title": m.test.title if m.test else "N/A",
                    "mock":mock_records_data,
                    "ball": m.ball,
                    "type": m.test.type if m.test else "unknown",
                    "updater" : homework_id.updater.full_name if homework_id and homework_id.updater else
                    m.updater.full_name if m.choice in ["Speaking","Unit_Test"] and m.updater is not None
                    else "N/A",
                    "created_at": m.created_at
                }
                if m.test and m.test.type == "Offline" and m.choice=="Test":
                    exams.append(item)
                elif m.choice=="Speaking":
                    speaking.append(item)
                elif m.choice=="Unit_Test":
                    unit.append(item)
                elif m.choice=="Mock":
                    mock.append(item)
                else:
                    homeworks.append(item)

            # Sort homework items by created_at (newest first)
            # homeworks.sort(key=lambda x: x['created_at'], reverse=True)
            # exams.sort(key=lambda x: x['created_at'], reverse=True)

            overall_exam = sum(x['ball'] for x in exams) / len(exams) if exams else 0
            overall_homework = sum(x['ball'] for x in homeworks) / len(homeworks) if homeworks else 0
            overall_speaking = sum(x['ball'] for x in speaking) / len(speaking) if speaking else 0
            overall_unit = sum(x['ball'] for x in unit) / len(unit) if unit else 0
            overall_mock = sum(x['ball'] for x in mock) / len(mock) if mock else 0
            overall = round((overall_exam + overall_homework + overall_speaking + overall_unit + overall_mock) / 5, 2) if exams or homeworks or speaking or unit else 0

            first_ball = Student.objects.filter(id=sg.student.id).first() if sg.student else None

            results.append({
                "id":target_id,
                "user": name,
                "first_ball":first_ball.ball if first_ball else 0,
                "exams": {
                    "items": exams,
                    "overall": round(overall_exam, 2)
                },
                "homeworks": {
                    "items": homeworks,
                    "overall": round(overall_homework, 2)
                },
                "speaking": {
                    "items": speaking,
                    "overall": round(overall_speaking, 2)
                },
                "unit_test": {
                    "items": unit,
                    "overall": round(overall_unit, 2)
                },
                "mock": {
                    "items":mock,
                    "overall": round(overall_mock,2)
                },
                "overall": overall
            })

        return Response(results)
