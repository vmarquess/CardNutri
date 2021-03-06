import base_dados as bd
import random
from operator import itemgetter


def ini_populacao(dias, refeicao):
    # refeicao = 0 -> todas refeicoes
    # Dias no máximo 5

    lista = list()

    if refeicao == 0:
        refeicao = bd.tipos_refeicao

    if isinstance(refeicao, list):
        for i in range(0, dias):
            guarda_cardapio = dict()
            for refeicoes in refeicao:
                aux = refeicoes.gerar_cardapio()
                guarda_cardapio.update({refeicoes.nome: aux})
            lista.append(guarda_cardapio)

    else:
        guarda_cardapio = dict()
        for i in range(0, dias):
            aux = refeicao.gerar_cardapio()
            guarda_cardapio.update({refeicao.nome: aux})
            lista.append(guarda_cardapio)

    return lista


def funcao_fitness(populacao, tipo):
    fitness_valores = dict()
    if tipo == 1:
        for i in range(0, len(populacao)):
            fitness = funcao_objetivo(populacao[i])
            fitness_valores[i] = fitness
    else:
        for i in range(0, len(populacao)):
            fitness = funcao_objetivo(populacao[i])
            fitness_valores[fitness] = i

    return fitness_valores


def funcao_objetivo(cardapio):
    f1 = calcularErroNutri(cardapio)
    f2 = calcularCusto(cardapio)

    aptidao = (0.6 * f1) + (0.4 * f2)
    aptidao = round(aptidao, 3)

    return aptidao


def calcularErroNutri(cardapio):
    nutriCardapio = dict(Energia=0,
                         Proteína=0,
                         Lipídeos=0,
                         Carboidrato=0,
                         Fibra=0,
                         Cálcio=0,
                         Magnésio=0,
                         Ferro=0,
                         Zinco=0)

    for dia in cardapio:
        for refeicao in dia:
            for pratos in dia[refeicao]:
                for chave in nutriCardapio.keys():
                    valor = nutriCardapio[chave]
                    valor = valor + pratos.nutrientesTotal[chave]
                    nutriCardapio[chave] = valor

    # Restrição das cores

    coreslist = list()
    for dia in cardapio:
        for refeicao in dia:
            cores = dict(Amarelo=0, Vermelho=0, Verde=0, Marrom=0)
            for pratos in dia[refeicao]:
                if pratos.cor == 'Amarelo':
                    cores['Amarelo'] += 1
                if pratos.cor == 'Vermelho':
                    cores['Vermelho'] += 1
                if pratos.cor == 'Verde':
                    cores['Verde'] += 1
                if pratos.cor == 'Marrom':
                    cores['Marrom'] += 1
            coreslist.append(cores)

    r1total = 0
    for cor in coreslist:
        if cor['Amarelo'] > 2:
            r1 = (cor['Amarelo'] - 2)
            r1total += r1
        if cor['Vermelho'] > 2:
            r1 = (cor['Vermelho'] - 2)
            r1total += r1
        if cor['Verde'] > 2:
            r1 = (cor['Verde'] - 2)
            r1total += r1
        if cor['Marrom'] > 2:
            r1 = (cor['Marrom'] - 2)
            r1total += r1

    # Restrição Consistencia

    liqpas = 0
    for dia in cardapio:
        for refeicao in dia:
            for pratos in dia[refeicao]:
                if pratos.consistencia == 'Liquída' or pratos.consistencia == 'Pastosa':
                    liqpas += 1

    if liqpas > 1:
        r2 = liqpas
    else:
        r2 = 0

    # Restrição Variedade

    repeticao = 0
    for dia in cardapio:
        for pratoAlmoco in dia['Almoço']:
            if pratoAlmoco in dia['Jantar']:
                repeticao += 1

        for pratosLanche in dia['Lanche']:
            if pratosLanche in dia['Desjejum']:
                repeticao += 1

    indice = 0
    listIndRepet = list()
    for dia in cardapio:
        for diaComparacao in range(0, len(cardapio)):
            if indice != diaComparacao:
                for pratoAlmoco in dia['Almoço']:
                    if pratoAlmoco in cardapio[diaComparacao]['Jantar']:
                        if diaComparacao + indice not in listIndRepet:
                            listIndRepet.append(diaComparacao + indice)
        indice += 1

    repeticao += len(listIndRepet)

    for chave in nutriCardapio:
        valor = nutriCardapio[chave]
        valor = bd.refNutricional[chave] - valor
        nutriCardapio[chave] = abs(valor)

    erroInicial = 0

    for chave in nutriCardapio:
        erroInicial += abs(nutriCardapio[chave])

    erroInicial = erroInicial / len(nutriCardapio)

    totalRestricoes = r1total + r2 + (repeticao * 2)
    erroFinal = erroInicial + totalRestricoes

    return erroFinal


def calcularCusto(cardapio):
    custoCardapio = 0
    w = 0

    for dia in cardapio:
        for refeicao in dia:
            for pratos in dia[refeicao]:
                custoCardapio += float(pratos.preco)

    if custoCardapio > bd.refNutricional['CustoAluno']:
        w = 1

    penalidade = w * bd.refNutricional['CustoAluno']

    return custoCardapio + penalidade


def funcao_dizimacao_corte(pop, fitn):
    fitnessOrdenado = sorted(fitn.items(), key=itemgetter(1))
    qtdRemocao = int(len(pop) * 0.4)
    remover = list()

    for cont in range(len(fitnessOrdenado) - 1, len(fitnessOrdenado) - qtdRemocao - 1, -1):
        remover.append(pop[fitnessOrdenado[cont][0]])

    for valor in remover:
        pop.remove(valor)

    return pop


def funcao_dizimacao_pais(pop):
    pais = list()

    pai1 = random.randint(0, len(pop) - 1)
    pais.append(pop[pai1])

    pai2 = pai1
    while pai2 == pai1:
        pai2 = random.randint(0, len(pop) - 1)

    pais.append(pop[pai2])

    return pais


def cruzamento(pais, taxa_cruzamento):
    filhos1_lista = list()
    filhos2_lista = list()
    filhos = list()

    if random.random() < taxa_cruzamento:
        for dia in range(0, len(pais[0])):
            filhoAux1 = dict()
            filhoAux2 = dict()
            for refeicao in pais[0][0].keys():
                tamanho = len(pais[0][0][refeicao])
                corte = random.randint(0, tamanho - 2) + 1
                filho1 = pais[0][dia][refeicao][0:corte] + pais[1][dia][refeicao][corte:tamanho]
                filho2 = pais[1][dia][refeicao][0:corte] + pais[0][dia][refeicao][corte:tamanho]

                filhoAux1.update({refeicao: filho1})
                filhoAux2.update({refeicao: filho2})
            filhos1_lista.append(filhoAux1)
            filhos2_lista.append(filhoAux2)
        filhos.append(filhos1_lista)
        filhos.append(filhos2_lista)
    else:
        filhos.append(pais[0])
        filhos.append(pais[1])

    return filhos


def mutacao(filhos, taxa_mutacao):
    if random.random() < taxa_mutacao:
        for filho in filhos:
            dias = len(filho)
            dia_escolhido = random.randint(0, dias - 1)
            for refeicao in filho[dia_escolhido]:
                qtd_pratos = len(filho[dia_escolhido][refeicao])
                indice_mut = random.randint(0, qtd_pratos - 1)
                mutado = filho[dia_escolhido][refeicao][indice_mut]

                while mutado == filho[dia_escolhido][refeicao][indice_mut]:
                    mutado = random.choice(bd.pratos_grupo[filho[dia_escolhido][refeicao][indice_mut].tipo])

                filho[dia_escolhido][refeicao][indice_mut] = mutado

    return filhos
