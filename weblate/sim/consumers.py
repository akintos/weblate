import json
from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from weblate.auth.models import User

from weblate.trans.models import Project, Unit


@database_sync_to_async
def project_perm_check(user, project_slug):
    project = Project.objects.filter(slug=project_slug).first()

    if not project:
        return 404

    return 200 if user.has_perm("unit.edit", project) else 401


class SimConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Unit.objects.all()

    async def connect(self):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            await self.close(code=401)
            return
        
        project_slug = self.scope["url_route"]["kwargs"]["project"]
        result = await project_perm_check(user,  project_slug)

        if result != 200:
            await self.close(code=result)
            return
        
        self.project_slug = project_slug

        await self.accept()

    async def receive(self, text_data: str):
        try:
            unit_data = await self._get_unit(text_data)
            await self.send(json.dumps(unit_data))
        except Exception as e:
            await self.send(json.dumps({"success": False, "error": str(e)}))

    @database_sync_to_async
    def _get_unit(self, query: str):
        unit_key = query

        unit = self.queryset.filter(
            translation__component__project__slug=self.project_slug,
            id=unit_key
        ).first()

        if not unit:
            return {"success": False, "error": "UNIT_NOT_FOUND"}

        data = {
            "component": unit.translation.component.slug,
            "key": unit.context,
            "src": unit.source,
            "dst": unit.target,
            "fuzzy": unit.fuzzy,
            "position": unit.position,
            "checksum": unit.checksum,
        }

        return {"success": True, "data": data}
