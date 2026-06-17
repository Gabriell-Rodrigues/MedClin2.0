# Testes da trilha de auditoria (rastreabilidade via logging, sem tabela).
# Verifica que ações relevantes emitem um registro no logger 'medclin.auditoria'.

from django.test import TestCase

from apps.farmacia.entity_estoque.models import Medicamento
from apps.farmacia.control_ctr_estoque.services import CTRMedicamento
from apps.prontuario.entity_prontuario.models import Prontuario
from apps.prontuario.control_ctr_prontuario.services import CTRProntuario


class AuditoriaTests(TestCase):
    def test_dispensacao_gera_registro_de_auditoria(self):
        med = Medicamento.objects.create(nome='Dipirona', quantidadeEstoque=10,
                                         quantidadeMinima=2)
        with self.assertLogs('medclin.auditoria', level='INFO') as captura:
            CTRMedicamento.dispensar(med, 2, id_farmaceutico=1, id_prontuario=3)
        self.assertTrue(any('farmacia' in linha for linha in captura.output))

    def test_evolucao_gera_registro_de_auditoria(self):
        pr = Prontuario.objects.create()
        CTRProntuario.conceder_acesso(pr, 'medico', 10)
        with self.assertLogs('medclin.auditoria', level='INFO') as captura:
            CTRProntuario.registrar_evolucao(pr, 10, 'Diag', 'Obs', 'Presc')
        self.assertTrue(any('prontuario' in linha for linha in captura.output))
