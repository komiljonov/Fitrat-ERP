from django.db import models

from data.command.models import BaseModel
from data.student.student.models import Student


class Quiz(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Answer(BaseModel):
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Question(BaseModel):
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



class Vocabulary(BaseModel):
    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='vocabularies_quiz')
    photo = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_photo')
    voice = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_voice')
    in_english = models.CharField(max_length=255, null=True,blank=True)
    in_uzbek = models.CharField(max_length=255, null=True,blank=True)
    def __str__(self):
        return f"{self.quiz.name}    {self.in_english}    {self.in_uzbek}"


class Fill_gaps(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='fill_gaps_quiz')
    question : "Question" = models.ForeignKey("quiz.Question", on_delete=models.SET_NULL, null=True, blank=True,related_name='fill_gaps_question')

    def __str__(self):
        return f"{self.quiz.title}    {self.question.question_text}"


class Listening(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='listening_quiz')
    question : "Question" = models.ForeignKey("quiz.Question", on_delete=models.SET_NULL, null=True, blank=True,related_name='listening_question')

    def __str__(self):
        return f"{self.quiz.title}    {self.question.question_text}"


class Pairs(BaseModel):
    first_pair = models.CharField(max_length=255)
    second_pair = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_pair}    {self.second_pair}"


class MatchPairs(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='match_pairs_quiz')
    pairs : "Pairs" = models.ManyToManyField(Pairs)
    def __str__(self):
        return f"{self.quiz.title} "