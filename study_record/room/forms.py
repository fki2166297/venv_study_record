from django import forms
from .models import Room
from study.models import Subject

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('name', 'publication')


class SubjectForm(forms.Form):
    subject = forms.ModelChoiceField(label='教科', queryset=Subject.objects.none())

    # ログインユーザーの教科のうち、使用可能なもの（is_available == True）を選択肢にする
    def __init__(self, user=None, *args, **kwargs):
        self.base_fields['subject'].queryset = Subject.objects.filter(user=user, is_available=True)
        super().__init__(*args, **kwargs)
