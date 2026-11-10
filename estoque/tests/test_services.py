
from django.test import TestCase

from estoque.models import Produto, Movimentacao
from estoque.services import registrar_operacao, liberar_operacao


class EstoqueServiceTests(TestCase):

    def setUp(self):
        """Cria um produto para ser utilizado nos testes."""
        self.produto = Produto.objects.create(
            identificacao="PROD-TESTE"
        )

    def adicionar_estoque(self, quantidade=10):
        """Adiciona estoque inicial para os testes."""
        registrar_operacao(
            produto_id=self.produto.id,
            tipo="ENTRADA",
            quantidade=quantidade
        )
        self.produto.refresh_from_db()

    def test_entrada_aumenta_estoque(self):
        """Uma entrada deve aumentar o total e o disponível."""
        registrar_operacao(
            self.produto.id, "ENTRADA", 10
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_total, 10)
        self.assertEqual(self.produto.quantidade_disponivel, 10)

    def test_saida_diminui_estoque(self):
        """Uma saída deve diminuir o total e o disponível."""
        self.adicionar_estoque(10)

        registrar_operacao(
            self.produto.id, "SAIDA", 4
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_total, 6)
        self.assertEqual(self.produto.quantidade_disponivel, 6)

    def test_saida_com_estoque_insuficiente(self):
        """Não deve permitir saída maior que o disponível."""
        self.adicionar_estoque(5)

        with self.assertRaises(ValueError):
            registrar_operacao(
                self.produto.id, "SAIDA", 10
            )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_total, 5)
        self.assertEqual(self.produto.quantidade_disponivel, 5)

    def test_reserva_reduz_disponivel(self):
        """Uma reserva deve transferir o saldo para reservado."""
        self.adicionar_estoque(10)

        movimentacao = registrar_operacao(
            self.produto.id,
            "RESERVA",
            4,
            "RES-TESTE"
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_disponivel, 6)
        self.assertEqual(self.produto.quantidade_reservada, 4)
        self.assertEqual(movimentacao.status, "ATIVO")

    def test_bloqueio_reduz_disponivel(self):
        """Um bloqueio deve transferir o saldo para bloqueado."""
        self.adicionar_estoque(10)

        movimentacao = registrar_operacao(
            self.produto.id,
            "BLOQUEIO",
            3,
            "BLO-TESTE"
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_disponivel, 7)
        self.assertEqual(self.produto.quantidade_bloqueada, 3)
        self.assertEqual(movimentacao.status, "ATIVO")

    def test_liberar_reserva_devolve_quantidade(self):
        """A liberação deve devolver o saldo reservado."""
        self.adicionar_estoque(10)

        registrar_operacao(
            self.produto.id,
            "RESERVA",
            4,
            "RES-TESTE"
        )

        liberar_operacao("RES-TESTE")

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_disponivel, 10)
        self.assertEqual(self.produto.quantidade_reservada, 0)

    def test_nao_permitir_liberacao_dupla(self):
        """Uma reserva não pode ser liberada duas vezes."""
        self.adicionar_estoque(10)

        registrar_operacao(
            self.produto.id,
            "RESERVA",
            4,
            "RES-TESTE"
        )

        liberar_operacao("RES-TESTE")

        with self.assertRaises(ValueError):
            liberar_operacao("RES-TESTE")

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_disponivel, 10)
        self.assertEqual(self.produto.quantidade_reservada, 0)

    def test_estoque_permanece_consistente(self):
        """A soma dos saldos deve corresponder ao total."""
        self.adicionar_estoque(20)

        registrar_operacao(
            self.produto.id, "RESERVA", 5
        )

        registrar_operacao(
            self.produto.id, "BLOQUEIO", 3
        )

        self.produto.refresh_from_db()

        self.assertEqual(
            self.produto.quantidade_total,
            self.produto.quantidade_disponivel
            + self.produto.quantidade_reservada
            + self.produto.quantidade_bloqueada
        )
