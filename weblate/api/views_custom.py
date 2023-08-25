import os
from typing import Iterable

from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.renderers import JSONRenderer

from rest_framework.serializers import BaseSerializer, Serializer, ValidationError
from rest_framework.serializers import CharField


from weblate.auth.models import User
from weblate.trans.models import Project, Unit

class PassAdminUserThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        if request.user.is_superuser:
            return True
        
        return super().allow_request(request, view)

class TenPerHourUserThrottle(PassAdminUserThrottle):
    rate = '10/hour'

@api_view(['GET'])
@throttle_classes([TenPerHourUserThrottle])
def export_view(request, project:str, lang: str):
    user: User = request.user
    if user.is_anonymous:
        raise NotAuthenticated({"message": "This api requires authenticaiton"})

    project_obj: Project = Project.objects.get(slug=project)
    if not request.user.has_perm("project.edit", project):
        raise PermissionDenied({
            "message":"You don't have permission to export the project",
            "project": project})

    units: Iterable[Unit] = Unit.objects.filter(
        translation__component__project=project_obj,
        translation__language__code=lang
    )
    
    result = [
        {
            "context": unit.context,
            "source": unit.source,
            "target": unit.target,
            "fuzzy": unit.fuzzy,
            "approved": unit.approved,
        }
        for unit in units
    ]
    return Response(result)


@receiver(post_save, sender=Unit)
def invalidate_bg3_dialog_cache(sender, instance, **kwargs):
    unit: Unit = instance
    if unit.translation.component.project.slug != "bg3":
        return
    if unit.translation.language.code != "ko":
        return
    if not unit.translation.component.slug.startswith("dialog"):
        return
    
    for location, filename, line in unit.get_locations():
        cleaned_filename = filename.removeprefix("Gustav/").removeprefix("Shared/")
        cache.delete(f"bg3_dialog:{cleaned_filename.replace('/', '_')}")


class DialogSerializer(Serializer):
    dialog = CharField(required=True)


@api_view(['POST'])
def bg3_dialog(request):
    user: User = request.user
    if user.is_anonymous:
        raise NotAuthenticated({"message": "This api requires authenticaiton"})
    
    bg3_proj: Project = Project.objects.get(slug="bg3")
    if not request.user.can_access_project(bg3_proj):
        raise PermissionDenied({
            "message":"You don't have permission to access the project",
            "project": "bg3"})
    
    dialog = request.data.get("dialog")
    if not dialog:
        raise ValidationError({"dialog": "This field is required"})
    
    dialog_path = os.path.splitext(dialog)[0] + ".lsj"

    cache_key = f"bg3_dialog:{dialog_path.replace('/', '_')}"
    dialog_cache = cache.get(cache_key)
    if dialog_cache:
        return Response(dialog_cache)

    units = Unit.objects.filter(
        translation__component__project=bg3_proj,
        translation__component__slug__startswith="dialog",
        translation__language__code="ko",
        location__contains=dialog_path
    ).prefetch_related('translation__component')

    result = [
        {
            "id": unit.id,
            "position": unit.position,
            "context": unit.context,
            "source": unit.source,
            "target": unit.target,
            "fuzzy": unit.fuzzy,
            "approved": unit.approved,
            "component": unit.translation.component.slug,
        }
        for unit in units
    ]

    cache.set(cache_key, result, 60*60*24)
    return Response(result)
