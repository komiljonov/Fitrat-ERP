from rest_framework import serializers

from data.student.quiz.serializers import ObjectiveTestSerializer, Cloze_TestSerializer, True_FalseSerializer


class MultipleChoiceSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    answer_id = serializers.UUIDField()


class FillGapsSerializer(serializers.Serializer):
    fill_id = serializers.UUIDField()
    gaps = serializers.ListField(child=serializers.CharField())

    class Meta:
        ref_name = "Check_FillGapsSerializer"


class VocabularyAnswerSerializer(serializers.Serializer):
    vocab_id = serializers.UUIDField()
    english = serializers.CharField(allow_null=True, required=False)
    uzbek = serializers.CharField(allow_null=True, required=False)


class ListeningAnswerSerializer(serializers.Serializer):
    listening_id = serializers.UUIDField()
    answer_id = serializers.UUIDField()


class MatchPairItemSerializer(serializers.Serializer):
    left = serializers.CharField()
    right = serializers.CharField()

    class Meta:
        ref_name = "Check_MatchPairItemSerializer"


class MatchPairsSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    pairs = MatchPairItemSerializer(many=True)

    class Meta:
        ref_name = "Check_MatchPairsSerializer"


class ObjectiveAnswerSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    answer_id = serializers.UUIDField()

    class Meta:
        ref_name = "Check_ObjectiveAnswerSerializer"


class Cloze_TestAnswerSerializer(serializers.Serializer):
    question_ids = serializers.ListField(child=serializers.CharField())
    answer_ids = serializers.UUIDField()

    class Meta:
        ref_name = "Check_Cloze_TestSerializer"


class ImageObjectiveTestAnswerSerializer(serializers.Serializer):
    answer_id = serializers.UUIDField()

    class Meta:
        ref_name = "Check_ObjectiveTestAnswerSerializer"


class True_FalseAnswerSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    answer = serializers.ChoiceField(choices=["True", "False", "Not Given"])

    class Meta:
        ref_name = "Check_TrueFalseAnswerSerializer"


class QuizCheckSerializer(serializers.Serializer):
    theme = serializers.UUIDField(required=False)
    quiz_id = serializers.UUIDField()
    multiple_choice = MultipleChoiceSerializer(many=True, required=False)
    fill_gaps = FillGapsSerializer(many=True, required=False)
    vocabularies = VocabularyAnswerSerializer(many=True, required=False)
    listening = ListeningAnswerSerializer(many=True, required=False)
    match_pairs = MatchPairsSerializer(many=True, required=False)
    objective = ObjectiveTestSerializer(many=True, required=False)
    cloze = Cloze_TestSerializer(many=True, required=False)
    image_objective = ImageObjectiveTestAnswerSerializer(many=True, required=False)
    true_false = True_FalseSerializer(many=True, required=False)

    class Meta:
        ref_name = "Check_QuizCheckSerializer"
