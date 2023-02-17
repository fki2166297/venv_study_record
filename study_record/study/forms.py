from django import forms
from django.db import models
from .models import StudyRecord, Subject


class StudyRecordForm(forms.ModelForm):
    subject = forms.ModelChoiceField(label='教科', queryset=Subject.objects.none())

    # ログインユーザーの教科のうち、使用可能なもの（is_available == True）を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user, is_available=True)
        super().__init__(*args, **kwargs)

    class Meta:
        model = StudyRecord
        fields = ('subject', 'studied_at', 'minutes', 'publication')


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'color')
