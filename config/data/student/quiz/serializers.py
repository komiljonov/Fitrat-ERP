from datetime import datetime

from icecream import ic
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import Quiz, Question, Answer, Fill_gaps, Vocabulary, MatchPairs, Exam, Gaps, \
    QuizGaps, Pairs, ExamRegistration
from ..homeworks.models import Homework
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..subject.models import Subject, Theme
from ..subject.serializers import SubjectSerializer, ThemeSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=Answer.objects.all())
    text = serializers.PrimaryKeyRelatedField(queryset=QuizGaps.objects.all())
    class Meta:
        model = Question
        fields = ["id","quiz" ,"text", "answers"]



    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["text"] = QuizGapsSerializer(instance.text).data
        rep["answers"] = AnswerSerializer(instance.answers.all(),many=True).data
        return rep


class QuizGapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizGaps
        fields = [
            "id",
            "name",
            "created_at"
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    fill_gap = serializers.SerializerMethodField()
    vocabularies = serializers.SerializerMethodField()
    match_pairs = serializers.SerializerMethodField()

    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(),allow_null=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "theme",
            "subject",
            "questions",
            "fill_gap",
            "vocabularies",
            "match_pairs",
            "created_at",
        ]
    def get_questions(self, obj):
        return QuestionSerializer(Question.objects.filter(quiz=obj), many=True).data

    def get_fill_gap(self, obj):
        return FillGapsSerializer(Fill_gaps.objects.filter(quiz=obj), many=True).data  # ✅ correct

    def get_vocabularies(self, obj):
        return VocabularySerializer(Vocabulary.objects.filter(quiz=obj),context=self.context ,many=True).data

    def get_match_pairs(self, obj):
        return MatchPairsSerializer(MatchPairs.objects.filter(quiz=obj), many=True).data


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject).data
        rep["theme"] = (
            ThemeSerializer(instance.theme,include_only=["id","title"]).data
        )
        return rep

class QuizImportSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    questions = QuestionSerializer(many=True)

    def create(self, validated_data):
        quiz, created = Quiz.objects.get_or_create(
            title=validated_data['title'],
            defaults={'description': validated_data.get('description', '')}
        )

        for question_data in validated_data['questions']:
            question = Question.objects.create(
                quiz=quiz, question_text=question_data['question_text']
            )

            # Create and add answers to the question
            answers = [
                Answer.objects.create(**answer_data)
                for answer_data in question_data['answers']
            ]
            question.answers.set(answers)

        return quiz

class UserAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()

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
        fields = ["id", "quiz", "question", "gaps"]

    def create(self, validated_data):
        gaps_instances = []
        question_obj = validated_data.get("question")
        quiz = validated_data.get("quiz")

        if question_obj:
            for word in question_obj.name.split(" "):  # ✅ use .name
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
        rep["gaps"] = GapsSerializer(instance.gaps.all(), many=True).data  # ← FIXED HERE
        return rep

class VocabularySerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    voice = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    class Meta:
        model = Vocabulary
        fields = [
            "id",
            "quiz",
            "photo",
            "voice",
            "in_english",
            "in_uzbek",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["photo"] = FileUploadSerializer(instance.photo,context=self.context).data
        rep["voice"] = FileUploadSerializer(instance.voice,context=self.context).data
        return rep

class PairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pairs
        fields = [
            "id",
            "pair",
            "choice",
            "created_at",
        ]

class MatchPairsSerializer(serializers.ModelSerializer):
    pairs = serializers.PrimaryKeyRelatedField(queryset=Pairs.objects.all(),many=True,allow_null=True)
    class Meta:
        model = MatchPairs
        fields = [
            "id",
            "quiz",
            "pairs",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["pairs"] = PairsSerializer(instance.pairs.all(),many=True).data
        return rep

class ExamSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(),allow_null=True)
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),many=True,allow_null=True)
    materials = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True,allow_null=True)
    homework = serializers.PrimaryKeyRelatedField(queryset=Homework.objects.all(),allow_null=True)
    students_xml = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    results = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)

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
            "students",
            "subject",
            "students_xml",
            "materials",
            "results",
            "students_count",
            "date",
            "start_time",
            "end_time",
            "homework",
            "created_at",
        ]


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["results"] = FileUploadSerializer(instance.results).data
        rep["students"] =(
            StudentSerializer(instance.students.all(),include_only=["id","first_name", "last_name","phone"], many=True).data
        ) if instance.students else None
        return rep


class ExamRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRegistration
        fields = [
            "id",
            "student",
            "exam",
            "mark",
            "created_at",
        ]

    def validate(self, attrs):
        exam = attrs.get("exam")
        student = attrs.get("student")

        if not exam:
            raise serializers.ValidationError({"exam": "Imtihon topilmadi."})

        now = datetime.now()
        exam_end_datetime = datetime.combine(exam.date, exam.end_time)

        if now > exam_end_datetime:
            raise serializers.ValidationError({"exam": "Imtihondan ro'yxatdan o'tish vaqti yakunlangan."})

        if ExamRegistration.objects.filter(exam=exam, student=student).exists():
            raise serializers.ValidationError({"student": "Talaba allaqachon imtihon uchun ro'yxatdan o'tgan."})

        return attrs