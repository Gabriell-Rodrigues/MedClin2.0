# Testes do UC-02 (Redefinir Senha) por link/token, sem tabela de token.

from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.acesso.control_ctr_funcionario.services import CTRAutenticacao
from .helpers import criar_recepcionista, SENHA


class RedefinicaoSenhaTests(TestCase):
    def setUp(self):
        self.user = criar_recepcionista('rec@test.com')

    def test_solicitar_envia_email_com_link(self):
        self.client.post(reverse('acesso:redefinir_senha'),
                         {'email': 'rec@test.com'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('senha/redefinir/', mail.outbox[0].body)

    def test_email_inexistente_nao_envia_e_nao_revela(self):
        resp = self.client.post(reverse('acesso:redefinir_senha'),
                                {'email': 'naoexiste@test.com'}, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(resp.status_code, 200)

    def test_fluxo_completo_redefine_e_loga_com_nova_senha(self):
        token, _ = CTRAutenticacao.gerar_token_redefinicao('rec@test.com')
        url = reverse('acesso:redefinir_senha_confirmar', args=[token])
        self.client.post(url, {'nova_senha': 'NovaSenha@1',
                               'confirmar_senha': 'NovaSenha@1'})

        # A senha antiga não funciona mais; a nova funciona.
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': 'rec@test.com', 'senha': SENHA})
        self.assertIsNone(self.client.session.get('usuario_perfil'))

        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': 'rec@test.com', 'senha': 'NovaSenha@1'})
        self.assertEqual(self.client.session.get('usuario_perfil'), 'recepcionista')

    def test_token_e_de_uso_unico(self):
        token, _ = CTRAutenticacao.gerar_token_redefinicao('rec@test.com')
        CTRAutenticacao.redefinir_senha_com_token(token, 'NovaSenha@1')
        with self.assertRaises(ValidationError):
            CTRAutenticacao.redefinir_senha_com_token(token, 'OutraSenha@2')

    def test_token_invalido_e_rejeitado(self):
        with self.assertRaises(ValidationError):
            CTRAutenticacao.validar_token_redefinicao('token-invalido')

    def test_senhas_diferentes_sao_rejeitadas(self):
        token, _ = CTRAutenticacao.gerar_token_redefinicao('rec@test.com')
        url = reverse('acesso:redefinir_senha_confirmar', args=[token])
        resp = self.client.post(url, {'nova_senha': 'A@123456',
                                      'confirmar_senha': 'B@123456'})
        # Formulário inválido: permanece na página (não redireciona ao login).
        self.assertEqual(resp.status_code, 200)
