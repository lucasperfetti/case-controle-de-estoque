from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum

from .models import Produto, Movimentacao
from .forms import ProdutoForm, OperacaoForm, LiberacaoForm
from .services import registrar_operacao, liberar_operacao


def dashboard(request):

    produtos = Produto.objects.all()

    contexto = {
        'total_produtos': produtos.count(),
        'total_disponivel': produtos.aggregate(
            total=Sum('quantidade_disponivel')
        )['total'] or 0,

        'total_reservado': produtos.aggregate(
            total=Sum('quantidade_reservada')
        )['total'] or 0,

        'total_bloqueado': produtos.aggregate(
            total=Sum('quantidade_bloqueada')
        )['total'] or 0,

        'movimentacoes': Movimentacao.objects.all()[:10],
    }

    return render(request, 'estoque/dashboard.html', contexto)


def produtos(request):

    lista = Produto.objects.all().order_by('identificacao')

    return render(request, 'estoque/produtos.html', {
        'produtos': lista
    })


def cadastrar_produto(request):

    form = ProdutoForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            messages.success(request, "Produto cadastrado com sucesso!")
            return redirect('produtos')

    return render(request, 'estoque/cadastrar_produto.html', {
        'form': form
    })


def operacao(request, tipo):

    tipos_validos = ['ENTRADA', 'SAIDA', 'RESERVA', 'BLOQUEIO']

    if tipo not in tipos_validos:
        return redirect('dashboard')

    form = OperacaoForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            try:
                movimentacao = registrar_operacao(
                    produto_id=form.cleaned_data['produto'].id,
                    tipo=tipo,
                    quantidade=form.cleaned_data['quantidade'],
                    identificacao=form.cleaned_data['identificacao']
                )

                messages.success(
                    request,
                    f"Operação realizada! Identificação: {movimentacao.identificacao}"
                )

                return redirect('dashboard')

            except ValueError as erro:
                messages.error(request, str(erro))

    return render(request, 'estoque/operacao.html', {
        'form': form,
        'tipo': tipo
    })


def liberar(request):

    form = LiberacaoForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            try:
                movimentacao = liberar_operacao(
                    form.cleaned_data['identificacao']
                )

                messages.success(
                    request,
                    f"Operação {movimentacao.identificacao} liberada!"
                )

                return redirect('dashboard')

            except ValueError as erro:
                messages.error(request, str(erro))

    return render(request, 'estoque/liberar.html', {
        'form': form
    })


def consultar(request):

    produto = None

    identificacao = request.GET.get('identificacao', '').strip()

    if identificacao:
        produto = Produto.objects.filter(
            identificacao__iexact=identificacao
        ).first()

        if not produto:
            messages.error(request, "Produto não encontrado.")

    return render(request, 'estoque/consultar.html', {
        'produto': produto,
        'identificacao': identificacao
    })
