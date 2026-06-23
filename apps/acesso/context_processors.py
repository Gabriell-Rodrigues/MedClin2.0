# Context processor de acesso: expõe o perfil logado e flags de navegação para
# que o menu mostre apenas os módulos permitidos a cada perfil.
#
# As flags espelham as permissões dos decorators (apps/acesso/decorators.py),
# seguindo a Matriz de Atores x Casos de Uso.


def usuario(request):
    perfil = request.session.get('usuario_perfil')

    def algum(*perfis):
        return perfil in perfis

    return {
        'perfil_atual': perfil,
        'usuario_logado': bool(request.session.get('usuario_id')),
        'nav': {
            'pacientes': algum('recepcionista'),
            'consultas': algum('recepcionista', 'medico', 'paciente'),
            'prontuarios': algum('medico', 'enfermeiro', 'farmaceutico', 'paciente'),
            'medicamentos': algum('farmaceutico', 'gestor'),
            'materiais': algum('enfermeiro', 'gestor'),
            'funcionarios': algum('gestor'),
            'pagamentos': algum('recepcionista'),
            'relatorio': algum('gestor'),
            'notificacoes': algum('gestor'),
        },
    }
