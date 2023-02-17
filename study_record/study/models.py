from django.db import models
from accounts.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Subject(models.Model):
    user         = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name         = models.CharField(max_length=50)
    color        = models.CharField(max_length=7, default='#ffa8a8')
    is_available = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PublicationChoices(models.TextChoices):
    FOLLOW  = 'follow', 'フォロワーに公開'
    PRIVATE = 'private', '非公開'


class StudyRecord(models.Model):
    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE)
    studied_at  = models.DateTimeField()
    minutes     = models.IntegerField(default=30, validators=[MinValueValidator(5), MaxValueValidator(1440)])
    publication = models.CharField(max_length=10, choices=PublicationChoices.choices, default='follow')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

