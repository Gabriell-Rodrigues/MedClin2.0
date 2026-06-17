# View da página inicial (dashboard) do MedClin, com os atalhos para os módulos.

from django.shortcuts import render


def home(request):
    """
    Página inicial do sistema, com acesso aos módulos disponíveis.
    """

    return render(request, 'home.html', {'titulo': 'MedClin'})
