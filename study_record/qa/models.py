from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Question(models.Model):
    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image       = models.ImageField(upload_to='question_images/', null=True, blank=True, default='')
    title       = models.CharField(max_length=200)
    text        = models.TextField()
    supplement  = models.TextField(null=True, blank=False)
    is_resolved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    user            = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question        = models.ForeignKey(Question, on_delete=models.PROTECT)
    text            = models.TextField()
    image           = models.ImageField(upload_to='answer_images/', null=True, blank=True, default='')
    is_best         = models.BooleanField(default=False)
    self_resolution = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer     = models.ForeignKey(Answer, on_delete=models.PROTECT, related_name='comments')
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

