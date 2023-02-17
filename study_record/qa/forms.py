from django import forms
from .models import Question, Answer


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'text', 'image')


class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text', 'image')
