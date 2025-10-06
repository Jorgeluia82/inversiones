from ttkbootstrap import ttk
import tkinter as tk
from tkinter import messagebox
from utils.validation import parse_float_or_none, validate_date_str

class BaseModal(tk.Toplevel):
    def __init__(self, master, title=""):
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.result = None
        self.destroy()

class CreateClientDialog(BaseModal):
    def __init__(self, master):
        super().__init__(master, "Crear cliente")
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Nombre *").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(frm, width=36)
        self.e_name.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(frm, text="Email").grid(row=1, column=0, sticky="w")
        self.e_email = ttk.Entry(frm, width=36)
        self.e_email.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(frm, text="Teléfono").grid(row=2, column=0, sticky="w")
        self.e_phone = ttk.Entry(frm, width=36)
        self.e_phone.grid(row=2, column=1, sticky="ew", pady=4)
        ttk.Label(frm, text="Capital inicial").grid(row=3, column=0, sticky="w")
        self.e_capital = ttk.Entry(frm, width=20)
        self.e_capital.insert(0, "0")
        self.e_capital.grid(row=3, column=1, sticky="w", pady=4)
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancelar", command=self.on_close, bootstyle="secondary").pack(side="right", padx=6)
        ttk.Button(btns, text="Crear", command=self.on_submit, bootstyle="primary").pack(side="right")
        self.bind("<Return>", lambda _e: self.on_submit())

    def on_submit(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return
        capital = parse_float_or_none(self.e_capital.get())
        if capital is None or capital < 0:
            messagebox.showwarning("Validación", "Capital inválido")
            return
        self.result = {
            "name": name,
            "email": self.e_email.get().strip() or None,
            "phone": self.e_phone.get().strip() or None,
            "capital": float(capital),
        }
        self.destroy()

class AmountDialog(BaseModal):
    def __init__(self, master, title="Monto", label="Monto", default=""):
        super().__init__(master, title)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=label).grid(row=0, column=0, sticky="w")
        self.e_amount = ttk.Entry(frm, width=20)
        self.e_amount.insert(0, default)
        self.e_amount.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Nota (opcional)").grid(row=1, column=0, sticky="w")
        self.e_note = ttk.Entry(frm, width=36)
        self.e_note.grid(row=1, column=1, sticky="w", pady=4)
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancelar", command=self.on_close, bootstyle="secondary").pack(side="right", padx=6)
        ttk.Button(btns, text="Aceptar", command=self.on_ok, bootstyle="success").pack(side="right")
        self.bind("<Return>", lambda _e: self.on_ok())

    def on_ok(self):
        val = parse_float_or_none(self.e_amount.get())
        if val is None or val <= 0:
            from tkinter import messagebox
            messagebox.showwarning("Validación", "Monto inválido")
            return
        self.result = {"amount": float(val), "note": self.e_note.get().strip() or None}
        self.destroy()

class BuyDialog(BaseModal):
    def __init__(self, master, title="Ingresar inversión"):
        super().__init__(master, title)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Empresa *").grid(row=0, column=0, sticky="w")
        self.e_company = ttk.Entry(frm, width=26)
        self.e_company.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Monto a invertir *").grid(row=1, column=0, sticky="w")
        self.e_amount = ttk.Entry(frm, width=20)
        self.e_amount.grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Precio por acción *").grid(row=2, column=0, sticky="w")
        self.e_price = ttk.Entry(frm, width=20)
        self.e_price.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Nota").grid(row=3, column=0, sticky="w")
        self.e_note = ttk.Entry(frm, width=30)
        self.e_note.grid(row=3, column=1, sticky="w", pady=4)
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancelar", command=self.on_close, bootstyle="secondary").pack(side="right", padx=6)
        ttk.Button(btns, text="Comprar", command=self.on_ok, bootstyle="primary").pack(side="right")
        self.bind("<Return>", lambda _e: self.on_ok())

    def on_ok(self):
        from utils.validation import parse_float_or_none
        company = self.e_company.get().strip()
        amount = parse_float_or_none(self.e_amount.get())
        price = parse_float_or_none(self.e_price.get())
        if not company:
            messagebox.showwarning("Validación", "Empresa es obligatoria")
            return
        if amount is None or amount <= 0 or price is None or price <= 0:
            messagebox.showwarning("Validación", "Monto/Precio inválidos")
            return
        self.result = {"company": company, "amount": float(amount), "price": float(price), "note": self.e_note.get().strip() or None}
        self.destroy()

class SellDialog(BaseModal):
    def __init__(self, master, title="Vender inversión", default_shares=""):
        super().__init__(master, title)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Acciones a vender *").grid(row=0, column=0, sticky="w")
        self.e_shares = ttk.Entry(frm, width=20)
        self.e_shares.insert(0, default_shares)
        self.e_shares.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Precio por acción *").grid(row=1, column=0, sticky="w")
        self.e_price = ttk.Entry(frm, width=20)
        self.e_price.grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Nota").grid(row=2, column=0, sticky="w")
        self.e_note = ttk.Entry(frm, width=30)
        self.e_note.grid(row=2, column=1, sticky="w", pady=4)
        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancelar", command=self.on_close, bootstyle="secondary").pack(side="right", padx=6)
        ttk.Button(btns, text="Vender", command=self.on_ok, bootstyle="danger").pack(side="right")
        self.bind("<Return>", lambda _e: self.on_ok())

    def on_ok(self):
        from utils.validation import parse_float_or_none
        shares = parse_float_or_none(self.e_shares.get())
        price = parse_float_or_none(self.e_price.get())
        if shares is None or shares <= 0 or price is None or price <= 0:
            messagebox.showwarning("Validación", "Acciones/Precio inválidos")
            return
        self.result = {"shares": float(shares), "price": float(price), "note": self.e_note.get().strip() or None}
        self.destroy()

class UpdatePriceDialog(BaseModal):
    def __init__(self, master, title="Actualizar precio"):
        super().__init__(master, title)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Nuevo precio *").grid(row=0, column=0, sticky="w")
        self.e_price = ttk.Entry(frm, width=20)
        self.e_price.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text="Nota").grid(row=1, column=0, sticky="w")
        self.e_note = ttk.Entry(frm, width=30)
        self.e_note.grid(row=1, column=1, sticky="w", pady=4)
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancelar", command=self.on_close, bootstyle="secondary").pack(side="right", padx=6)
        ttk.Button(btns, text="Actualizar", command=self.on_ok, bootstyle="info").pack(side="right")
        self.bind("<Return>", lambda _e: self.on_ok())

    def on_ok(self):
        from utils.validation import parse_float_or_none
        price = parse_float_or_none(self.e_price.get())
        if price is None or price <= 0:
            messagebox.showwarning("Validación", "Precio inválido")
            return
        self.result = {"price": float(price), "note": self.e_note.get().strip() or None}
        self.destroy()
