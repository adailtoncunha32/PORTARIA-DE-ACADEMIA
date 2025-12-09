import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import json
import os

ARQUIVO_ALUNOS = "alunos.json"
ARQUIVO_USUARIOS = "usuarios.json"


# ========= FUNÇÕES DE DATA / PAGAMENTO =========

def ultimo_dia_do_mes(ano: int, mes: int) -> int:
    """Retorna o último dia do mês (28-31)."""
    if mes == 12:
        return 31
    primeiro_mes_seguinte = date(ano, mes + 1, 1)
    ultimo_dia = primeiro_mes_seguinte - timedelta(days=1)
    return ultimo_dia.day


def calcular_proximo_vencimento(dia_venc: int, hoje: date | None = None) -> date:
    """Calcula o próximo vencimento a partir do dia escolhido."""
    if hoje is None:
        hoje = date.today()

    ano = hoje.year
    mes = hoje.month

    # se já passou o dia de vencimento, joga para o próximo mês
    if hoje.day > dia_venc:
        mes += 1
        if mes == 13:
            mes = 1
            ano += 1

    dia = min(dia_venc, ultimo_dia_do_mes(ano, mes))
    return date(ano, mes, dia)


def adicionar_um_mes(data: date) -> date:
    """Usado para somar 1 mês quando pagamento é feito antes do vencimento."""
    ano = data.year
    mes = data.month + 1
    if mes == 13:
        mes = 1
        ano += 1
    dia = min(data.day, ultimo_dia_do_mes(ano, mes))
    return date(ano, mes, dia)


def status_pagamento(dia_venc: int, prox: date, hoje: date | None = None) -> str:
    """Retorna 'ok', 'aviso' (próx 3 dias) ou 'atrasado'."""
    if hoje is None:
        hoje = date.today()

    if prox < hoje:
        return "atrasado"

    delta = (prox - hoje).days
    if 0 <= delta <= 3:
        return "aviso"

    return "ok"


# ========= ARQUIVOS JSON =========

def carregar_alunos() -> list[dict]:
    """Lê alunos.json, cria alguns exemplos se não existir."""
    if not os.path.exists(ARQUIVO_ALUNOS):
        hoje = date.today()
        alunos = [
            {
                "id": 1,
                "nome": "João Silva",
                "dia_venc": 5,
                "prox": calcular_proximo_vencimento(5, hoje).isoformat()
            },
            {
                "id": 2,
                "nome": "Maria Santos",
                "dia_venc": 10,
                "prox": calcular_proximo_vencimento(10, hoje).isoformat()
            },
            {
                "id": 3,
                "nome": "Carlos Lima",
                "dia_venc": 20,
                "prox": calcular_proximo_vencimento(20, hoje).isoformat()
            },
            {
                "id": 4,
                "nome": "Patrícia Poeta",
                "dia_venc": 31,
                "prox": calcular_proximo_vencimento(31, hoje).isoformat()
            },
        ]
        salvar_alunos(alunos)
        return alunos

    with open(ARQUIVO_ALUNOS, "r", encoding="utf-8") as f:
        alunos = json.load(f)

    # saneamento: garantir campos e tipos
    hoje = date.today()
    for idx, a in enumerate(alunos):
        a.setdefault("id", idx + 1)
        a["nome"] = a.get("nome", f"Aluno {a['id']}")
        # dia_venc sempre int
        dv = a.get("dia_venc", hoje.day)
        try:
            a["dia_venc"] = int(dv)
        except ValueError:
            a["dia_venc"] = hoje.day

        prox_str = a.get("prox")
        if not prox_str:
            prox = calcular_proximo_vencimento(a["dia_venc"], hoje)
        else:
            try:
                prox = date.fromisoformat(prox_str)
            except Exception:
                prox = calcular_proximo_vencimento(a["dia_venc"], hoje)
        a["prox"] = prox.isoformat()

    salvar_alunos(alunos)
    return alunos


def salvar_alunos(alunos: list[dict]) -> None:
    with open(ARQUIVO_ALUNOS, "w", encoding="utf-8") as f:
        json.dump(alunos, f, ensure_ascii=False, indent=2)


def carregar_usuarios() -> list[dict]:
    """Lê usuarios.json e garante campo 'perfil'."""
    if not os.path.exists(ARQUIVO_USUARIOS):
        usuarios = [
            {"usuario": "admin", "senha": "admin", "perfil": "admin"}
        ]
        salvar_usuarios(usuarios)
        return usuarios

    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    for u in usuarios:
        if "perfil" not in u:
            u["perfil"] = "admin"
    salvar_usuarios(usuarios)
    return usuarios


def salvar_usuarios(usuarios: list[dict]) -> None:
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)


# ========= APLICAÇÃO PRINCIPAL =========

class App(tk.Tk):
    def __init__(self, usuario_logado: str, perfil: str = "recepcao"):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        self.alunos = carregar_alunos()
        self.usuarios = carregar_usuarios()

        self.title("SUNSET_PORTARIA – Sistema de Portaria da Academia Sunset")
        self.geometry("1200x650")
        self.minsize(1000, 600)
        self.configure(bg="#020617")

        self._criar_layout()
        self.mostrar_dashboard()

    # ----- layout geral -----

    def _criar_layout(self):
        # topo
        top = tk.Frame(self, bg="#020617", height=50)
        top.pack(side="top", fill="x")

        lbl_titulo = tk.Label(
            top,
            text="SUNSET_PORTARIA – PORTARIA INTELIGENTE",
            bg="#020617",
            fg="#e5e7eb",
            font=("Segoe UI", 16, "bold")
        )
        lbl_titulo.pack(side="left", padx=20, pady=10)

        lbl_user = tk.Label(
            top,
            text=f"Usuário: {self.usuario_logado} ({self.perfil})   |   Hoje: {date.today().strftime('%d/%m/%Y')}",
            bg="#020617",
            fg="#9ca3af",
            font=("Segoe UI", 10)
        )
        lbl_user.pack(side="right", padx=20)

        # menu lateral
        self.menu = tk.Frame(self, bg="#020617", width=200)
        self.menu.pack(side="left", fill="y")

        lbl_menu = tk.Label(
            self.menu,
            text="MENU",
            bg="#020617",
            fg="#facc15",
            font=("Segoe UI", 12, "bold")
        )
        lbl_menu.pack(pady=(20, 10))

        self._btn_menu(
            "Dashboard",
            self.mostrar_dashboard
        )
        self._btn_menu(
            "Alunos",
            self.mostrar_alunos
        )
        self._btn_menu(
            "Check-in",
            self.mostrar_checkin
        )
        self._btn_menu(
            "Alertas",
            self.mostrar_alertas
        )
        self._btn_menu(
            "Pesquisa",
            self.mostrar_pesquisa
        )

        if self.perfil == "admin":
            self._btn_menu("Admin / Usuários", self.mostrar_usuarios_sistema)

        self._btn_menu("Sair", self.destroy, danger=True)

        # área de conteúdo
        self.content = tk.Frame(self, bg="#0f172a")
        self.content.pack(side="right", fill="both", expand=True)

    def _btn_menu(self, texto, comando, danger: bool = False):
        cor = "#ef4444" if danger else "#22c55e"
        btn = tk.Button(
            self.menu,
            text=texto,
            bg=cor,
            fg="#020617",
            activebackground="#16a34a" if not danger else "#b91c1c",
            activeforeground="#f9fafb",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=comando,
            cursor="hand2"
        )
        btn.pack(fill="x", padx=20, pady=4)

    def limpar_conteudo(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ----- DASHBOARD -----

    def mostrar_dashboard(self):
        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        hoje = date.today()
        total = len(self.alunos)
        atrasados = sum(
            1
            for a in self.alunos
            if status_pagamento(a["dia_venc"], date.fromisoformat(a["prox"]), hoje) == "atrasado"
        )
        aviso = sum(
            1
            for a in self.alunos
            if status_pagamento(a["dia_venc"], date.fromisoformat(a["prox"]), hoje) == "aviso"
        )

        self._card_dashboard(frame, "Total de alunos", total, "#0ea5e9")
        self._card_dashboard(frame, "Pagamentos a vencer (3 dias)", aviso, "#facc15")
        self._card_dashboard(frame, "Inadimplentes", atrasados, "#ef4444")

        # legenda
        legenda = tk.Frame(frame, bg="#0f172a")
        legenda.pack(anchor="w", pady=(30, 0))
        tk.Label(legenda, text="Legenda de cores:", bg="#0f172a", fg="#e5e7eb",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(legenda, text="Verde = em dia   ", bg="#0f172a", fg="#22c55e",
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(legenda, text="Amarelo = vence em 3 dias   ", bg="#0f172a", fg="#facc15",
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(legenda, text="Vermelho = atrasado", bg="#0f172a", fg="#ef4444",
                 font=("Segoe UI", 10)).pack(side="left")

    def _card_dashboard(self, parent, titulo, valor, cor_faixa):
        card = tk.Frame(parent, bg="#020617", bd=0, relief="flat")
        card.pack(side="left", padx=10, pady=10, fill="y")

        faixa = tk.Frame(card, bg=cor_faixa, height=4)
        faixa.pack(fill="x", side="top")

        lbl_titulo = tk.Label(
            card,
            text=titulo,
            bg="#020617",
            fg="#9ca3af",
            font=("Segoe UI", 10)
        )
        lbl_titulo.pack(padx=20, pady=(12, 4))

        lbl_valor = tk.Label(
            card,
            text=str(valor),
            bg="#020617",
            fg="#e5e7eb",
            font=("Segoe UI", 20, "bold")
        )
        lbl_valor.pack(padx=20, pady=(0, 12))

    # ----- ALUNOS -----

    def mostrar_alunos(self):
        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = tk.Label(
            frame,
            text="Alunos – Cadastro e Pagamentos",
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Segoe UI", 14, "bold")
        )
        titulo.pack(anchor="w", pady=(0, 10))

        form = tk.Frame(frame, bg="#0f172a")
        form.pack(anchor="w", pady=(0, 10))

        tk.Label(form, text="Nome:", bg="#0f172a", fg="#e5e7eb").grid(row=0, column=0, sticky="e")
        entry_nome = tk.Entry(form, width=40)
        entry_nome.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Dia venc. (1-31):", bg="#0f172a", fg="#e5e7eb").grid(row=0, column=2, sticky="e")
        entry_dia = tk.Entry(form, width=5)
        entry_dia.grid(row=0, column=3, padx=5, pady=2)

        btn_add = tk.Button(
            form,
            text="Adicionar / Atualizar aluno",
            bg="#22c55e",
            fg="#020617",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn_add.grid(row=0, column=4, padx=10)

        btn_del = tk.Button(
            form,
            text="Remover selecionado",
            bg="#ef4444",
            fg="#f9fafb",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn_del.grid(row=0, column=5, padx=10)

        btn_pag = tk.Button(
            form,
            text="Pagamento OK",
            bg="#0ea5e9",
            fg="#020617",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn_pag.grid(row=0, column=6, padx=10)

        # Tabela
        cols = ("id", "nome", "dia_venc", "prox", "status")
        tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            height=18
        )
        tree.pack(fill="both", expand=True, pady=(10, 0))

        for col, txt, w in [
            ("id", "ID", 40),
            ("nome", "Nome", 260),
            ("dia_venc", "Dia venc.", 80),
            ("prox", "Próx. venc.", 100),
            ("status", "Status", 120),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center")

        # cores
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 9))
        tree.tag_configure("ok", foreground="#22c55e")
        tree.tag_configure("aviso", foreground="#facc15")
        tree.tag_configure("atrasado", foreground="#ef4444")

        def preencher():
            tree.delete(*tree.get_children())
            hoje = date.today()
            for a in self.alunos:
                prox = date.fromisoformat(a["prox"])
                st = status_pagamento(a["dia_venc"], prox, hoje)
                tag = st
                st_txt = {
                    "ok": "Em dia",
                    "aviso": "Vence em breve",
                    "atrasado": "Atrasado",
                }[st]
                tree.insert(
                    "",
                    "end",
                    iid=str(a["id"]),
                    values=(a["id"], a["nome"], a["dia_venc"], prox.strftime("%d/%m/%Y"), st_txt),
                    tags=(tag,)
                )

        def on_add():
            nome = entry_nome.get().strip()
            dia_str = entry_dia.get().strip()
            if not nome or not dia_str:
                messagebox.showwarning("Atenção", "Informe nome e dia de vencimento.")
                return
            try:
                dia = int(dia_str)
                if not (1 <= dia <= 31):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Atenção", "Dia de vencimento deve ser número entre 1 e 31.")
                return

            selecionado = tree.selection()
            hoje = date.today()

            if selecionado:
                # update
                iid = int(selecionado[0])
                for a in self.alunos:
                    if a["id"] == iid:
                        a["nome"] = nome
                        a["dia_venc"] = dia
                        a["prox"] = calcular_proximo_vencimento(dia, hoje).isoformat()
                        break
            else:
                novo_id = max([a["id"] for a in self.alunos], default=0) + 1
                prox = calcular_proximo_vencimento(dia, hoje)
                self.alunos.append(
                    {
                        "id": novo_id,
                        "nome": nome,
                        "dia_venc": dia,
                        "prox": prox.isoformat(),
                    }
                )

            salvar_alunos(self.alunos)
            preencher()
            entry_nome.delete(0, tk.END)
            entry_dia.delete(0, tk.END)
            tree.selection_remove(tree.selection())

        def on_del():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showinfo("Info", "Selecione um aluno para remover.")
                return
            iid = int(selecionado[0])
            self.alunos = [a for a in self.alunos if a["id"] != iid]
            salvar_alunos(self.alunos)
            preencher()

        def on_pagamento_ok():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showinfo("Info", "Selecione um aluno para registrar pagamento.")
                return
            iid = int(selecionado[0])
            hoje = date.today()
            for a in self.alunos:
                if a["id"] == iid:
                    # se pagar antes, empurra 1 mês a partir do vencimento atual
                    prox_atual = date.fromisoformat(a["prox"])
                    if hoje <= prox_atual:
                        proximo = adicionar_um_mes(prox_atual)
                    else:
                        proximo = calcular_proximo_vencimento(a["dia_venc"], hoje)
                    a["prox"] = proximo.isoformat()
                    break
            salvar_alunos(self.alunos)
            preencher()

        btn_add.config(command=on_add)
        btn_del.config(command=on_del)
        btn_pag.config(command=on_pagamento_ok)

        preencher()

    # ----- CHECK-IN -----

    def mostrar_checkin(self):
        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Check-in de alunos",
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        cols = ("id", "nome", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        tree.pack(side="left", fill="both", expand=True)

        for col, txt, w in [
            ("id", "ID", 40),
            ("nome", "Nome", 260),
            ("status", "Situação", 140),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center")

        style = ttk.Style()
        tree.tag_configure("ok", foreground="#22c55e")
        tree.tag_configure("aviso", foreground="#facc15")
        tree.tag_configure("atrasado", foreground="#ef4444")

        hoje = date.today()

        def preencher():
            tree.delete(*tree.get_children())
            for a in self.alunos:
                prox = date.fromisoformat(a["prox"])
                st = status_pagamento(a["dia_venc"], prox, hoje)
                txt = {
                    "ok": "Liberado",
                    "aviso": "Liberado (vence em breve)",
                    "atrasado": "Bloqueado (pagamento)",
                }[st]
                tree.insert(
                    "",
                    "end",
                    iid=str(a["id"]),
                    values=(a["id"], a["nome"], txt),
                    tags=(st,)
                )

        preencher()

        painel = tk.Frame(frame, bg="#0f172a")
        painel.pack(side="right", fill="y", padx=(10, 0))

        tk.Label(painel, text="Entradas de hoje (visual)", bg="#0f172a", fg="#e5e7eb",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

        lista_entradas = tk.Listbox(painel, width=40, height=18)
        lista_entradas.pack()

        def registrar_entrada():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Selecione um aluno para registrar entrada.")
                return
            iid = int(sel[0])
            aluno = next((a for a in self.alunos if a["id"] == iid), None)
            if not aluno:
                return
            prox = date.fromisoformat(aluno["prox"])
            st = status_pagamento(aluno["dia_venc"], prox, hoje)
            if st == "atrasado":
                messagebox.showwarning("Atenção", "Aluno com pagamento atrasado. Liberar somente após regularização.")
                return
            lista_entradas.insert(tk.END, f"{aluno['nome']} – {date.today().strftime('%d/%m/%Y')}")

        btn_checkin = tk.Button(
            painel,
            text="Registrar entrada",
            bg="#22c55e",
            fg="#020617",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=registrar_entrada
        )
        btn_checkin.pack(pady=(8, 0))

    # ----- ALERTAS -----

    def mostrar_alertas(self):
        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Alertas de pagamento",
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        cols = ("id", "nome", "dia_venc", "prox", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        tree.pack(fill="both", expand=True)

        for col, txt, w in [
            ("id", "ID", 40),
            ("nome", "Nome", 260),
            ("dia_venc", "Dia venc.", 80),
            ("prox", "Próx. venc.", 100),
            ("status", "Situação", 140),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center")

        tree.tag_configure("aviso", foreground="#facc15")
        tree.tag_configure("atrasado", foreground="#ef4444")

        hoje = date.today()
        for a in self.alunos:
            prox = date.fromisoformat(a["prox"])
            st = status_pagamento(a["dia_venc"], prox, hoje)
            if st == "ok":
                continue
            st_txt = "Vence em breve" if st == "aviso" else "Atrasado"
            tree.insert(
                "",
                "end",
                values=(a["id"], a["nome"], a["dia_venc"], prox.strftime("%d/%m/%Y"), st_txt),
                tags=(st,)
            )

    # ----- PESQUISA -----

    def mostrar_pesquisa(self):
        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Pesquisa de alunos",
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        barra = tk.Frame(frame, bg="#0f172a")
        barra.pack(anchor="w", pady=(0, 10))

        tk.Label(barra, text="Nome ou parte:", bg="#0f172a", fg="#e5e7eb").pack(side="left")
        entry_q = tk.Entry(barra, width=40)
        entry_q.pack(side="left", padx=6)

        btn = tk.Button(
            barra,
            text="Buscar",
            bg="#0ea5e9",
            fg="#020617",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn.pack(side="left", padx=6)

        cols = ("id", "nome", "dia_venc", "prox", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        tree.pack(fill="both", expand=True)

        for col, txt, w in [
            ("id", "ID", 40),
            ("nome", "Nome", 260),
            ("dia_venc", "Dia venc.", 80),
            ("prox", "Próx. venc.", 100),
            ("status", "Situação", 140),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center")

        tree.tag_configure("ok", foreground="#22c55e")
        tree.tag_configure("aviso", foreground="#facc15")
        tree.tag_configure("atrasado", foreground="#ef4444")

        def executar_busca():
            q = entry_q.get().strip().lower()
            tree.delete(*tree.get_children())
            hoje = date.today()
            for a in self.alunos:
                if q and q not in a["nome"].lower():
                    continue
                prox = date.fromisoformat(a["prox"])
                st = status_pagamento(a["dia_venc"], prox, hoje)
                st_txt = {
                    "ok": "Em dia",
                    "aviso": "Vence em breve",
                    "atrasado": "Atrasado",
                }[st]
                tree.insert(
                    "",
                    "end",
                    values=(a["id"], a["nome"], a["dia_venc"], prox.strftime("%d/%m/%Y"), st_txt),
                    tags=(st,)
                )

        btn.config(command=executar_busca)

    # ----- ADMIN / USUÁRIOS -----

    def mostrar_usuarios_sistema(self):
        if self.perfil != "admin":
            messagebox.showwarning("Acesso negado", "Somente admin pode gerenciar usuários.")
            return

        self.limpar_conteudo()
        frame = tk.Frame(self.content, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Admin – Usuários do sistema",
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(frame, bg="#0f172a")
        form.pack(anchor="w", pady=(0, 8))

        tk.Label(form, text="Usuário:", bg="#0f172a", fg="#e5e7eb").grid(row=0, column=0, sticky="e")
        entry_user = tk.Entry(form, width=20)
        entry_user.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Senha:", bg="#0f172a", fg="#e5e7eb").grid(row=0, column=2, sticky="e")
        entry_senha = tk.Entry(form, width=20, show="*")
        entry_senha.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form, text="Perfil:", bg="#0f172a", fg="#e5e7eb").grid(row=0, column=4, sticky="e")
        cb_perfil = ttk.Combobox(form, values=["admin", "recepcao"], width=10, state="readonly")
        cb_perfil.set("recepcao")
        cb_perfil.grid(row=0, column=5, padx=5)

        btn_add = tk.Button(
            form,
            text="Adicionar usuário",
            bg="#22c55e",
            fg="#020617",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn_add.grid(row=0, column=6, padx=8)

        btn_del = tk.Button(
            form,
            text="Remover selecionado",
            bg="#ef4444",
            fg="#f9fafb",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        btn_del.grid(row=0, column=7, padx=8)

        cols = ("usuario", "perfil")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        tree.pack(fill="both", expand=True)

        for col, txt, w in [
            ("usuario", "Usuário", 200),
            ("perfil", "Perfil", 100),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center")

        def preencher():
            tree.delete(*tree.get_children())
            for u in self.usuarios:
                perfil = u.get("perfil", "admin")
                tree.insert("", "end", values=(u["usuario"], perfil))

        def on_add_user():
            usuario = entry_user.get().strip()
            senha = entry_senha.get().strip()
            perfil = cb_perfil.get().strip() or "recepcao"

            if not usuario or not senha:
                messagebox.showwarning("Atenção", "Informe usuário e senha.")
                return

            if any(u["usuario"] == usuario for u in self.usuarios):
                messagebox.showwarning("Atenção", "Já existe um usuário com esse nome.")
                return

            self.usuarios.append(
                {"usuario": usuario, "senha": senha, "perfil": perfil}
            )
            salvar_usuarios(self.usuarios)
            preencher()
            entry_user.delete(0, tk.END)
            entry_senha.delete(0, tk.END)

        def on_del_user():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Selecione um usuário para remover.")
                return
            usuario = tree.item(sel[0])["values"][0]
            if usuario == "admin":
                messagebox.showwarning("Atenção", "O usuário 'admin' não pode ser removido.")
                return
            self.usuarios = [u for u in self.usuarios if u["usuario"] != usuario]
            salvar_usuarios(self.usuarios)
            preencher()

        btn_add.config(command=on_add_user)
        btn_del.config(command=on_del_user)

        preencher()


# ========= PONTO DE ENTRADA PARA TESTE DIRETO =========

if __name__ == "__main__":
    app = App("admin", "admin")
    app.mainloop()
