# Testes do módulo de Farmácia: dispensação (UC-13) e consumo de material,
# com baixa de estoque transacional.

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.farmacia.entity_estoque.models import (
    Material, Medicamento, MaterialConsumido, MedicamentoDispensado,
)
from apps.farmacia.control_ctr_estoque.services import CTRMateriais, CTRMedicamento


class DispensacaoTests(TestCase):
    def test_dispensar_da_baixa_e_registra(self):
        med = Medicamento.objects.create(nome='Dipirona', quantidadeEstoque=10,
                                         quantidadeMinima=2)
        disp = CTRMedicamento.dispensar(med, 3, id_farmaceutico=1, id_prontuario=5)
        med.refresh_from_db()
        self.assertEqual(med.quantidadeEstoque, 7)
        self.assertTrue(
            MedicamentoDispensado.objects.filter(pk=disp.pk, idProntuario=5,
                                                 idFarmaceutico=1).exists()
        )

    def test_dispensar_sem_estoque_faz_rollback(self):
        med = Medicamento.objects.create(nome='Amoxicilina', quantidadeEstoque=1,
                                         quantidadeMinima=0)
        with self.assertRaises(ValidationError):
            CTRMedicamento.dispensar(med, 5, id_farmaceutico=1)
        med.refresh_from_db()
        self.assertEqual(med.quantidadeEstoque, 1)
        self.assertEqual(MedicamentoDispensado.objects.count(), 0)

    def test_dispensar_exige_farmaceutico(self):
        med = Medicamento.objects.create(nome='Soro', quantidadeEstoque=5,
                                         quantidadeMinima=0)
        with self.assertRaises(ValidationError):
            CTRMedicamento.dispensar(med, 1, id_farmaceutico=None)


class ConsumoMaterialTests(TestCase):
    def test_consumo_da_baixa_e_registra(self):
        mat = Material.objects.create(nome='Luva', quantidadeEstoque=5,
                                      quantidadeMinima=1)
        cons = CTRMateriais.registrar_consumo(mat, 2, id_enfermeiro=4)
        mat.refresh_from_db()
        self.assertEqual(mat.quantidadeEstoque, 3)
        self.assertTrue(
            MaterialConsumido.objects.filter(pk=cons.pk, idEnfermeiro=4).exists()
        )

    def test_consumo_sem_estoque_faz_rollback(self):
        mat = Material.objects.create(nome='Gaze', quantidadeEstoque=1,
                                      quantidadeMinima=0)
        with self.assertRaises(ValidationError):
            CTRMateriais.registrar_consumo(mat, 10, id_enfermeiro=4)
        mat.refresh_from_db()
        self.assertEqual(mat.quantidadeEstoque, 1)
        self.assertEqual(MaterialConsumido.objects.count(), 0)
