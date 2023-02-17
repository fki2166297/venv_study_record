from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    icon      = models.ImageField(verbose_name="アイコン", upload_to="account_icons/", null=True, blank=True)
    introduce = models.TextField(verbose_name="自己紹介", max_length=200, null=True, blank=True)

    class Meta:
        verbose_name_plural = "CustomUser"


class Connection(models.Model):
    follower   = models.ForeignKey(CustomUser, related_name="follower", on_delete=models.CASCADE)
    following  = models.ForeignKey(CustomUser, related_name="following", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} : {self.following.username}"
