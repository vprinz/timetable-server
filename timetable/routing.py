from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from university.consumers import UniversityConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('notifications/', UniversityConsumer)
    ])
})
