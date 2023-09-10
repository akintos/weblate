from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser

from rest_framework.authtoken.models import Token

from channels.db import database_sync_to_async


@database_sync_to_async
def getUserFromToken(token_string):
    return Token.objects.get(key=token_string).user


class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app
 
    async def __call__(self, scope, receive, send):
        # Check this actually has headers. They're a required scope key for HTTP and WS.
        if "headers" not in scope:
            raise ValueError(
                "TokenAuthMiddleWare was passed a scope that did not have a headers key "
                + "(make sure it is only passed HTTP or WebSocket connections)"
            )
        
        name: bytes
        value: bytes
        # Go through headers to find the cookie one
        for name, value in scope.get("headers", []):
            if name.lower() == b"authentication" and value.startswith(b"Token "):
                token = value[6:].decode("latin1")
                scope["user"] = await getUserFromToken(token)
                break
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
