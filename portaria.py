import sqlite3
import datetime
import random
import calendar

DB_NAME = "sunset_academia.db"


# =============================
# BANCO DE DADOS
# =============================
def iniciar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            biometria_hash TEXT NOT NULL,
            vencimento TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            autorizado TEXT NOT NULL,
            motivo TEXT
        )
    """
    )

    conn.commit()
    conn.close()


# =============================
# FUNÇÕES DE APOIO
# =============================
def hoje() -> datetime.date:
    return datetime.date.today()



def str_para_data(data_str: str) -> datetime.date:
    """Converte string para data aceitando vários formatos comuns."""
    data_str = data_str.strip()
    formatos = [
        "%Y-%m-%d",  # 2026-04-02
        "%d/%m/%Y",  # 02/04/2026
        "%d-%m-%Y",  # 02-04-2026
    ]
    for fmt in formatos:
        try:
            return datetime.datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    # Se não bater com nenhum formato, dispara erro
    raise ValueError(f"Formato de data inválido: {data_str}")


def data_para_str(data: datetime.date) -> str:
    return data.strftime("%Y-%m-%d")


def adicionar_um_mes(data: datetime.date) -> datetime.date:
    """Avança 1 mês respeitando mudança de ano e último dia do mês."""
    ano = data.year
    mes = data.month + 1
    if mes > 12:
        mes = 1
        ano += 1

    dia = data.day
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    if dia > ultimo_dia:
        dia = ultimo_dia

    return datetime.date(ano, mes, dia)


def gerar_biometria_fake() -> str:
    """Simula uma biometria retornando um código aleatório."""
    return str(random.randint(100000, 999999))


def calcular_status(vencimento_str: str) -> str:
    """Retorna EM_DIA, VENCE_HOJE ou ATRASADO"""
    hoje_data = hoje()
    venc = str_para_data(vencimento_str)
    if venc < hoje_data:
        return "ATRASADO"
    elif venc == hoje_data:
        return "VENCE_HOJE"
    else:
        return "EM_DIA"


def registrar_log(matricula: str, autorizado: str, motivo: str | None = None) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    agora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO acessos (matricula, data_hora, autorizado, motivo)
        VALUES (?, ?, ?, ?)
        """,
        (matricula, agora_str, autorizado, motivo),
    )

    conn.commit()
    conn.close()


# =============================
# FUNÇÕES DO SISTEMA - ALUNOS
# =============================
def cadastrar_aluno():
    print("\n=== CADASTRAR NOVO ALUNO – ACADEMIA SUNSET ===")
    nome = input("Nome do aluno: ").strip()
    if not nome:
        print("Nome inválido.")
        return

    matricula = input("Matrícula (código único): ").strip()
    if not matricula:
        print("Matrícula inválida.")
        return

    biometria = gerar_biometria_fake()
    print(f"Biometria gerada automaticamente (simulada): {biometria}")

    vencimento_str = input("Primeira data de vencimento (AAAA-MM-DD): ").strip()
    try:
        data_venc = str_para_data(vencimento_str)
    except ValueError:
        print("Data inválida. Aluno não cadastrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO alunos (nome, matricula, biometria_hash, vencimento)
            VALUES (?, ?, ?, ?)
            """,
            (nome, matricula, biometria, data_para_str(data_venc)),
        )
        conn.commit()
        print("✅ Aluno cadastrado com sucesso!")
        print(f"   Matrícula: {matricula}")
        print(f"   Biometria (simulação): {biometria}")
        print(f"   Vencimento: {data_para_str(data_venc)}")
    except sqlite3.IntegrityError:
        print("Já existe um aluno com essa matrícula.")
    finally:
        conn.close()


def listar_alunos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT nome, matricula, biometria_hash, vencimento FROM alunos ORDER BY nome;")
    alunos = cursor.fetchall()
    conn.close()

    if not alunos:
        print("\nNenhum aluno cadastrado.")
        return

    print("\n=== LISTA DE ALUNOS – ACADEMIA SUNSET ===")
    for nome, matricula, bio, venc in alunos:
        status = calcular_status(venc)
        if status == "EM_DIA":
            status_legivel = "EM DIA"
        elif status == "VENCE_HOJE":
            status_legivel = "VENCE HOJE"
        else:
            status_legivel = "EM ATRASO"

        print(
            f"Aluno: {nome} | Matrícula: {matricula} | Bio: {bio} | "
            f"Vencimento: {venc} | Status: {status_legivel}"
        )


# =============================
# PAGAMENTOS AUTOMÁTICOS
# =============================
def registrar_pagamento():
    print("\n=== REGISTRAR PAGAMENTO DE MENSALIDADE ===")
    matricula = input("Informe a matrícula do aluno: ").strip()
    if not matricula:
        print("Matrícula inválida.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome, vencimento FROM alunos WHERE matricula = ?;",
        (matricula,),
    )
    row = cursor.fetchone()
    if not row:
        print("Aluno não encontrado.")
        conn.close()
        return

    nome, vencimento_str = row
    venc_atual = str_para_data(vencimento_str)
    novo_venc = adicionar_um_mes(venc_atual)

    print(f"Aluno: {nome}")
    print(f"Vencimento atual: {data_para_str(venc_atual)}")
    print(f"Novo vencimento após pagamento: {data_para_str(novo_venc)}")

    confirma = input("Confirmar pagamento e avançar vencimento? (s/n): ").strip().lower()
    if confirma != "s":
        print("Operação cancelada.")
        conn.close()
        return

    cursor.execute(
        "UPDATE alunos SET vencimento = ? WHERE matricula = ?;",
        (data_para_str(novo_venc), matricula),
    )
    conn.commit()
    conn.close()
    print("✅ Pagamento registrado e vencimento atualizado.")


def mostrar_alertas():
    """Mostra quem vence hoje e quem está em atraso ao iniciar o sistema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT nome, matricula, vencimento FROM alunos;")
    alunos = cursor.fetchall()
    conn.close()

    if not alunos:
        return

    hoje_data = hoje()
    print("\n=== ALERTAS DE PAGAMENTO – ACADEMIA SUNSET ===")
    algum_alerta = False
    for nome, matricula, venc in alunos:
        venc_data = str_para_data(venc)
        if venc_data == hoje_data:
            print(f"⚠️ Mensalidade de {nome} (Mat: {matricula}) VENCE HOJE ({venc}).")
            algum_alerta = True
        elif venc_data < hoje_data:
            print(f"🚫 {nome} (Mat: {matricula}) está EM ATRASO. Venceu em {venc}.")
            algum_alerta = True

    if not algum_alerta:
        print("Nenhum aluno com vencimento hoje ou em atraso.")


# =============================
# ACESSO / PORTARIA
# =============================
def registrar_acesso():
    print("\n=== VERIFICAÇÃO DE ACESSO (BIOMETRIA/CÓDIGO) ===")
    bio = input("Passe o dedo no leitor (digite o código biométrico ou matrícula): ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT nome, matricula, biometria_hash, vencimento
        FROM alunos
        WHERE biometria_hash = ? OR matricula = ?;
        """,
        (bio, bio),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("Biometria ou matrícula não reconhecida! ACESSO NEGADO.")
        registrar_log("DESCONHECIDO", "NEGADO", "Aluno não encontrado")
        return

    nome, matricula, bio_hash, vencimento_str = row
    status = calcular_status(vencimento_str)

    if status == "ATRASADO":
        print(f"🚫 Pagamento atrasado! Aluno {nome} não pode entrar.")
        print(f"Vencimento em: {vencimento_str}")
        registrar_log(matricula, "NEGADO", "Pagamento em atraso")
    elif status == "VENCE_HOJE":
        print(f"⚠️ Mensalidade de {nome} VENCE HOJE ({vencimento_str}).")
        print("Entrada autorizada, mas avisar o aluno para pagar hoje.")
        registrar_log(matricula, "AUTORIZADO", "Vence hoje")
    else:
        print(f"✅ Entrada autorizada! Bem-vindo, {nome}.")
        registrar_log(matricula, "AUTORIZADO", "Pagamento em dia")


def ver_historico():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT matricula, data_hora, autorizado, motivo FROM acessos ORDER BY id DESC LIMIT 50;"
    )
    logs = cursor.fetchall()
    conn.close()

    print("\n=== HISTÓRICO DE ACESSOS (últimos 50) ===")
    if not logs:
        print("Nenhum acesso registrado.")
        return

    for m, data_hora, autorizado, motivo in logs:
        motivo_txt = f" | Motivo: {motivo}" if motivo else ""
        print(f"[{data_hora}] Mat: {m} → {autorizado}{motivo_txt}")


# =============================
# MENU PRINCIPAL
# =============================
def menu():
    iniciar_banco()
    print("Sistema de portaria da Academia Sunset inicializado.")
    mostrar_alertas()

    while True:
        print("\n===== PORTARIA SUNSET ACADEMY =====")
        print("1 - Cadastrar aluno")
        print("2 - Listar alunos")
        print("3 - Registrar acesso (biometria/código)")
        print("4 - Ver histórico de acessos")
        print("5 - Registrar pagamento (avançar 1 mês)")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar_aluno()
        elif opcao == "2":
            listar_alunos()
        elif opcao == "3":
            registrar_acesso()
        elif opcao == "4":
            ver_historico()
        elif opcao == "5":
            registrar_pagamento()
        elif opcao == "0":
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    menu()
