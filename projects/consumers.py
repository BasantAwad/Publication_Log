from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserProfile

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
            await self.accept()
            await self.set_online(True)
    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.set_online(False)
            await self.channel_layer.group_discard(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
    async def receive(self, text_data):
        pass
    async def set_online(self, status):
        user = self.scope['user']
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_online = status
        profile.save()