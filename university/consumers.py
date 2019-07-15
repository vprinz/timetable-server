from channels.generic.websocket import AsyncJsonWebsocketConsumer


class UniversityConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('gossip', self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard('gossip', self.channel_name)

    async def university_gossip(self, event):
        del event['type']
        await self.send_json(event)
