from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NoseyConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('test', self.channel_name)
        print(f'Added {self.channel_name} channel to ntf.')

    async def disconnect(self):
        await self.channel_layer.group_discard('gossip', self.channel_name)
        print(f'Removed {self.channel_name} channel from ntf.')

    async def user_gossip(self, event):
        await self.send_json(event)
        print(f'Got message {event} at {self.channel_name}')
