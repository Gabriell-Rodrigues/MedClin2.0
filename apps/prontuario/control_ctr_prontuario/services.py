# Representa o Control CTRProntuario, concentrando as regras de negócio do
# Módulo de Prontuário Eletrônico.
#
# Responsabilidades segundo a Tabela 18 do Documento de Arquitetura:
# - verificar acesso por perfil (Medico_Prontuario, Enfermeiro_Prontuario,
#   Farmaceutico_Prontuario);
# - inicializar prontuário;
# - atualizar evolução (diagnostico, observacoes, prescricaoAtiva);
# - obter histórico clínico.

import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.prontuario.entity_prontuario.models import (
    Prontuario,
    MedicoProntuario,
    EnfermeiroProntuario,
    FarmaceuticoProntuario,
)

_auditoria = logging.getLogger('medclin.auditoria')


class CTRProntuario:
    """
    Classe responsável pelas regras de negócio relacionadas ao Prontuário.
    """

    PERFIL_MEDICO = 'medico'
    PERFIL_ENFERMEIRO = 'enfermeiro'
    PERFIL_FARMACEUTICO = 'farmaceutico'

    PERFIS = (
        (PERFIL_MEDICO, 'Médico'),
        (PERFIL_ENFERMEIRO, 'Enfermeiro'),
        (PERFIL_FARMACEUTICO, 'Farmacêutico'),
    )

    # Mapeia cada perfil para a sua tabela associativa e o respectivo campo de id.
    _MODELOS_ACESSO = {
        PERFIL_MEDICO: (MedicoProntuario, 'idMedico'),
        PERFIL_ENFERMEIRO: (EnfermeiroProntuario, 'idEnfermeiro'),
        PERFIL_FARMACEUTICO: (FarmaceuticoProntuario, 'idFarmaceutico'),
    }

    # ------------------------------------------------------------------
    # Inicialização do prontuário
    # ------------------------------------------------------------------
    @staticmethod
    def inicializar_prontuario(paciente=None):
        """
        Inicializa um novo prontuário (UC-06).

        O prontuário é criado vazio. Os campos clínicos são preenchidos
        posteriormente pelo médico ao registrar a evolução (UC-12).

        Se um paciente for informado, o vínculo é registrado no próprio
        paciente, por meio do atributo idProntuario, conforme o mapeamento
        objeto-relacional (Paciente referencia Prontuario).
        """

        prontuario = Prontuario()
        prontuario.full_clean()
        prontuario.save()

        if paciente is not None:
            paciente.idProntuario = prontuario.idProntuario
            paciente.save(update_fields=['idProntuario'])

        CTRProntuario.registrar_alteracao(
            prontuario,
            'Prontuário inicializado com sucesso.'
        )

        return prontuario

    @staticmethod
    def listar_prontuarios():
        """
        Lista todos os prontuários cadastrados.
        """

        return Prontuario.objects.all()

    @staticmethod
    def buscar_por_id(idProntuario):
        """
        Busca um prontuário pelo seu identificador.
        """

        return Prontuario.objects.filter(idProntuario=idProntuario).first()

    @staticmethod
    def obter_paciente_vinculado(prontuario):
        """
        Retorna o paciente vinculado a este prontuário, se houver.

        O vínculo é mantido do lado do Paciente (idProntuario), conforme o
        mapeamento objeto-relacional. A leitura do módulo de cadastros é feita
        de forma defensiva para não acoplar o prontuário ao paciente.
        """

        try:
            from apps.cadastros.entity_paciente.models import Paciente
        except ImportError:
            return None

        return Paciente.objects.filter(
            idProntuario=prontuario.idProntuario
        ).first()

    # ------------------------------------------------------------------
    # Controle de acesso por perfil
    # ------------------------------------------------------------------
    @staticmethod
    def _resolver_perfil(perfil):
        """
        Valida o perfil informado e retorna o model associativo e o campo de id.
        """

        dados = CTRProntuario._MODELOS_ACESSO.get(perfil)

        if dados is None:
            raise ValidationError('Perfil profissional inválido.')

        return dados

    @staticmethod
    def conceder_acesso(prontuario, perfil, id_profissional):
        """
        Concede a um profissional acesso ao prontuário, registrando-o na tabela
        associativa correspondente ao seu perfil (UC-11).

        A operação é idempotente: se o acesso já existir, ele é mantido.
        """

        modelo, campo_id = CTRProntuario._resolver_perfil(perfil)

        if not id_profissional:
            raise ValidationError('O identificador do profissional é obrigatório.')

        _, criado = modelo.objects.get_or_create(**{
            campo_id: id_profissional,
            'prontuario': prontuario,
        })

        if criado:
            CTRProntuario.registrar_alteracao(
                prontuario,
                f'Acesso concedido ao {perfil} {id_profissional}.'
            )

        return criado

    @staticmethod
    def verificar_acesso(prontuario, perfil, id_profissional):
        """
        Verifica se um profissional tem acesso autorizado ao prontuário (UC-11).

        Retorna True se existir registro na tabela associativa do perfil.
        """

        modelo, campo_id = CTRProntuario._resolver_perfil(perfil)

        return modelo.objects.filter(**{
            campo_id: id_profissional,
            'prontuario': prontuario,
        }).exists()

    @staticmethod
    def listar_profissionais_autorizados(prontuario):
        """
        Retorna os profissionais autorizados a acessar o prontuário, agrupados
        por perfil.
        """

        return {
            CTRProntuario.PERFIL_MEDICO: list(
                prontuario.medicos_autorizados.values_list('idMedico', flat=True)
            ),
            CTRProntuario.PERFIL_ENFERMEIRO: list(
                prontuario.enfermeiros_autorizados.values_list('idEnfermeiro', flat=True)
            ),
            CTRProntuario.PERFIL_FARMACEUTICO: list(
                prontuario.farmaceuticos_autorizados.values_list('idFarmaceutico', flat=True)
            ),
        }

    # ------------------------------------------------------------------
    # Registro de evolução clínica (UC-12)
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def registrar_evolucao(prontuario, id_medico, diagnostico, observacoes,
                           prescricao_ativa):
        """
        Registra a evolução clínica do prontuário (UC-12 - Registrar Prontuário
        Eletrônico).

        Apenas médicos autorizados podem registrar evolução. Os campos atuais
        (diagnostico, observacoes, prescricaoAtiva) são atualizados e uma cópia
        datada da evolução é acrescentada ao historicoEvolucoes.
        """

        if not CTRProntuario.verificar_acesso(
            prontuario,
            CTRProntuario.PERFIL_MEDICO,
            id_medico
        ):
            raise ValidationError(
                'Apenas um médico autorizado pode registrar a evolução deste prontuário.'
            )

        diagnostico = (diagnostico or '').strip()
        observacoes = (observacoes or '').strip()
        prescricao_ativa = (prescricao_ativa or '').strip()

        if not diagnostico and not observacoes and not prescricao_ativa:
            raise ValidationError('Informe ao menos um campo da evolução clínica.')

        prontuario.diagnostico = diagnostico
        prontuario.observacoes = observacoes
        prontuario.prescricaoAtiva = prescricao_ativa
        prontuario.historicoEvolucoes = CTRProntuario._acrescentar_historico(
            prontuario.historicoEvolucoes,
            id_medico,
            diagnostico,
            observacoes,
            prescricao_ativa,
        )

        prontuario.full_clean()
        prontuario.save()

        CTRProntuario.registrar_alteracao(
            prontuario,
            f'Evolução registrada pelo médico {id_medico}.'
        )

        return prontuario

    @staticmethod
    def _acrescentar_historico(historico_atual, id_medico, diagnostico,
                               observacoes, prescricao_ativa):
        """
        Monta um novo bloco de evolução datado e o acrescenta ao histórico,
        mantendo o registro mais recente no topo.
        """

        data = timezone.now().strftime('%d/%m/%Y %H:%M')

        bloco = (
            f'[{data}] Médico {id_medico}\n'
            f'Diagnóstico: {diagnostico or "-"}\n'
            f'Observações: {observacoes or "-"}\n'
            f'Prescrição: {prescricao_ativa or "-"}'
        )

        separador = '\n' + ('-' * 60) + '\n'

        if historico_atual:
            return bloco + separador + historico_atual

        return bloco

    @staticmethod
    def obter_historico(prontuario):
        """
        Obtém o histórico de evoluções clínicas do prontuário.
        """

        return prontuario.historicoEvolucoes

    # ------------------------------------------------------------------
    # Auditoria simples
    # ------------------------------------------------------------------
    @staticmethod
    def registrar_alteracao(prontuario, mensagem):
        """
        Registra uma alteração relacionada ao prontuário.

        Como ainda não existe tabela de auditoria no escopo do módulo,
        o registro fica apenas preparado de forma simples.
        """

        _auditoria.info(f'prontuario | Prontuario#{prontuario.idProntuario} | {mensagem}')
