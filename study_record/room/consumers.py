import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from accounts.models import CustomUser
from .models import Room, Member, Message


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['pk']
        self.room_name = f'room_{self.room_id}'

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.create_member()

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        await self.delete_member()

        await self.close()

    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        data = {
            'type': 'chat_message',
            'user': {
                'id': user.id,
                'username': user.username,
                'icon': str(user.icon),
            },
            'message': message,
        }

        await self.create_message(message)

        await self.channel_layer.group_send(self.room_name, data)

    async def chat_message(self, event):
        user = event['user']
        message = event['message']

        # Send message to WebSocket
        await self.send(json.dumps({'user': user, 'message': message}))

    @database_sync_to_async
    def create_member(self):
        Member.objects.create(
            room    = Room.objects.get(pk=self.room_id),
            user    = self.scope['user'],
            is_host = False,
        )

    @database_sync_to_async
    def delete_member(self):
        Member.objects.filter(user=self.scope['user']).delete()

    @database_sync_to_async
    def create_message(self, message):
        print('message')
        Message.objects.create(
            room    = Room.objects.get(pk=self.room_id),
            user    = self.scope['user'],
            message = message,
        )