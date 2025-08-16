from django.apps import AppConfig


class CarregahoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carregahores'

    def ready(self):
        from . import signals  # noqa
