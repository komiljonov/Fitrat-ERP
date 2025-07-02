
from rest_framework import serializers

from .models import UnitTest, UnitTestResult, QuizResult, MockExam, MockExamResult
from ..student.course.models import Course
from ..student.groups.models import Group
from ..student.mastering.models import Mastering
from ..student.quiz.models import Quiz, Exam
from ..student.quiz.serializers import QuestionSerializer, MatchPairsSerializer, True_FalseSerializer, \
    VocabularySerializer, ObjectiveTestSerializer, Cloze_TestSerializer, ImageObjectiveTestSerializer
from ..student.student.models import Student
from ..student.student.serializers import StudentSerializer
from ..student.studentgroup.models import StudentGroup
from ..student.subject.models import Theme, Subject
from ..student.subject.serializers import ThemeSerializer, SubjectSerializer


class UnitTestSerializer(serializers.ModelSerializer):
    themes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Theme.objects.all(),
        required=False
    )
    theme_after = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(), allow_null=True, required=False
    )
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = UnitTest
        fields = [
            "id",
            "theme_after",
            "themes",
            "quiz",
            "group",
            "created_at"
        ]

    def create(self, validated_data):
        themes = validated_data.pop("themes", [])
        unit_test = UnitTest.objects.create(**validated_data)
        unit_test.themes.set(themes)

        # Create mastering records for all students in the group
        students = StudentGroup.objects.filter(
            group=unit_test.group, student__isnull=False
        ).select_related("student")

        for sg in students:
            Mastering.objects.create(
                theme=None,
                student=sg.student,
                test=unit_test.quiz,
                choice="Unit_Test"
            )

        return unit_test

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["themes"] = ThemeSerializer(instance.themes.all(), many=True).data
        rep["theme_after"] = (
            ThemeSerializer(instance.theme_after).data if instance.theme_after else None
        )
        return rep


class UnitTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitTestResult
        fields = [
            "id",
            "student",
            "unit",
            "point",
            "created_at"
        ]


class QuizResultSerializer(serializers.ModelSerializer):
    # Write-only fields for incoming UUID lists

    student = serializers.CharField(write_only=True, required=False)

    quiz_id = serializers.CharField(write_only=True, required=False)

    match_pair = serializers.ListField(write_only=True, required=False)
    true_false = serializers.ListField(write_only=True, required=False)
    questions = serializers.ListField(write_only=True, required=False)
    cloze_test = serializers.ListField(write_only=True, required=False)
    objective = serializers.ListField(write_only=True, required=False)
    image_objective = serializers.ListField(write_only=True, required=False)
    vocabulary = serializers.ListField(write_only=True, required=False)

    # Read-only output fields
    standard = serializers.SerializerMethodField()
    match_pair_result = serializers.SerializerMethodField()
    true_false_result = serializers.SerializerMethodField()
    vocabulary_result = serializers.SerializerMethodField()
    objective_result = serializers.SerializerMethodField()
    cloze_test_result = serializers.SerializerMethodField()
    image_objective_result = serializers.SerializerMethodField()

    total_question_count = serializers.SerializerMethodField()
    class Meta:
        model = QuizResult
        fields = [
            "id", "student", "point", "created_at", "quiz_id",
            "questions", "match_pair", "true_false", "vocabulary",
            "objective", "cloze_test", "image_objective",
            "standard", "match_pair_result", "true_false_result",
            "vocabulary_result", "objective_result","total_question_count",
            "cloze_test_result", "image_objective_result"
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        student_input = validated_data.pop("student", None)

        student = None
        if student_input:
            student = Student.objects.filter(user__id=student_input).first()
        elif request and hasattr(request.user, "student"):
            student = Student.objects.filter(user=request.user).first()

        quiz = validated_data.pop("quiz_id", None)
        quiz = Quiz.objects.filter(id=quiz).first()

        if not student:
            raise serializers.ValidationError("Valid student could not be resolved from input or request.")

        quiz_result = QuizResult.objects.create(student=student, quiz=quiz)

        # Assign M2M fields if provided
        m2m_fields = [
            ("match_pair", "match_pair"),
            ("true_false", "true_false"),
            ("questions", "questions"),
            ("cloze_test", "cloze_test"),
            ("objective", "objective"),
            ("image_objective", "image_objective"),
            ("vocabulary", "vocabulary"),
        ]
        for key, attr in m2m_fields:
            if key in validated_data:
                getattr(quiz_result, attr).set(validated_data[key])
        return quiz_result

    def get_total_question_count(self, obj):
        return (
                obj.questions.count() +
                obj.match_pair.count() +
                obj.true_false.count() +
                obj.vocabulary.count() +
                obj.objective.count() +
                obj.cloze_test.count() +
                obj.image_objective.count()
        )

    # Read methods for result representation
    def get_standard(self, obj):
        return QuestionSerializer(obj.questions.all(),context=self.context, many=True).data

    def get_match_pair_result(self, obj):
        return MatchPairsSerializer(obj.match_pair.all(),context=self.context, many=True).data

    def get_true_false_result(self, obj):
        return True_FalseSerializer(obj.true_false.all(),context=self.context, many=True).data

    def get_vocabulary_result(self, obj):
        return VocabularySerializer(obj.vocabulary.all(),context=self.context, many=True).data

    def get_objective_result(self, obj):
        return ObjectiveTestSerializer(obj.objective.all(),context=self.context, many=True).data

    def get_cloze_test_result(self, obj):
        return Cloze_TestSerializer(obj.cloze_test.all(),context=self.context, many=True).data

    def get_image_objective_result(self, obj):
        return ImageObjectiveTestSerializer(obj.image_objective.all(),context=self.context, many=True).data


class MockExamSerializer(serializers.ModelSerializer):

    options = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),allow_null=True, required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), allow_null=True, required=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True, required=False)

    class Meta:
        model = MockExam
        fields = [
            "id",
            "options",
            "course",
            "group",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "created_at"
        ]

    def create(self, validated_data):
        group = validated_data.get("group")
        if group:
            students = StudentGroup.objects.filter(group=group)
            for student in students:
                mastering = MockExamResult.objects.create(
                    mock=self.instance,
                    student=student.student if student.student else None,
                    overall_score=0
                )
                print(mastering)

        return super().create(validated_data)



    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep["options"] = SubjectSerializer(instance.options,context=self.context).data
        rep["group"] = {
            "id": instance.group.id,
            "name" : instance.group.name,
        } if instance.group else None
        rep["course"] = {
            "id": instance.course.id,
            "name" : instance.course.name,
        } if instance.course else None

        return rep



class MockExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockExamResult
        fields = [
            "id",
            "student",
            "mock",
            "reading",
            "listening",
            "writing",
            "speaking",
            "overall_score",
            "created_at",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instance.mock and instance.student:
            instance.overall_score = (
                instance.reading + instance.listening + instance.writing + instance.speaking
            ) / 4
            instance.save()

            Mastering.objects.create(
                student=instance.student,
                lid=None,
                theme=None,
                test=None,
                choice="Mock",
                ball=instance.overall_score,
            )

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = {
            "id": instance.student.id,
            "full_name": f"{instance.student.first_name} ({instance.student.last_name})",
        }
        return rep