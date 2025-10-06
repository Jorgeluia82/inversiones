from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from data import repositorios as repo
from ui.dialogs import CreateClientDialog
from utils.format import money

class HomeView(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=8)
        self.app = app
        self.conn = app.conn
        self.build()

    def build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=12)
        ttk.Label(header, text="Base de datos para inversiones", font=("Segoe UI", 18, "bold")).pack(side="left")

        # Búsqueda
        search = ttk.Frame(self)
        search.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(search, text="Buscar cliente:").pack(side="left")
        self.e_q = ttk.Entry(search, width=30)
        self.e_q.pack(side="left", padx=6)
        ttk.Button(search, text="Buscar", command=self.refresh, bootstyle="primary").pack(side="left")
        ttk.Button(search, text="Limpiar", command=self.clear_search, bootstyle="secondary").pack(side="left", padx=(6,0))

        self.cards = ttk.Frame(self)
        self.cards.pack(fill="both", expand=True, padx=12, pady=8)
        self.cards.columnconfigure((0,1,2,3), weight=1)

        self.refresh()

    def _card(self, parent, title, subtitle, primary_text=None, primary_cmd=None):
        card = ttk.Frame(parent, padding=16, bootstyle="light")
        # Línea superior decorativa
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(0,10))
        ttk.Label(card, text=title, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(card, text=subtitle).pack(anchor="w", pady=(4,10))
        if primary_text and primary_cmd:
            ttk.Button(card, text=primary_text, command=primary_cmd, bootstyle="primary").pack(anchor="e")
        return card

    def clear_search(self):
        self.e_q.delete(0, 'end')
        self.refresh()

    def refresh(self):
        for w in self.cards.winfo_children():
            w.destroy()
        q = self.e_q.get().strip() or None
        clients = repo.list_clients(self.conn, q=q)

        # Card Crear cliente
        cc = self._card(self.cards, "+ Crear cliente", "Registrar nuevo inversionista", "Crear", self.create_client)
        cc.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # Clientes
        col = 1
        row = 0
        for cli in clients:
            subtitle = f"Capital: {money(cli['capital_available'])}"
            card = self._card(self.cards, cli["name"], subtitle, "Entrar", lambda cid=cli["id"]: self.app.open_client(cid))
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_client(self):
        dlg = CreateClientDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            try:
                repo.create_client(self.conn, dlg.result["name"], dlg.result["email"], dlg.result["phone"], dlg.result["capital"])
                from tkinter import messagebox
                messagebox.showinfo("Éxito", "Cliente creado")
                self.refresh()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", str(e))
