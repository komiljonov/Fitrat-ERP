from django.db import models

from data.command.models import TimeStampModel
from data.student.student.models import Student


class Quiz(TimeStampModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Answer(TimeStampModel):
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Question(TimeStampModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answers = models.ManyToManyField(Answer)

    def __str__(self):
        return self.question_text

    def get_correct_answer(self):
      return self.answers.filter(is_correct=True).first()

    def check_answer(self, answer_id):
        try:
            answer = Answer.objects.get(pk=answer_id)
            return answer.is_correct and answer in self.answers.all()
        except Answer.DoesNotExist:
            return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if self.answers.count() == 0: # Ensure at least 4 answers when question is saved
            for i in range(4): # Add dummy answers if no answers exist
                Answer.objects.create(text=f"Answer {i+1}", is_correct=False)
