from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from users.consumers import NoseyConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('notifications/', NoseyConsumer)
    ])
})
