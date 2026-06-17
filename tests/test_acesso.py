# Testes de autenticação (UC-01) e controle de acesso por perfil (RBAC).

from django.test import TestCase
from django.urls import reverse

from .helpers import (
    SENHA, mascarar_cpf,
    criar_gestor, criar_recepcionista, criar_medico, criar_paciente,
)


class LoginTests(TestCase):
    def setUp(self):
        self.recep = criar_recepcionista('recep@test.com')

    def test_login_por_email(self):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': 'recep@test.com', 'senha': SENHA})
        self.assertEqual(self.client.session.get('usuario_perfil'), 'recepcionista')

    def test_login_por_cpf_sem_mascara(self):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': self.recep.cpf, 'senha': SENHA})
        self.assertEqual(self.client.session.get('usuario_perfil'), 'recepcionista')

    def test_login_por_cpf_com_mascara(self):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': mascarar_cpf(self.recep.cpf), 'senha': SENHA})
        self.assertEqual(self.client.session.get('usuario_perfil'), 'recepcionista')

    def test_login_senha_errada_falha(self):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': 'recep@test.com', 'senha': 'errada'})
        self.assertIsNone(self.client.session.get('usuario_perfil'))

    def test_senha_armazenada_com_argon2(self):
        self.assertTrue(self.recep.senha.startswith('argon2'))


class RBACTests(TestCase):
    def setUp(self):
        self.gestor = criar_gestor('g@test.com')
        self.recep = criar_recepcionista('r@test.com')
        self.paciente = criar_paciente('p@test.com')

    def _login(self, email):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': email, 'senha': SENHA})

    def test_paciente_nao_acessa_lista_de_consultas(self):
        self._login('p@test.com')
        resp = self.client.get(reverse('atendimento:consulta_listar'))
        self.assertEqual(resp.status_code, 403)

    def test_paciente_nao_acessa_lista_de_prontuarios(self):
        self._login('p@test.com')
        resp = self.client.get(reverse('prontuario:prontuario_listar'))
        self.assertEqual(resp.status_code, 403)

    def test_recepcionista_acessa_pacientes(self):
        self._login('r@test.com')
        resp = self.client.get(reverse('cadastros:paciente_listar'))
        self.assertEqual(resp.status_code, 200)

    def test_gestor_acessa_funcionarios(self):
        self._login('g@test.com')
        resp = self.client.get(reverse('acesso:funcionario_listar', args=['medico']))
        self.assertEqual(resp.status_code, 200)

    def test_anonimo_redirecionado_para_login(self):
        resp = self.client.get(reverse('cadastros:paciente_listar'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('acesso:login'), resp['Location'])
