from django.db import models
from accounts.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Subject(models.Model):
    user         = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    name         = models.CharField(verbose_name='教科', max_length=50)
    color        = models.CharField(verbose_name='色', max_length=7, default='#ffa8a8')
    is_available = models.BooleanField(verbose_name='使用可能', default=True)
    created_at   = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at   = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Subject'

    def __str__(self):
        return self.name


class PublicationChoices(models.TextChoices):
    FOLLOW  = 'follow', 'フォロワーに公開'
    PRIVATE = 'private', '非公開'


class StudyRecord(models.Model):
    user        = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    subject     = models.ForeignKey(Subject, verbose_name="教科", on_delete=models.CASCADE)
    studied_at  = models.DateTimeField(verbose_name='日時')
    minutes     = models.IntegerField(verbose_name='学習時間', default=30, validators=[MinValueValidator(5), MaxValueValidator(1440)])
    publication = models.CharField(verbose_name='公開設定', max_length=10, choices=PublicationChoices.choices, default='follow')
    created_at  = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at  = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'StudyRecord'
