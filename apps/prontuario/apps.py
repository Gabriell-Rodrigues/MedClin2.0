# Define as configurações principais do app de prontuário dentro do projeto Django.

from django.apps import AppConfig


class ProntuarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prontuario'
    verbose_name = 'Módulo de Prontuário Eletrônico'
