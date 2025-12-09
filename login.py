import tkinter as tk
from tkinter import messagebox
from datetime import date

# Importa a tela principal e o carregador de usuários
from sunset_gui import App, carregar_usuarios


def abrir_app(usuario: str, perfil: str) -> None:
    """Fecha a tela de login e abre o sistema principal."""
    root.destroy()
    app = App(usuario, perfil)
    app.mainloop()


def validar_login(event=None) -> None:
    """Valida usuário e senha e, se ok, abre o sistema."""
    user = entry_user.get().strip()
    pwd = entry_pwd.get().strip()

    if not user or not pwd:
        messagebox.showwarning("Atenção", "Informe usuário e senha.")
        return

    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["usuario"] == user and u["senha"] == pwd:
            perfil = u.get("perfil", "recepcao")
            abrir_app(user, perfil)
            return

    messagebox.showerror("Erro", "Usuário ou senha inválidos.")


# ========= INTERFACE DE LOGIN =========

root = tk.Tk()
root.title("SUNSET_PORTARIA – Login")
root.geometry("420x260")
root.resizable(False, False)
root.configure(bg="#111827")

# Título
lbl_titulo = tk.Label(
    root,
    text="SUNSET_PORTARIA",
    bg="#111827",
    fg="#e5e7eb",
    font=("Segoe UI", 16, "bold"),
)
lbl_titulo.pack(pady=(15, 5))

lbl_sub = tk.Label(
    root,
    text=f"Portaria inteligente – {date.today().strftime('%d/%m/%Y')}",
    bg="#111827",
    fg="#9ca3af",
    font=("Segoe UI", 9),
)
lbl_sub.pack(pady=(0, 15))

frame_form = tk.Frame(root, bg="#111827")
frame_form.pack(pady=5, padx=20, fill="x")

# Usuário
lbl_user = tk.Label(
    frame_form,
    text="Usuário:",
    bg="#111827",
    fg="#e5e7eb",
    font=("Segoe UI", 10, "bold"),
)
lbl_user.grid(row=0, column=0, sticky="w")
entry_user = tk.Entry(frame_form, width=32)
entry_user.grid(row=0, column=1, pady=4)

# Senha
lbl_pwd = tk.Label(
    frame_form,
    text="Senha:",
    bg="#111827",
    fg="#e5e7eb",
    font=("Segoe UI", 10, "bold"),
)
lbl_pwd.grid(row=1, column=0, sticky="w")
entry_pwd = tk.Entry(frame_form, width=32, show="*")
entry_pwd.grid(row=1, column=1, pady=4)

# Botão ENTRAR
btn_login = tk.Button(
    root,
    text="ENTRAR",
    bg="#22c55e",
    fg="#020617",
    activebackground="#16a34a",
    activeforeground="#f9fafb",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    cursor="hand2",
    command=validar_login,
)
btn_login.pack(pady=20, ipadx=60, ipady=4)

# Enter também faz login
root.bind("<Return>", validar_login)

# Foca no campo usuário
entry_user.focus()

if __name__ == "__main__":
    root.mainloop()
