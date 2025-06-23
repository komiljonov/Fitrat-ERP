from django import forms
from .models import QuizResult

class QuizResultForm(forms.ModelForm):
    class Meta:
        model = QuizResult
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark all ManyToMany fields as not required
        for field_name in [
            "questions", "match_pair", "true_false",
            "vocabulary", "objective", "cloze_test",
            "image_objective", "Listening"
        ]:
            self.fields[field_name].required = False
