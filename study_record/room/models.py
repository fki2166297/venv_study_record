from django.db import models
from accounts.models import CustomUser


class RoomPublicationChoices(models.TextChoices):
    PUBLIC   = 'public', '全体公開'
    FOLLOWER = 'follower', 'フォロワーに公開'


class Room(models.Model):
    name        = models.CharField(max_length=150)
    publication = models.CharField(max_length=10, choices=RoomPublicationChoices.choices, default='PUBLIC')
    host        = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    started_at  = models.DateTimeField(auto_now_add=True)
    ended_at    = models.DateTimeField(auto_now=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Room'


class RoomMessage(models.Model):
    room    = models.ForeignKey(Room, on_delete=models.CASCADE)
    user    = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=400)


class RoomMember(models.Model):
    room      = models.ForeignKey(Room, on_delete=models.CASCADE)
    user      = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_host   = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)


# class RoomMemberRecord(models.Model):
#     user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     studied_at =