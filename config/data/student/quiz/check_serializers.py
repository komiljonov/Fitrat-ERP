from rest_framework import serializers
from uuid import UUID

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

class QuizCheckSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    multiple_choice = MultipleChoiceSerializer(many=True, required=False)
    fill_gaps = FillGapsSerializer(many=True, required=False)
    vocabularies = VocabularyAnswerSerializer(many=True, required=False)
    listening = ListeningAnswerSerializer(many=True, required=False)
    match_pairs = MatchPairsSerializer(many=True, required=False)

    class Meta:
        ref_name = "Check_QuizCheckSerializer"
