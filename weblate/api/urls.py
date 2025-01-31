#
# Copyright © 2012 - 2020 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#


from django.conf.urls import include, url

from weblate.api.routers import WeblateRouter
from weblate.api.views import (
    ChangeViewSet,
    ComponentListViewSet,
    ComponentViewSet,
    GroupViewSet,
    LanguageViewSet,
    Metrics,
    ProjectViewSet,
    RoleViewSet,
    ScreenshotViewSet,
    TranslationViewSet,
    UnitViewSet,
    UserViewSet,
)

from weblate.api.views_custom import bg3_dialog, bg3_quest, export_view

# Routers provide an easy way of automatically determining the URL conf.
router = WeblateRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"components", ComponentViewSet, "component")
router.register(r"translations", TranslationViewSet)
router.register(r"languages", LanguageViewSet)
router.register("component-lists", ComponentListViewSet)
router.register(r"changes", ChangeViewSet)
router.register(r"units", UnitViewSet)
router.register(r"screenshots", ScreenshotViewSet)


# URL regexp for language code
LANGUAGE = r"(?P<lang>[^/]+)"

# URL regexp for project
PROJECT = r"(?P<project>[^/]+)/"

# URL regexp for component
COMPONENT = PROJECT + r"(?P<component>[^/]+)/"

# URL regexp for translations
TRANSLATION = COMPONENT + LANGUAGE + "/"

# URL regexp for project language pages
PROJECT_LANG = PROJECT + LANGUAGE + "/"


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r"^metrics/$", Metrics.as_view(), name="metrics"),
    url(r"^", include(router.urls)),
    url(
        r"^export/" + PROJECT_LANG + "$",
        export_view,
        name="export"
    ),
    url(
        r"^bg3_dialog$",
        bg3_dialog,
        name="bg3_dialog"
    ),
    url(
        r"^bg3_quest$",
        bg3_quest,
        name="bg3_quest"
    ),
]
