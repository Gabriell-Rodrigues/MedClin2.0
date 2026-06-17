# Representa os Controls (CTR) do Módulo de Gestão de Acesso, concentrando as
# regras de cadastro, edição, busca, autenticação e redefinição de senha dos
# funcionários/profissionais da clínica.
#
# Casos de uso atendidos:
#   UC-01 - Fazer Login no Sistema
#   UC-02 - Redefinir Senha
#   UC-08 - Cadastrar Funcionários (dispatch do Gestor)

import hashlib
import logging

from django.core import signing
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.cadastros.validators import validar_cpf, remover_mascara_cpf
from apps.acesso.entity_funcionario.models import (
    Recepcionista,
    Medico,
    Enfermeiro,
    Farmaceutico,
    Gestor,
)

_auditoria = logging.getLogger('medclin.auditoria')


class CTRFuncionario:
    """
    Control base com as regras de negócio comuns a todos os perfis de
    funcionário. Cada perfil concreto define apenas o model, o rótulo e os
    campos específicos (crm, coren, crf, etc.).
    """

    model = None
    label = 'Funcionário'
    # Campos específicos do perfil, além dos comuns (nome, cpf, email, telefone).
    campos_extra = ()

    @classmethod
    def cadastrar(cls, dados):
        """Cadastra um novo funcionário do perfil (UC-08)."""

        cpf_limpo = validar_cpf(dados.get('cpf'))
        email = (dados.get('email') or '').strip().lower()

        if cls.model.objects.filter(cpf=cpf_limpo).exists():
            raise ValidationError(f'Já existe um {cls.label.lower()} com este CPF.')

        if cls.model.objects.filter(email__iexact=email).exists():
            raise ValidationError(f'Já existe um {cls.label.lower()} com este e-mail.')

        obj = cls.model(
            nome=dados.get('nome'),
            cpf=cpf_limpo,
            email=email,
            telefone=dados.get('telefone'),
        )

        for campo in cls.campos_extra:
            setattr(obj, campo, dados.get(campo))

        senha = dados.get('senha')

        if not senha:
            raise ValidationError('A senha é obrigatória.')

        obj.set_senha(senha)
        obj.full_clean()
        obj.save()

        cls.registrar_alteracao(obj, f'{cls.label} cadastrado com sucesso.')

        return obj

    @classmethod
    def editar(cls, obj, dados):
        """Edita os dados de um funcionário já cadastrado."""

        cpf_limpo = validar_cpf(dados.get('cpf'))
        email = (dados.get('email') or '').strip().lower()

        if cls.model.objects.filter(cpf=cpf_limpo).exclude(pk=obj.pk).exists():
            raise ValidationError(f'Já existe outro {cls.label.lower()} com este CPF.')

        if cls.model.objects.filter(email__iexact=email).exclude(pk=obj.pk).exists():
            raise ValidationError(f'Já existe outro {cls.label.lower()} com este e-mail.')

        obj.nome = dados.get('nome')
        obj.cpf = cpf_limpo
        obj.email = email
        obj.telefone = dados.get('telefone')

        for campo in cls.campos_extra:
            setattr(obj, campo, dados.get(campo))

        senha = dados.get('senha')

        if senha:
            obj.set_senha(senha)

        obj.full_clean()
        obj.save()

        cls.registrar_alteracao(obj, f'Dados do {cls.label.lower()} alterados.')

        return obj

    @classmethod
    def buscar_por_id(cls, pk):
        """Busca um funcionário pela chave primária."""
        return cls.model.objects.filter(pk=pk).first()

    @classmethod
    def buscar(cls, termo):
        """Busca funcionários por nome ou CPF."""

        termo = (termo or '').strip()

        if not termo:
            return cls.model.objects.none()

        return cls.model.objects.filter(
            Q(nome__icontains=termo) | Q(cpf__icontains=termo)
        ).order_by('nome')

    @classmethod
    def listar(cls):
        """Lista todos os funcionários do perfil."""
        return cls.model.objects.all().order_by('nome')

    @classmethod
    def autenticar(cls, email_ou_cpf, senha):
        """
        Autentica um funcionário do perfil pelo e-mail ou CPF (UC-01).

        Retorna o objeto autenticado ou None.
        """

        entrada = (email_ou_cpf or '').strip()

        # O CPF é gravado apenas com dígitos; o usuário pode digitar com ou sem
        # máscara (123.456.789-09). Normaliza para casar nos dois formatos.
        filtros = Q(email__iexact=entrada)
        cpf_limpo = remover_mascara_cpf(entrada)
        if len(cpf_limpo) == 11:
            filtros |= Q(cpf=cpf_limpo)

        obj = cls.model.objects.filter(filtros).first()

        if obj and obj.conferir_senha(senha):
            return obj

        return None

    @classmethod
    def alterar_senha(cls, obj, nova_senha):
        """Redefine a senha do funcionário (UC-02)."""

        if not nova_senha:
            raise ValidationError('A nova senha é obrigatória.')

        obj.set_senha(nova_senha)
        obj.save(update_fields=['senha'])

        cls.registrar_alteracao(obj, f'Senha do {cls.label.lower()} alterada.')

        return obj

    @staticmethod
    def registrar_alteracao(obj, mensagem):
        """Registro simples de auditoria (sem tabela dedicada no escopo)."""
        _auditoria.info(f'acesso | {type(obj).__name__}#{obj.pk} | {mensagem}')


class CTRRecepcionista(CTRFuncionario):
    model = Recepcionista
    label = 'Recepcionista'


class CTRMedico(CTRFuncionario):
    model = Medico
    label = 'Médico'
    campos_extra = ('crm', 'especializacao', 'idAgenda')


class CTREnfermeiro(CTRFuncionario):
    model = Enfermeiro
    label = 'Enfermeiro'
    campos_extra = ('coren',)


class CTRFarmaceutico(CTRFuncionario):
    model = Farmaceutico
    label = 'Farmacêutico'
    campos_extra = ('crf',)


class CTRGestor(CTRFuncionario):
    model = Gestor
    label = 'Gestor'


# Registro de perfis -> controle, usado pelas telas e pelo cadastro de
# funcionários feito pelo Gestor (UC-08).
PERFIS = {
    'recepcionista': CTRRecepcionista,
    'medico': CTRMedico,
    'enfermeiro': CTREnfermeiro,
    'farmaceutico': CTRFarmaceutico,
    'gestor': CTRGestor,
}


def obter_ctr(perfil):
    """Retorna o controle correspondente ao perfil informado."""

    ctr = PERFIS.get(perfil)

    if ctr is None:
        raise ValidationError('Perfil de funcionário inválido.')

    return ctr


class CTRAutenticacao:
    """
    Control de autenticação geral do sistema (UC-01 / UC-02).

    Centraliza o login e a redefinição de senha considerando todos os perfis
    com acesso ao sistema: os funcionários (Recepcionista, Médico, Enfermeiro,
    Farmacêutico, Gestor) e o Paciente.
    """

    @staticmethod
    def _ctr_paciente():
        """Importa o controle de Paciente de forma defensiva (loose coupling)."""
        from apps.cadastros.control_ctr_paciente.services import CTRPaciente
        return CTRPaciente

    @staticmethod
    def autenticar(email_ou_cpf, senha):
        """
        Tenta autenticar o usuário em todos os perfis do sistema (UC-01).

        Retorna uma tupla (perfil, objeto) em caso de sucesso, ou None.
        """

        for perfil, ctr in PERFIS.items():
            obj = ctr.autenticar(email_ou_cpf, senha)
            if obj:
                return perfil, obj

        paciente = CTRAutenticacao._ctr_paciente().autenticar_paciente(
            email_ou_cpf, senha
        )

        if paciente:
            return 'paciente', paciente

        return None

    # ------------------------------------------------------------------
    # Redefinição de senha por link/token (UC-02)
    #
    # Fluxo: o usuário pede o link por e-mail -> recebe um token assinado válido
    # por 30 minutos -> abre o link e define a nova senha -> o link deixa de
    # valer. Não há tabela de token: o estado vai no próprio token assinado
    # (django.core.signing), preservando a aderência ao Mapeamento
    # Objeto-Relacional. O uso único é garantido amarrando o token ao hash da
    # senha atual — ao trocar a senha, o token antigo deixa de conferir.
    # ------------------------------------------------------------------
    SALT_REDEFINICAO = 'medclin.redefinicao-senha'
    VALIDADE_TOKEN_SEG = 30 * 60  # 30 minutos

    @staticmethod
    def _buscar_por_email(email):
        """Localiza (perfil, objeto) por e-mail, em qualquer perfil do sistema."""
        email = (email or '').strip().lower()
        if not email:
            return None
        for perfil, ctr in PERFIS.items():
            obj = ctr.model.objects.filter(email__iexact=email).first()
            if obj:
                return perfil, obj
        from apps.cadastros.entity_paciente.models import Paciente as PacienteModel
        paciente = PacienteModel.objects.filter(email__iexact=email).first()
        if paciente:
            return 'paciente', paciente
        return None

    @staticmethod
    def _assinatura_senha(obj):
        """Resumo da senha atual; muda ao redefinir a senha (uso único)."""
        return hashlib.sha256((obj.senha or '').encode('utf-8')).hexdigest()[:16]

    @staticmethod
    def gerar_token_redefinicao(email):
        """
        Gera um token assinado de redefinição (UC-02), válido por 30 minutos.

        Retorna (token, objeto) se o e-mail existir; caso contrário, None.
        """
        achado = CTRAutenticacao._buscar_por_email(email)
        if not achado:
            return None
        perfil, obj = achado
        token = signing.dumps(
            {'perfil': perfil, 'id': obj.pk, 'h': CTRAutenticacao._assinatura_senha(obj)},
            salt=CTRAutenticacao.SALT_REDEFINICAO,
        )
        return token, obj

    @staticmethod
    def validar_token_redefinicao(token):
        """
        Valida o token e retorna (perfil, objeto). Levanta ValidationError se o
        token for inválido, expirado ou já utilizado.
        """
        try:
            dados = signing.loads(
                token,
                salt=CTRAutenticacao.SALT_REDEFINICAO,
                max_age=CTRAutenticacao.VALIDADE_TOKEN_SEG,
            )
        except signing.SignatureExpired:
            raise ValidationError('O link de redefinição expirou. Solicite um novo.')
        except signing.BadSignature:
            raise ValidationError('Link de redefinição inválido.')

        perfil = dados.get('perfil')
        pk = dados.get('id')

        if perfil == 'paciente':
            from apps.cadastros.entity_paciente.models import Paciente as PacienteModel
            obj = PacienteModel.objects.filter(pk=pk).first()
        else:
            ctr = PERFIS.get(perfil)
            obj = ctr.model.objects.filter(pk=pk).first() if ctr else None

        if obj is None:
            raise ValidationError('Conta não encontrada para este link.')

        # Uso único: se a senha já foi alterada, a assinatura não confere mais.
        if dados.get('h') != CTRAutenticacao._assinatura_senha(obj):
            raise ValidationError('Este link já foi utilizado. Solicite um novo.')

        return perfil, obj

    @staticmethod
    def redefinir_senha_com_token(token, nova_senha):
        """Redefine a senha a partir de um token válido (UC-02)."""
        if not nova_senha:
            raise ValidationError('A nova senha é obrigatória.')

        perfil, obj = CTRAutenticacao.validar_token_redefinicao(token)

        if perfil == 'paciente':
            CTRAutenticacao._ctr_paciente().alterar_senha(obj, nova_senha)
        else:
            PERFIS[perfil].alterar_senha(obj, nova_senha)

        return perfil, obj
