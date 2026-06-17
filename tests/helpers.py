# Utilitários compartilhados pelos testes (geração de CPF válido e criação de
# usuários de cada perfil). Não contém testes.

import random

from apps.acesso.entity_funcionario.models import (
    Recepcionista, Medico, Enfermeiro, Farmaceutico, Gestor,
)
from apps.cadastros.entity_paciente.models import Paciente

SENHA = 'Clinica@2026'


def gerar_cpf():
    """Gera um CPF válido (com dígitos verificadores corretos)."""
    n = [random.randint(0, 9) for _ in range(9)]
    while len(set(n)) == 1:
        n = [random.randint(0, 9) for _ in range(9)]
    for _ in range(2):
        s = sum((len(n) + 1 - i) * v for i, v in enumerate(n))
        d = 11 - (s % 11)
        n.append(0 if d >= 10 else d)
    return ''.join(map(str, n))


def mascarar_cpf(cpf):
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


def _salvar(obj):
    obj.set_senha(SENHA)
    obj.full_clean()
    obj.save()
    return obj


def criar_gestor(email='gestor@test.com'):
    return _salvar(Gestor(nome='Gestor Teste', cpf=gerar_cpf(),
                          email=email, telefone='82999990001'))


def criar_recepcionista(email='recep@test.com'):
    return _salvar(Recepcionista(nome='Recepcao Teste', cpf=gerar_cpf(),
                                 email=email, telefone='82999990002'))


def criar_medico(email='medico@test.com'):
    return _salvar(Medico(nome='Medico Teste', cpf=gerar_cpf(), email=email,
                          telefone='82999990003', crm='CRM' + gerar_cpf()[:6],
                          especializacao='Clínico'))


def criar_enfermeiro(email='enf@test.com'):
    return _salvar(Enfermeiro(nome='Enfermeiro Teste', cpf=gerar_cpf(),
                              email=email, telefone='82999990004',
                              coren='COREN' + gerar_cpf()[:5]))


def criar_farmaceutico(email='farm@test.com'):
    return _salvar(Farmaceutico(nome='Farmaceutico Teste', cpf=gerar_cpf(),
                                email=email, telefone='82999990005',
                                crf='CRF' + gerar_cpf()[:5]))


def criar_paciente(email='paciente@test.com', id_prontuario=None):
    return _salvar(Paciente(nome='Paciente Teste', cpf=gerar_cpf(), email=email,
                            telefone='82999990006', dataNascimento='1990-05-20',
                            idProntuario=id_prontuario))
