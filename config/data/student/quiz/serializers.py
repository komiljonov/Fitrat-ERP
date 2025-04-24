from icecream import ic
from rest_framework import serializers

from .models import Quiz, Question, Answer, Fill_gaps, Vocabulary,  MatchPairs, Exam, Gaps, \
    QuizGaps, Pairs
from ..student.models import Student
from ..subject.models import Subject
from ..subject.serializers import SubjectSerializer
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

    students_excel = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    results_excel = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),allow_null=True)
    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",

            "type",
            "students_excel",
            "results_excel",
            "students_count",
            "subject",

            "date",
            "start_time",
            "end_time",

            "description",
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
        return VocabularySerializer(Vocabulary.objects.filter(quiz=obj), many=True).data
    def get_match_pairs(self, obj):
        return MatchPairsSerializer(MatchPairs.objects.filter(quiz=obj), many=True).data


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject).data
        rep["students_excel"] = FileUploadSerializer(instance.students_excel, context=self.context).data
        rep["results_excel"] = FileUploadSerializer(instance.results_excel, context=self.context).data
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
        rep["photo"] = FileUploadSerializer(instance.photo).data
        rep["voice"] = FileUploadSerializer(instance.voice).data
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
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),many=True,allow_null=True)
    class Meta:
        model = Exam
        fields = [
            "id",
            "quiz",
            "type",
            "student",
            "subject",
            "students_xml",
            "exam_materials",
            "results",
            "end_date",
            "created_at",
        ]

