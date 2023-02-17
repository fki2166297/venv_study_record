from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Question(models.Model):
    user        = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.CASCADE)
    image       = models.ImageField(verbose_name='画像', upload_to='question_images/', null=True, blank=True, default='')
    title       = models.CharField(verbose_name='タイトル', max_length=200)
    text        = models.TextField(verbose_name='質問文')
    supplement  = models.TextField(verbose_name='補足説明文', null=True, blank=False)
    is_resolved = models.BooleanField(verbose_name='解決済み', default=False)
    created_at  = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at  = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'

    def __str__(self):
        return self.text


class Answer(models.Model):
    user            = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.CASCADE)
    question        = models.ForeignKey(Question, verbose_name='質問ID', on_delete=models.PROTECT)
    text            = models.TextField(verbose_name='回答文')
    image           = models.ImageField(verbose_name='画像', upload_to='answer_images/', null=True, blank=True, default='')
    is_best         = models.BooleanField(verbose_name='ベストアンサー', default=False)
    self_resolution = models.BooleanField(verbose_name='自己解決', default=False)
    created_at      = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at      = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Answer'


class AnswerComment(models.Model):
    user       = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.CASCADE)
    answer     = models.ForeignKey(Answer, verbose_name='質問ID', on_delete=models.PROTECT, related_name='comments')
    text       = models.TextField(verbose_name='コメント')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'AnswerComment'
