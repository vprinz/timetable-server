from django.apps import AppConfig


class UniversityConfig(AppConfig):
    name = 'university'

    def ready(self):
        import university.signals
