"""
ASGI config for ids project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from ids.consumers import TrainConsumer, PredictConsumer, AnalysisConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ids.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("train/", TrainConsumer.as_asgi()),
            path("predict/", PredictConsumer.as_asgi()),
            path("analysis/", AnalysisConsumer.as_asgi()),
        ])
    ),
})