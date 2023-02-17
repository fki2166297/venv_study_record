# Generated by Django 4.1.1 on 2023-02-17 01:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='ルーム名')),
                ('publication', models.CharField(choices=[('public', '全体公開'), ('follower', 'フォロワーに公開')], default='PUBLIC', max_length=10, verbose_name='公開設定')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='開始日時')),
                ('ended_at', models.DateTimeField(auto_now=True, verbose_name='終了日時')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='主催者')),
            ],
            options={
                'verbose_name_plural': 'Room',
            },
        ),
        migrations.CreateModel(
            name='RoomMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=400, verbose_name='メッセージ')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room', verbose_name='ルーム')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
        migrations.CreateModel(
            name='RoomMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True, verbose_name='日時')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room', verbose_name='ルーム')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
    ]
