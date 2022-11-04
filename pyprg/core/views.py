
from django.http.response import JsonResponse
from django.shortcuts import render
from .models import Produto, Vendas, Vendedor
from datetime import datetime
from django.db.models import Sum


def home(request):
    # return HttpResponse("Home")
    return render(request,  'core/home.html')


def retorna_total_vendido(request):
    total = Vendas.objects.all().aggregate(Sum('total'))['total__sum']
    if request.method == "GET":
        return JsonResponse({'total': total})


def relatorio_faturamento(request):
    # mostra o faturamento nos ultimos 12 meses
    x = Vendas.objects.all()

    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
    data = []
    labels = []
    cont = 0
    mes = datetime.now().month + 1
    ano = datetime.now().year
    for i in range(12):
        # pois no python começamos sempre com 0
        mes -= 1
        if mes == 0:  # relatorio dos ultimos 12 meses. Do mes atual ate o ano anterior
            mes = 12
            ano -= 1

        y = sum([i.total for i in x if i.data.month == mes and i.data.year == ano])
        labels.append(meses[mes-1])
        data.append(y)
        cont += 1

    # fazer a inversão das listas data e labels
    data_json = {'data': data[::-1], 'labels': labels[::-1]}

    return JsonResponse(data_json)


def relatorio_produtos(request):
    produtos = Produto.objects.all()
    label = []
    data = []
    for produto in produtos:
        vendas = Vendas.objects.filter(nome_produto=produto).aggregate(Sum('total'))
        if not vendas['total__sum']:
            # se não tiver nenhum produto convertemos none para zero
            vendas['total__sum'] = 0
        label.append(produto.nome)
        data.append(vendas['total__sum'])
    # a função zip faz um link entre label e data
    x = list(zip(label, data))

    # ordenar a lista pela posição 1 que é valor na ordem reversa do maior para o menor
    x.sort(key=lambda x: x[1], reverse=True)
    # * para fazer a descompatação no python
    x = list(zip(*x))

    # label na posição zero e valor na posição 1
    return JsonResponse({'labels': x[0][:3], 'data': x[1][:3]})


def relatorio_funcionario(request):
    vendedores = Vendedor.objects.all()
    label = []
    data = []
    for vendedor in vendedores:
        vendas = Vendas.objects.filter(vendedor=vendedor).aggregate(Sum('total'))
        if not vendas['total__sum']:
            vendas['total__sum'] = 0
        label.append(vendedor.nome)
        data.append(vendas['total__sum'])

    x = list(zip(label, data))

    x.sort(key=lambda x: x[1], reverse=True)
    x = list(zip(*x))

    return JsonResponse({'labels': x[0][:3], 'data': x[1][:3]})
