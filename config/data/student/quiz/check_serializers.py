from rest_framework import serializers


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


# NEW: Objective Test Answer Serializer (field-based)
class ObjectiveTestAnswerSerializer(serializers.Serializer):
    objective_id = serializers.UUIDField()
    answer_ids = serializers.ListField(child=serializers.UUIDField())  # Multiple answers

    class Meta:
        ref_name = "Check_ObjectiveTestAnswerSerializer"


# NEW: Cloze Test Answer Serializer (field-based)
class ClozeTestAnswerSerializer(serializers.Serializer):
    cloze_id = serializers.UUIDField()
    word_sequence = serializers.ListField(child=serializers.CharField())  # Word order

    class Meta:
        ref_name = "Check_ClozeTestAnswerSerializer"


# NEW: Image Objective Test Answer Serializer (field-based)
class ImageObjectiveTestAnswerSerializer(serializers.Serializer):
    image_objective_id = serializers.UUIDField()
    answer = serializers.CharField()  # Text answer

    class Meta:
        ref_name = "Check_ImageObjectiveTestAnswerSerializer"


# NEW: True/False Answer Serializer (field-based)
class TrueFalseAnswerSerializer(serializers.Serializer):
    true_false_id = serializers.UUIDField()
    choice = serializers.BooleanField()  # True/False choice

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

    # Updated to use field-based serializers
    objective_test = ObjectiveTestAnswerSerializer(many=True, required=False)
    cloze_test = ClozeTestAnswerSerializer(many=True, required=False)
    image_objective_test = ImageObjectiveTestAnswerSerializer(many=True, required=False)
    true_false = TrueFalseAnswerSerializer(many=True, required=False)

    class Meta:
        ref_name = "Check_QuizCheckSerializer"