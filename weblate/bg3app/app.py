from django.apps import AppConfig


class BG3Config(AppConfig):
    name = "weblate.bg3app"
    label = "weblate_bg3app"
    verbose_name = "Baldur's Gate 3 Weblate app"

    def ready(self) -> None:
        pass
