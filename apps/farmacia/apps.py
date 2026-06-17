# Define as configurações principais do app de farmácia dentro do projeto.

from django.apps import AppConfig


class FarmaciaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.farmacia'
    verbose_name = 'Módulo Farmacêutico'
