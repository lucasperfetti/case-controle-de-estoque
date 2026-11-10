
from django.db import models
from django.core.validators import MinValueValidator


class Produto(models.Model):

    identificacao = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Identificação"
    )

    quantidade_total = models.PositiveIntegerField(default=0)
    quantidade_disponivel = models.PositiveIntegerField(default=0)
    quantidade_reservada = models.PositiveIntegerField(default=0)
    quantidade_bloqueada = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.identificacao

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    @property
    def estoque_consistente(self):
        return (
            self.quantidade_total ==
            self.quantidade_disponivel +
            self.quantidade_reservada +
            self.quantidade_bloqueada
        )


class Movimentacao(models.Model):

    class Tipo(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SAIDA = 'SAIDA', 'Saída'
        RESERVA = 'RESERVA', 'Reserva'
        BLOQUEIO = 'BLOQUEIO', 'Bloqueio'

    class Status(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        LIBERADO = 'LIBERADO', 'Liberado'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    identificacao = models.CharField(
        max_length=50,
        unique=True
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return f"{self.identificacao} - {self.produto.identificacao}"
