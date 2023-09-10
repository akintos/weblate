import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weblate.settings")

django_asgi_app = get_asgi_application()

from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
from weblate.sim.middleware import TokenAuthMiddleWare

from weblate.sim.consumers import SimConsumer

application = ProtocolTypeRouter({
    # "http": django_asgi_app,
    "websocket": TokenAuthMiddleWare(
        URLRouter(
            [
                re_path(r"^ws/sim/(?P<project>[^/]+)$", SimConsumer.as_asgi()),
            ]
        )
    ),
})
