# Comando de bootstrap: cria o primeiro Gestor do sistema.
#
# Necessário porque o cadastro de funcionários (UC-08) é restrito ao Gestor.
# Usa o controle CTRGestor (mesma regra da aplicação), garantindo a senha com
# hash — ao contrário do admin do Django, que salvaria a senha em texto puro.
#
# Uso:
#   python manage.py criar_gestor --nome "Admin" --cpf 529.982.247-25 \
#       --email admin@medclin.com --senha senha123 --telefone 79999990000

from django.core.management.base import BaseCommand, CommandError

from apps.acesso.control_ctr_funcionario.services import CTRGestor


class Command(BaseCommand):
    help = 'Cria o primeiro Gestor (bootstrap do controle de acesso).'

    def add_arguments(self, parser):
        parser.add_argument('--nome', required=True)
        parser.add_argument('--cpf', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--senha', required=True)
        parser.add_argument('--telefone', default='0000000000')

    def handle(self, *args, **opts):
        try:
            gestor = CTRGestor.cadastrar({
                'nome': opts['nome'],
                'cpf': opts['cpf'],
                'email': opts['email'],
                'senha': opts['senha'],
                'telefone': opts['telefone'],
            })
        except Exception as erro:
            raise CommandError(f'Não foi possível criar o gestor: {erro}')

        self.stdout.write(self.style.SUCCESS(
            f'Gestor criado (id={gestor.idGestor}, email={gestor.email}). '
            f'Faça login em /acesso/login/.'
        ))
