from django.apps import AppConfig


class DbCoreConfig(AppConfig):
    name = "db_core"
    verbose_name = "БД"

    def ready(self):
        import db_core.signals
