import json
import os
import datetime
import re

ARQ = "alunos.json"

# =====================================================
# FUNÇÕES DE BANCO DE DADOS
# =====================================================

def carregar():
    if not os.path.exists(ARQ):
        return []
    with open(ARQ, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def salvar(lista):
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

# =====================================================
# PROCESSAMENTO INTELIGENTE DO DIA DE VENCIMENTO
# =====================================================

def limpar_dia(dia):
    """
    Recebe qualquer entrada e tenta extrair um número entre 1 e 28.
    """
    dia = dia.strip().lower()

    # PROCURA NÚMEROS NA STRING
    numeros = re.findall(r"\d+", dia)
    if numeros:
        dia_num = int(numeros[-1])  # último número encontrado
        if 1 <= dia_num <= 28:
            return dia_num

    # SE NADA SERVIR, RETORNAR ERRO
    return None

# =====================================================
# FUNÇÕES DE DATA
# =====================================================

def calc_prox_venc(dia):
    hoje = datetime.date.today()
    ano, mes = hoje.year, hoje.month

    if hoje.day > dia:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

    return datetime.date(ano, mes, dia)

def status_pagamento(data_venc):
    hoje = datetime.date.today()

    if hoje == data_venc:
        return "⚠ VENCE HOJE!"

    if hoje > data_venc:
        dias = (hoje - data_venc).days
        return f"❌ ATRASADO {dias} dias"

    dias = (data_venc - hoje).days
    return f"✔ Faltam {dias} dias"

# =====================================================
# SISTEMA PRINCIPAL
# =====================================================

def cadastrar():
    print("\n=== CADASTRO DE ALUNO ===")

    nome = input("Nome completo: ").strip().title()

    # PROCESSAR DIA DE VENCIMENTO
    while True:
        dia_raw = input("Dia do vencimento mensal (1–28): ").strip()
        dia = limpar_dia(dia_raw)

        if dia:
            break
        else:
            print("Entrada inválida! Exemplo correto: 5, 10, 15, 'dia 10', '5-10'.")

    venc = calc_prox_venc(dia)

    aluno = {
        "nome": nome,
        "dia_venc": dia,
        "proximo_venc": venc.isoformat()
    }

    dados = carregar()
    dados.append(aluno)
    salvar(dados)

    print(f"\nAluno {nome} cadastrado com sucesso.")
    print(f"Próximo vencimento: {venc}\n")

def listar():
    print("\n=== LISTA DE ALUNOS ===")

    dados = carregar()
    if not dados:
        print("Nenhum aluno cadastrado.\n")
        return

    for a in dados:
        print(f"Aluno: {a['nome']}")
        print(f"Dia do vencimento: {a['dia_venc']}")
        print(f"Próximo vencimento: {a['proximo_venc']}")
        print("-" * 50)

def alertas():
    print("\n=== ALERTAS DE PAGAMENTO – ACADEMIA SUNSET ===")
    
    dados = carregar()
    if not dados:
        print("Nenhum aluno cadastrado.\n")
        return

    hoje = datetime.date.today()
    print(f"Hoje: {hoje}\n")

    mudou = False

    for a in dados:
        venc = datetime.date.fromisoformat(a["proximo_venc"])
        stat = status_pagamento(venc)

        print(f"Aluno: {a['nome']}")
        print(f"Status: {stat}")

        # ATUALIZAÇÃO AUTOMÁTICA DO PRÓXIMO VENCIMENTO
        if hoje > venc:
            novo = calc_prox_venc(a["dia_venc"])
            a["proximo_venc"] = novo.isoformat()
            mudou = True
            print(f"➡ Novo vencimento reagendado para {novo}")

        print("-" * 50)

    if mudou:
        salvar(dados)

def menu():
    while True:
        print("""
=== SISTEMA DE PORTARIA - SUNSET FITNESS ===

1 - Cadastrar aluno
2 - Listar alunos
3 - Ver alertas de pagamento
0 - Sair
""")
        opc = input("Escolha uma opção: ").strip()

        if opc == "1":
            cadastrar()
        elif opc == "2":
            listar()
        elif opc == "3":
            alertas()
        elif opc == "0":
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    print("Sistema Sunset Fitness iniciado.\n")
    menu()
