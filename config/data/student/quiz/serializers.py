import logging
import random

from icecream import ic
from rest_framework import serializers

from .models import Quiz, Question, Answer, Fill_gaps, Vocabulary, MatchPairs, Exam, Gaps, \
    QuizGaps, Pairs, ExamRegistration, ObjectiveTest, Cloze_Test, True_False, ImageObjectiveTest, ExamCertificate, \
    ExamSubject
from ..groups.models import Group
from ..homeworks.models import Homework
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..subject.models import Subject, Theme
from ..subject.serializers import SubjectSerializer, ThemeSerializer
from ...account.models import CustomUser
from ...exam_results.models import QuizResult
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
            sentence_text = instance.sentence.text if hasattr(instance.sentence, 'text') else ''
            words = sentence_text.split()
            random.shuffle(words)
            rep["sentence"] = {
                "id": str(instance.sentence.id),
                "shuffled_words": words
            }

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

        if instance.answer:
            answers_data = AnswerSerializer(instance.answer).data
            rep["answer"] = answers_data.get("text")
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
            "id", "title", "description", "theme", "homework", "subject",
            "questions", "count", "time", "created_at",
        ]

    def get_questions(self, obj):
        request = self.context.get("request")
        query_count = request.query_params.get("count") if request else None
        student = request.user.student if request and hasattr(request.user, 'student') else None

        if query_count is not None and query_count.lower() == "false":
            count = None
        else:
            count = obj.count or 20

        questions = []
        seen_questions = set()  # Track (type, id) tuples to avoid duplicates
        quiz_result = None

        # Create or get QuizResult instance if student exists
        if student:
            quiz_result, created = QuizResult.objects.get_or_create(
                quiz=obj,
                student=student,
                defaults={'point': 0}
            )

        # Define question types and associated serializers & M2M fields
        question_types = [
            (Question, QuestionSerializer, "standard", "questions"),
            (Vocabulary, VocabularySerializer, "vocabulary", "vocabulary"),
            (MatchPairs, MatchPairsSerializer, "match_pair", "match_pair"),
            (ObjectiveTest, ObjectiveTestSerializer, "objective_test", "objective_test"),
            (Cloze_Test, Cloze_TestSerializer, "cloze_test", None),  # No M2M for cloze
            (ImageObjectiveTest, ImageObjectiveTestSerializer, "image_objective", "image_objective"),
            (True_False, True_FalseSerializer, "true_false", "true_false"),
        ]

        for model, serializer_class, qtype, relation_field in question_types:
            items = model.objects.filter(quiz=obj)
            for item in items:
                key = (qtype, item.id)
                if key in seen_questions:
                    continue  # Skip if already seen
                seen_questions.add(key)

                data = serializer_class(item, context=self.context).data
                data["type"] = qtype
                questions.append(data)

                if student and quiz_result and relation_field:
                    m2m_field = getattr(quiz_result, relation_field)
                    m2m_field.add(item)

        random.shuffle(questions)

        if count is not None:
            questions = questions[:min(count, len(questions))]

        # Update question count in QuizResult if it exists
        if student and quiz_result:
            quiz_result.point = len(questions)  # Or use your own logic
            quiz_result.save()

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
            data["type"] = "match_pair"
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


class ExamSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubject
        fields = [
            "id",
            "subject",
            "options",
            "lang_foreign",
            "lang_national",
            "order",
            "has_certificate",
            "certificate",
            "certificate_expire_date",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        student = Student.objects.filter(user=user).first()

        # Create the ExamSubject object
        exam_subject = ExamSubject.objects.create(**validated_data)

        # Fetch related ExamRegistration
        option_ids = [exam_subject.id]  # since `id` is the primary key of the created object
        exam = ExamRegistration.objects.filter(
            student=student,
            option__in=option_ids
        ).first()

        # If there's a certificate to attach
        if validated_data.get("has_certificate") and validated_data.get("certificate"):
            ExamCertificate.objects.create(
                student=student,
                certificate=validated_data["certificate"],
                exam=exam
            )
            logging.info("Exam Certificate created")

        return exam_subject  # ✅ Return the correct instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = {
            "id": instance.subject.id,
            "name": instance.subject.name,
            "is_language": instance.subject.is_language,
        } if instance.subject else None
        rep["certificate"] = FileUploadSerializer(instance.certificate,
        context=self.context).data if instance.certificate else None

        return rep


class ExamSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), allow_null=True)
    # students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True, allow_null=True)
    materials = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    homework = serializers.PrimaryKeyRelatedField(queryset=Homework.objects.all(), allow_null=True)
    students_xml = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    results = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    student_count = serializers.SerializerMethodField()

    options = serializers.PrimaryKeyRelatedField(queryset=ExamSubject.objects.all(), many=True, allow_null=True)

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
            "name",
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
        request = self.context.get("request")
        user = request.user

        rep = super().to_representation(instance)
        rep["results"] = FileUploadSerializer(instance.results).data if instance.results else None

        if user.role == "TEACHER":
            teacher_subject = Group.objects.filter(teacher=user).first().course.subject

            teacher_exam_subjects = ExamSubject.objects.filter(subject=teacher_subject)

            options_list = []
            for exam_subject in teacher_exam_subjects:
                if exam_subject.lang_national and exam_subject.lang_foreign:
                    lang_value = "both"
                elif exam_subject.lang_national:
                    lang_value = "national"
                elif exam_subject.lang_foreign:
                    lang_value = "foreign"
                else:
                    lang_value = None

                options_list.append({
                    "instance_id": exam_subject.id,
                    "id": exam_subject.subject.id,
                    "subject": exam_subject.subject.name,
                    "lang_type": lang_value,
                    "option": exam_subject.options,
                })

            rep["options"] = options_list

        else:
            rep["options"] = ExamSubjectSerializer(instance.options, many=True).data

        return rep


class ExamRegistrationSerializer(serializers.ModelSerializer):
    option = serializers.PrimaryKeyRelatedField(
        queryset=ExamSubject.objects.all(), many=True, allow_null=True,required=False
    )

    date = serializers.SerializerMethodField()
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all(), allow_null=True, required=False)

    class Meta:
        model = ExamRegistration
        fields = [
            "id",
            "student",
            "exam",
            "status",
            "group",
            "variation",
            "is_participating",
            "mark",
            "option",
            "student_comment",
            "date",
            "created_at",
        ]

    def get_date(self, instance):
        exam = Exam.objects.filter(date=instance.exam.date).first()
        return exam.date if exam else None

    def validate(self, attrs):
        exam =  getattr(self.instance, "exam", None)
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
            relatives_phones = Relatives.objects.filter(student=student).values_list("phone", flat=True)
            parents = CustomUser.objects.filter(phone__in=relatives_phones)

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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["exam"] = {
            "id": instance.exam.id,
            "name": instance.exam.name,
            "choice": instance.exam.choice,
            "type": instance.exam.type,
            "is_mandatory": instance.exam.is_mandatory,
        }
        rep["option"] = ExamSubjectSerializer(instance.option,context=self.context, many=True).data
        rep["student"] = StudentSerializer(instance.student, include_only=["id", "first_name", "last_name"]).data
        return rep


class ExamCertificateSerializer(serializers.ModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(), allow_null=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True,
    )

    class Meta:
        model = ExamCertificate
        fields = [
            "id",
            "student",
            "exam",
            "status",
            "certificate",
            "expire_date",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["certificate"] = FileUploadSerializer(instance.certificate, context=self.context).data
        rep["student"] = StudentSerializer(instance.student, include_only=["id", "first_name", "last_name"]).data
        return rep
