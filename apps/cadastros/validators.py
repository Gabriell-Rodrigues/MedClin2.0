# Contém validações reutilizáveis do módulo de cadastros, como a validação de CPF.

import re

from django.core.exceptions import ValidationError


def remover_mascara_cpf(cpf):
    """
    Remove pontos, traços, espaços e qualquer caractere que não seja número.

    Exemplo:
    123.456.789-09 -> 12345678909
    """

    return re.sub(r'\D', '', cpf or '')


def cpf_valido(cpf):
    """
    Verifica se um CPF é válido.

    Retorna:
    True  -> CPF válido
    False -> CPF inválido
    """

    cpf = remover_mascara_cpf(cpf)

    if len(cpf) != 11:
        return False

    if not cpf.isdigit():
        return False

    # Impede CPFs com todos os números iguais, como 11111111111
    if cpf == cpf[0] * 11:
        return False

    # Validação do primeiro dígito verificador
    soma = 0

    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    primeiro_digito = 11 - (soma % 11)

    if primeiro_digito >= 10:
        primeiro_digito = 0

    if primeiro_digito != int(cpf[9]):
        return False

    # Validação do segundo dígito verificador
    soma = 0

    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    segundo_digito = 11 - (soma % 11)

    if segundo_digito >= 10:
        segundo_digito = 0

    if segundo_digito != int(cpf[10]):
        return False

    return True


def validar_cpf(cpf):
    """
    Valida o CPF.

    Se o CPF for válido:
    - retorna o CPF limpo, somente com números.

    Se o CPF for inválido:
    - gera um erro de validação do Django.
    """

    cpf_limpo = remover_mascara_cpf(cpf)

    if not cpf_valido(cpf_limpo):
        raise ValidationError('CPF inválido.')

    return cpf_limpo


def formatar_cpf(cpf):
    """
    Formata o CPF para exibição na tela.

    Exemplo:
    12345678909 -> 123.456.789-09
    """

    cpf = remover_mascara_cpf(cpf)

    if len(cpf) != 11:
        return cpf

    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'