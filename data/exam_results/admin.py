from django.contrib import admin
from .models import QuizResult
from .results_create_form import QuizResultForm


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    form = QuizResultForm
