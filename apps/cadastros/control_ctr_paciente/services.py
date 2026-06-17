# Representa o Control CTRPaciente, concentrando as regras de cadastro, edição, validação e busca de pacientes.

import logging

from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.cadastros.entity_paciente.models import Paciente
from apps.cadastros.validators import validar_cpf, remover_mascara_cpf

_auditoria = logging.getLogger('medclin.auditoria')


class CTRPaciente:
    """
    Classe responsável pelas regras de negócio relacionadas ao Paciente.

    Responsabilidades segundo a BCE:
    - validar CPF;
    - persistir cadastro;
    - executar busca por CPF;
    - executar busca por nome;
    - registrar alterações.
    """

    @staticmethod
    def cadastrar_paciente(dados):
        """
        Cadastra um novo paciente no sistema.
        """

        cpf_limpo = validar_cpf(dados.get('cpf'))
        email = dados.get('email', '').strip().lower()

        if Paciente.objects.filter(cpf=cpf_limpo).exists():
            raise ValidationError('Já existe um paciente cadastrado com este CPF.')

        if Paciente.objects.filter(email__iexact=email).exists():
            raise ValidationError('Já existe um paciente cadastrado com este e-mail.')

        paciente = Paciente(
            nome=dados.get('nome'),
            cpf=cpf_limpo,
            telefone=dados.get('telefone'),
            dataNascimento=dados.get('dataNascimento'),
            email=email,
            idRecepcionista=dados.get('idRecepcionista'),
            idAgenda=dados.get('idAgenda'),
            idProntuario=dados.get('idProntuario'),
        )

        senha = dados.get('senha')

        if not senha:
            raise ValidationError('A senha é obrigatória.')

        paciente.set_senha(senha)
        paciente.full_clean()
        paciente.save()

        CTRPaciente.registrar_alteracao(
            paciente,
            'Paciente cadastrado com sucesso.'
        )

        return paciente

    @staticmethod
    def editar_paciente(paciente, dados):
        """
        Edita os dados de um paciente já cadastrado.
        """

        cpf_limpo = validar_cpf(dados.get('cpf'))
        email = dados.get('email', '').strip().lower()

        cpf_duplicado = Paciente.objects.filter(cpf=cpf_limpo).exclude(
            pk=paciente.pk
        ).exists()

        if cpf_duplicado:
            raise ValidationError('Já existe outro paciente cadastrado com este CPF.')

        email_duplicado = Paciente.objects.filter(email__iexact=email).exclude(
            pk=paciente.pk
        ).exists()

        if email_duplicado:
            raise ValidationError('Já existe outro paciente cadastrado com este e-mail.')

        paciente.nome = dados.get('nome')
        paciente.cpf = cpf_limpo
        paciente.telefone = dados.get('telefone')
        paciente.dataNascimento = dados.get('dataNascimento')
        paciente.email = email
        paciente.idRecepcionista = dados.get('idRecepcionista')
        paciente.idAgenda = dados.get('idAgenda')
        paciente.idProntuario = dados.get('idProntuario')

        senha = dados.get('senha')

        if senha:
            paciente.set_senha(senha)

        paciente.full_clean()
        paciente.save()

        CTRPaciente.registrar_alteracao(
            paciente,
            'Dados do paciente alterados.'
        )

        return paciente

    @staticmethod
    def buscar_por_cpf(cpf):
        """
        Busca um paciente pelo CPF.
        """

        cpf_limpo = validar_cpf(cpf)

        return Paciente.objects.filter(cpf=cpf_limpo).first()

    @staticmethod
    def buscar_por_nome(nome):
        """
        Busca pacientes pelo nome.
        """

        nome = nome.strip() if nome else ''

        if not nome:
            return Paciente.objects.none()

        return Paciente.objects.filter(
            nome__icontains=nome
        ).order_by('nome')

    @staticmethod
    def listar_pacientes():
        """
        Lista todos os pacientes cadastrados.
        """

        return Paciente.objects.all().order_by('nome')

    @staticmethod
    def autenticar_paciente(email_ou_cpf, senha):
        """
        Estrutura preparada para o UC-01 - Fazer Login.

        Não implementa o login completo do sistema.
        Apenas verifica se existe um paciente com o e-mail ou CPF informado.
        """

        entrada = email_ou_cpf.strip() if email_ou_cpf else ''

        # O CPF é gravado apenas com dígitos; aceita também CPF com máscara.
        filtros = Q(email__iexact=entrada)
        cpf_limpo = remover_mascara_cpf(entrada)
        if len(cpf_limpo) == 11:
            filtros |= Q(cpf=cpf_limpo)

        paciente = Paciente.objects.filter(filtros).first()

        if paciente and paciente.conferir_senha(senha):
            return paciente

        return None

    @staticmethod
    def alterar_senha(paciente, nova_senha):
        """
        Estrutura preparada para o UC-02 - Redefinir Senha.
        """

        if not nova_senha:
            raise ValidationError('A nova senha é obrigatória.')

        paciente.set_senha(nova_senha)
        paciente.save(update_fields=['senha'])

        CTRPaciente.registrar_alteracao(
            paciente,
            'Senha do paciente alterada.'
        )

        return paciente

    @staticmethod
    def registrar_alteracao(paciente, mensagem):
        """
        Registra uma alteração relacionada ao paciente.

        Como ainda não existe tabela de auditoria no escopo do módulo,
        o registro fica apenas preparado de forma simples.
        """

        _auditoria.info(f'cadastros | Paciente#{paciente.idPaciente} | {mensagem}')