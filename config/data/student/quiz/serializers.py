import random

from icecream import ic
from rest_framework import serializers

from .models import Quiz, Question, Answer, Fill_gaps, Vocabulary, MatchPairs, Exam, Gaps, \
    QuizGaps, Pairs, ExamRegistration, ObjectiveTest, Cloze_Test, True_False, ImageObjectiveTest, ExamCertificate, \
    ExamSubject
from .tasks import handle_task_creation
from ..homeworks.models import Homework
from ..subject.models import Subject, Theme
from ..subject.serializers import SubjectSerializer, ThemeSerializer
from ...account.models import CustomUser
from ...finances.finance.models import Finance, Kind
from ...notifications.models import Notification
from ...parents.models import Relatives
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=Answer.objects.all())
    text = serializers.PrimaryKeyRelatedField(queryset=QuizGaps.objects.all())
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = Question
        fields = ["id", "quiz", "text", "file", "answers", "comment"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["text"] = QuizGapsSerializer(instance.text).data

        # Randomize answers for regular questions
        answers_data = AnswerSerializer(instance.answers.all(), many=True).data
        random.shuffle(answers_data)
        rep["answers"] = answers_data
        if instance.file:
            rep["file"] = FileUploadSerializer(instance.file, context=self.context).data
        return rep


class QuizGapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizGaps
        fields = [
            "id",
            "name",
            "created_at"
        ]


class ObjectiveTestSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), allow_null=True)
    question = serializers.PrimaryKeyRelatedField(queryset=QuizGaps.objects.all(), allow_null=True)
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=Answer.objects.all(), allow_null=True)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = ObjectiveTest
        fields = [
            "id",
            "quiz",
            "question",
            "answers",
            "comment",
            "file",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Randomize answers for objective tests
        rep["question"] = QuizGapsSerializer(instance.question).data

        if instance.answers.exists():
            answers_data = AnswerSerializer(instance.answers.all(), many=True).data
            random.shuffle(answers_data)
            rep["answers"] = answers_data
        if instance.file:
            rep["file"] = FileUploadSerializer(instance.file, context=self.context).data
        return rep


class Cloze_TestSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(many=True, queryset=QuizGaps.objects.all(), allow_null=True)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    sentence = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all(), allow_null=True)

    class Meta:
        model = Cloze_Test
        fields = [
            "id",
            "quiz",
            "questions",
            "sentence",
            "comment",
            "file",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["questions"] = QuizGapsSerializer(instance.questions.all(), many=True).data
        if instance.file:
            rep["file"] = FileUploadSerializer(instance.file, context=self.context).data

        if instance.sentence:
            rep["sentence"] = AnswerSerializer(instance.sentence).data

        return rep


class ImageObjectiveTestSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = ImageObjectiveTest
        fields = [
            "id",
            "quiz",
            "image",
            "answer",
            "comment",
            "created_at",
            "file"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.image:
            rep["image"] = FileUploadSerializer(instance.image, context=self.context).data
        else:
            rep["image"] = None

        if hasattr(instance, 'answers') and instance.answers.exists():
            answers_data = AnswerSerializer(instance.answers.all(), many=True).data
            random.shuffle(answers_data)
            rep["answers"] = answers_data
        if instance.file:
            rep["file"] = FileUploadSerializer(instance.file, context=self.context).data
        return rep


class True_FalseSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=QuizGaps.objects.all(), allow_null=True)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = True_False
        fields = [
            "id",
            "quiz",
            "question",
            "answer",
            "comment",
            "file"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep["question"] = QuizGapsSerializer(instance.question).data
        if instance.file:
            rep["file"] = FileUploadSerializer(instance.file, context=self.context).data
        return rep


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "theme",
            "homework",
            "subject",
            "questions",
            "count",
            "time",
            "created_at",
        ]

    def get_questions(self, obj):
        request = self.context.get("request")
        query_count = request.query_params.get("count") if request else None

        if query_count is not None and query_count.lower() == "false":
            count = None
        else:
            count = obj.count or 20

        questions = []

        for item in Question.objects.filter(quiz=obj):
            data = QuestionSerializer(item, context=self.context).data
            data["type"] = "standard"
            questions.append(data)

        for item in Vocabulary.objects.filter(quiz=obj):
            data = VocabularySerializer(item, context=self.context).data
            data["type"] = "vocabulary"
            questions.append(data)

        for item in MatchPairs.objects.filter(quiz=obj):
            data = MatchPairsSerializer(item, context=self.context).data
            data["type"] = "match_pairs"
            questions.append(data)

        for item in ObjectiveTest.objects.filter(quiz=obj):
            data = ObjectiveTestSerializer(item, context=self.context).data
            data["type"] = "objective_test"
            questions.append(data)

        for item in Cloze_Test.objects.filter(quiz=obj):
            data = Cloze_TestSerializer(item, context=self.context).data
            data["type"] = "cloze_test"
            questions.append(data)

        for item in ImageObjectiveTest.objects.filter(quiz=obj):
            data = ImageObjectiveTestSerializer(item, context=self.context).data
            data["type"] = "image_objective"
            questions.append(data)

        for item in True_False.objects.filter(quiz=obj):
            data = True_FalseSerializer(item, context=self.context).data
            data["type"] = "true_false"
            questions.append(data)

        random.shuffle(questions)

        if count is not None:
            return questions[:min(count, len(questions))]
        return questions

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject).data
        rep["theme"] = ThemeSerializer(instance.theme, include_only=["id", "title"]).data
        return rep


class QuizCheckingSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "theme",
            "homework",
            "subject",
            "questions",
            "count",
            "time",
            "created_at",
        ]

    def get_questions(self, obj):
        request = self.context.get("request")
        questions = []

        for item in Question.objects.filter(quiz=obj):
            data = QuestionSerializer(item, context=self.context).data
            data["type"] = "standard"
            questions.append(data)

        for item in Vocabulary.objects.filter(quiz=obj):
            data = VocabularySerializer(item, context=self.context).data
            data["type"] = "vocabulary"
            questions.append(data)

        for item in MatchPairs.objects.filter(quiz=obj):
            data = MatchPairsSerializer(item, context=self.context).data
            data["type"] = "match_pairs"
            questions.append(data)

        for item in ObjectiveTest.objects.filter(quiz=obj):
            data = ObjectiveTestSerializer(item, context=self.context).data
            data["type"] = "objective_test"
            questions.append(data)

        for item in Cloze_Test.objects.filter(quiz=obj):
            data = Cloze_TestSerializer(item, context=self.context).data
            data["type"] = "cloze_test"
            questions.append(data)

        for item in ImageObjectiveTest.objects.filter(quiz=obj):
            data = ImageObjectiveTestSerializer(item, context=self.context).data
            data["type"] = "image_objective"
            questions.append(data)

        for item in True_False.objects.filter(quiz=obj):
            data = True_FalseSerializer(item, context=self.context).data
            data["type"] = "true_false"
            questions.append(data)
        return questions

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject).data
        rep["theme"] = ThemeSerializer(instance.theme, include_only=["id", "title"]).data
        return rep

class GapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gaps
        fields = [
            "id",
            "name"
        ]


class FillGapsSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), allow_null=True)
    question = serializers.PrimaryKeyRelatedField(queryset=QuizGaps.objects.all(), allow_null=True)
    gaps = serializers.PrimaryKeyRelatedField(queryset=Gaps.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Fill_gaps
        fields = ["id", "quiz", "question", "gaps", "comment"]

    def create(self, validated_data):
        gaps_instances = []
        question_obj = validated_data.get("question")
        quiz = validated_data.get("quiz")

        if question_obj:
            for word in question_obj.name.split(" "):
                if word.startswith("[") and word.endswith("]"):
                    gap_word = word[1:-1]  # remove brackets
                    ic(gap_word)
                    gap = Gaps.objects.create(name=gap_word)
                    gaps_instances.append(gap)

        # Create the Fill_gaps instance first
        fill_gaps_instance = Fill_gaps.objects.create(
            quiz=quiz,
            question=question_obj,
        )

        # Set the M2M relation after instance is created
        fill_gaps_instance.gaps.set(gaps_instances)
        fill_gaps_instance.save()

        return fill_gaps_instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["question"] = QuizGapsSerializer(instance.question).data

        # Randomize gaps order for fill-in-the-blanks
        gaps_data = GapsSerializer(instance.gaps.all(), many=True).data
        random.shuffle(gaps_data)
        rep["gaps"] = gaps_data

        return rep


class VocabularySerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    voice = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = Vocabulary
        fields = [
            "id",
            "quiz",
            "photo",
            "voice",
            "in_english",
            "in_uzbek",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["photo"] = FileUploadSerializer(instance.photo, context=self.context).data
        rep["voice"] = FileUploadSerializer(instance.voice, context=self.context).data
        return rep


class PairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pairs
        fields = [
            "id",
            "pair",
            "choice",
            "key",
            "created_at",
        ]


class MatchPairsSerializer(serializers.ModelSerializer):
    pairs = serializers.PrimaryKeyRelatedField(queryset=Pairs.objects.all(), many=True, allow_null=True)

    class Meta:
        model = MatchPairs
        fields = [
            "id",
            "quiz",
            "pairs",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Randomize pairs for matching exercises
        pairs_data = PairsSerializer(instance.pairs.all(), many=True).data
        random.shuffle(pairs_data)
        rep["pairs"] = pairs_data

        return rep


class ExamSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), allow_null=True)
    # students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True, allow_null=True)
    materials = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    homework = serializers.PrimaryKeyRelatedField(queryset=Homework.objects.all(), allow_null=True)
    students_xml = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    results = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    student_count = serializers.SerializerMethodField()

    options = serializers.PrimaryKeyRelatedField(queryset=ExamSubject.objects.all(), many=True,allow_null=True)

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(ExamSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    class Meta:
        model = Exam
        fields = [
            "id",
            "quiz",
            "choice",
            "type",
            "is_mandatory",
            # "students",
            "students_xml",
            "materials",
            "results",
            "lang_foreign",
            "lang_national",
            "is_language",
            "student_count",
            "date",
            "start_time",
            "end_time",
            "homework",
            "options",
            "created_at",
        ]

    def get_student_count(self, instance):
        count = ExamRegistration.objects.filter(
            exam=instance,
            is_participating=True,
        ).count()
        return count

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["results"] = FileUploadSerializer(instance.results).data
        rep["options"] = {
            "subject":instance.subject.name,
            "option":instance.options,
        }
        return rep


class ExamRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRegistration
        fields = [
            "id",
            "student",
            "exam",
            "status",
            "is_participating",
            "mark",
            "student_comment",
            "has_certificate",
            "certificate",
            "created_at",
        ]

    def validate(self, attrs):
        exam = attrs.get("exam")
        student = attrs.get("student")

        if not exam:
            raise serializers.ValidationError({"exam": "Imtihon topilmadi."})

        if attrs.get("is_participating") == False:
            Notification.objects.create(
                user=student,
                comment=f"Siz {exam.date} sanasida tashkil qilingan offline imtihonda ishtirok etishni"
                        f" {attrs.get('student_comment')} sabab bilan inkor etdingiz.",
                choice="Examination",
                come_from=attrs.get("id")
            )
            kind = Kind.objects.get(name="Money back")

            Finance.objects.create(
                action="EXPENSE",
                amount=50000,
                kind=kind,
                attendance=None,
                student=student,
                stuff=None,
                comment=f"Siz {exam.date} sanasida tashkil qilingan offline imtihonda ishtirok etishni"
                        f" {attrs.get('student_comment')} sabab bilan inkor etdingiz va 50000 so'm Jarima berildi.",
            )
            parents = CustomUser.objects.filter(phone__in=Relatives.objects.filter(student=student).all())
            if parents:
                for parent in parents:
                    Notification.objects.create(
                        user=parent,
                        comment=f"Farzandingiz {exam.date} sanasida tashkil qilingan offline imtihonda ishtirok etishni"
                                f" {attrs.get('student_comment')} sabab bilan inkor etdi.",
                        choice="Examination",
                        come_from=attrs.get("id")
                    )

        # If less than 12 hours remain before the exam starts
        if attrs.get("status") == "Inactive":
            raise serializers.ValidationError({"exam": "Imtihondan ro'yxatdan o'tish vaqti yakunlangan."})

        if ExamRegistration.objects.filter(exam=exam, student=student).exists():
            raise serializers.ValidationError({"student": "Talaba allaqachon imtihon uchun ro'yxatdan o'tgan."})

        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        handle_task_creation.delay(instance.exam.id)

        if validated_data.get("has_certificate") == True and validated_data.get("certificate"):
            ExamCertificate.objects.create(
                student=instance.student,
                exam=instance.exam,
                status = "Pending",
                expire_date=instance.certificate_expire_date,
                certificate=validated_data.get("certificate"),
            )

        return instance


class ExamCertificateSerializer(serializers.ModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),allow_null=True,
    )
    class Meta:
        model = ExamCertificate
        fields = [
            "id",
            "student",
            "exam",
            "status",
            "certificate",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["certificate"] = FileUploadSerializer(instance.certificate,context=self.context).data
        return rep