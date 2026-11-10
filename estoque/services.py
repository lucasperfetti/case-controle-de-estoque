from uuid import uuid4

from django.db import transaction

from .models import Produto, Movimentacao


def gerar_identificacao(tipo, identificacao=None):

    if identificacao:
        return identificacao.strip()

    prefixos = {
        'ENTRADA': 'ENT',
        'SAIDA': 'SAI',
        'RESERVA': 'RES',
        'BLOQUEIO': 'BLO',
    }

    return f"{prefixos[tipo]}-{uuid4().hex[:12].upper()}"


@transaction.atomic
def registrar_operacao(
    produto_id,
    tipo,
    quantidade,
    identificacao=None
):

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    produto = Produto.objects.select_for_update().get(
        id=produto_id
    )

    if tipo not in Movimentacao.Tipo.values:
        raise ValueError("Tipo de operação inválido.")

    if tipo in ['SAIDA', 'RESERVA', 'BLOQUEIO']:
        if quantidade > produto.quantidade_disponivel:
            raise ValueError("Estoque disponível insuficiente.")

    if tipo == 'ENTRADA':
        produto.quantidade_total += quantidade
        produto.quantidade_disponivel += quantidade

    elif tipo == 'SAIDA':
        produto.quantidade_total -= quantidade
        produto.quantidade_disponivel -= quantidade

    elif tipo == 'RESERVA':
        produto.quantidade_disponivel -= quantidade
        produto.quantidade_reservada += quantidade

    elif tipo == 'BLOQUEIO':
        produto.quantidade_disponivel -= quantidade
        produto.quantidade_bloqueada += quantidade

    if not produto.estoque_consistente:
        raise ValueError("Inconsistência nas quantidades do estoque.")

    produto.save()

    status = (
        Movimentacao.Status.ATIVO
        if tipo in ['RESERVA', 'BLOQUEIO']
        else Movimentacao.Status.CONCLUIDO
    )

    movimentacao = Movimentacao.objects.create(
        identificacao=gerar_identificacao(tipo, identificacao),
        produto=produto,
        tipo=tipo,
        quantidade=quantidade,
        status=status
    )

    return movimentacao


@transaction.atomic
def liberar_operacao(identificacao):

    try:
        movimentacao = Movimentacao.objects.select_for_update().get(
            identificacao=identificacao.strip()
        )
    except Movimentacao.DoesNotExist:
        raise ValueError("Operação não encontrada.")

    if movimentacao.tipo not in ['RESERVA', 'BLOQUEIO']:
        raise ValueError("Esta operação não pode ser liberada.")

    if movimentacao.status != Movimentacao.Status.ATIVO:
        raise ValueError("Esta operação já foi liberada ou finalizada.")

    produto = Produto.objects.select_for_update().get(
        id=movimentacao.produto_id
    )

    if movimentacao.tipo == 'RESERVA':
        produto.quantidade_reservada -= movimentacao.quantidade

    else:
        produto.quantidade_bloqueada -= movimentacao.quantidade

    produto.quantidade_disponivel += movimentacao.quantidade

    if not produto.estoque_consistente:
        raise ValueError("Inconsistência nas quantidades do estoque.")

    produto.save()

    movimentacao.status = Movimentacao.Status.LIBERADO
    movimentacao.save(update_fields=['status'])

    return movimentacao
