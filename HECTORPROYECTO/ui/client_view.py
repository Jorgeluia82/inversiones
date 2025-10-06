from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from services.portfolio import PortfolioService
from data import repositorios as repo
from ui.dialogs import AmountDialog, BuyDialog, SellDialog, UpdatePriceDialog
from ui.widgets import CollapsibleFrame, SortableTreeview, ToolTip
from utils.format import money
from utils.validation import is_valid_date
from utils.exports import export_history_csv
from tkinter import messagebox, filedialog

class ClientView(ttk.Frame):
    def __init__(self, master, app, client_id: int):
        super().__init__(master, padding=8)
        self.app = app
        self.conn = app.conn
        self.client_id = client_id
        self.svc = PortfolioService(self.conn)
        self._build()

    # ---------- UI ----------
    def _build(self):
        self.columnconfigure(0, weight=1)
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        self.lbl_title = ttk.Label(header, text="", font=("Segoe UI", 18, "bold"))
        self.lbl_title.pack(side="left")
        ttk.Button(header, text="← Volver", command=self.app.show_home, bootstyle="secondary").pack(side="right")

        capbar = ttk.Frame(self)
        capbar.grid(row=1, column=0, sticky="ew", padx=12)
        self.lbl_capital = ttk.Label(capbar, text="", font=("Segoe UI", 16, "bold"))
        self.lbl_capital.pack(side="left")
        btns = ttk.Frame(capbar)
        btns.pack(side="right")
        bdep = ttk.Button(btns, text="Ingresar capital", command=self.on_deposit, bootstyle="success")
        bdep.pack(side="left", padx=6)
        ToolTip(bdep, "Registrar depósito en efectivo")
        bwd = ttk.Button(btns, text="Retirar capital", command=self.on_withdraw, bootstyle="warning")
        bwd.pack(side="left")
        ToolTip(bwd, "Registrar retiro en efectivo")

        # Portafolio
        ttk.Label(self, text="Portafolio actual", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", padx=12, pady=(10,4))
        table_frame = ttk.Frame(self)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=12)
        self.rowconfigure(3, weight=1)

        cols = ("company","shares","avg_price","current_price","current_value","pnl")
        self.tv = SortableTreeview(table_frame, columns=cols, show="headings", height=10, bootstyle="info")
        for c, txt in zip(cols, ["Empresa","Acciones","Precio Prom.","Precio Actual","Valor Actual","P&L"]):
            self.tv.heading(c, text=txt)
            self.tv.column(c, width=140 if c=="company" else 110, anchor="center")
        self.tv.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, command=self.tv.yview, bootstyle="round")
        self.tv.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        action_bar = ttk.Frame(self)
        action_bar.grid(row=4, column=0, sticky="ew", padx=12, pady=6)
        ttk.Button(action_bar, text="Ingresar inversión", command=self.on_buy_new, bootstyle="primary").pack(side="left")
        self.btn_buy_more = ttk.Button(action_bar, text="Añadir más (BUY)", command=self.on_buy_more, bootstyle="primary", state="disabled")
        self.btn_buy_more.pack(side="left", padx=6)
        self.btn_sell = ttk.Button(action_bar, text="Retirar (SELL)", command=self.on_sell, bootstyle="danger", state="disabled")
        self.btn_sell.pack(side="left")
        self.btn_update = ttk.Button(action_bar, text="Actualizar precio", command=self.on_update_price, bootstyle="info", state="disabled")
        self.btn_update.pack(side="left", padx=6)

        self.tv.bind("<<TreeviewSelect>>", self.on_select_row)

        # Historial colapsable
        self.hist = CollapsibleFrame(self, title="Ver historial")
        self.hist.grid(row=5, column=0, sticky="nsew", padx=12, pady=(8,12))
        self.rowconfigure(5, weight=1)
        filt = ttk.Frame(self.hist.body)
        filt.pack(fill="x", pady=(4,6))
        ttk.Label(filt, text="Día (YYYY-MM-DD):").pack(side="left")
        self.e_day = ttk.Entry(filt, width=12)
        self.e_day.pack(side="left", padx=(4,10))
        ttk.Button(filt, text="Aplicar", command=self.apply_day, bootstyle="secondary").pack(side="left")
        ttk.Label(filt, text="Rango: Desde").pack(side="left", padx=(16,0))
        self.e_from = ttk.Entry(filt, width=12)
        self.e_from.pack(side="left", padx=4)
        ttk.Label(filt, text="Hasta").pack(side="left")
        self.e_to = ttk.Entry(filt, width=12)
        self.e_to.pack(side="left", padx=4)
        ttk.Button(filt, text="Aplicar", command=self.apply_range, bootstyle="secondary").pack(side="left", padx=(4,0))
        ttk.Button(filt, text="Limpiar filtros", command=self.clear_filters, bootstyle="warning").pack(side="left", padx=(10,0))
        ttk.Button(filt, text="Exportar CSV", command=self.export_csv, bootstyle="success").pack(side="right")

        hcols = ("fecha","tipo_general","empresa","detalle","monto","shares","price")
        self.tvh = SortableTreeview(self.hist.body, columns=hcols, show="headings", height=10, bootstyle="secondary")
        headers = ["Fecha/Hora","Tipo","Empresa","Detalle","Δ Capital","Shares","Precio"]
        for c, t in zip(hcols, headers):
            self.tvh.heading(c, text=t)
            w = 150 if c in ("fecha","detalle") else 110
            if c == "detalle": w = 380
            if c == "empresa": w = 160
            self.tvh.column(c, width=w, anchor="center")
        self.tvh.pack(fill="both", expand=True)

        self.refresh_all()

    # ---------- Helpers ----------
    def current_client(self):
        return repo.get_client(self.conn, self.client_id)

    def refresh_all(self):
        cli = self.current_client()
        if not cli:
            messagebox.showerror("Error", "Cliente no encontrado")
            self.app.show_home()
            return
        self.lbl_title.configure(text=cli["name"])
        self.lbl_capital.configure(text=f"Capital: {money(cli['capital_available'])}")
        # Portafolio
        for i in self.tv.get_children():
            self.tv.delete(i)
        portfolio = self.svc.get_client_portfolio(self.client_id)
        for row in portfolio:
            self.tv.insert("", "end", iid=str(row["investment_id"]),
                           values=(row["company"],
                                   f"{row['shares']:.4f}",
                                   money(row["avg_price"]),
                                   money(row["current_price"]),
                                   money(row["current_value"]),
                                   money(row["pnl"])))
        # Historial (sin filtros)
        self.load_history(None, None)

        # Disable action buttons until selection
        for b in (self.btn_buy_more, self.btn_sell, self.btn_update):
            b.configure(state="disabled")

    def on_select_row(self, _e=None):
        sel = self.get_selected_investment_id()
        state = "normal" if sel else "disabled"
        self.btn_buy_more.configure(state=state)
        self.btn_sell.configure(state=state)
        self.btn_update.configure(state=state)

    def get_selected_investment_id(self) -> int | None:
        sel = self.tv.selection()
        if sel:
            try:
                return int(sel[0])
            except Exception:
                return None
        return None

    # ---------- Actions ----------
    def on_deposit(self):
        dlg = AmountDialog(self, title="Ingresar capital", label="Monto a depositar")
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.svc.deposit(self.client_id, dlg.result["amount"], dlg.result["note"])
                messagebox.showinfo("Listo", "Depósito registrado")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_withdraw(self):
        dlg = AmountDialog(self, title="Retirar capital", label="Monto a retirar")
        self.wait_window(dlg)
        if dlg.result:
            if not messagebox.askyesno("Confirmar", "¿Confirmar retiro de capital?"):
                return
            try:
                self.svc.withdraw(self.client_id, dlg.result["amount"], dlg.result["note"])
                messagebox.showinfo("Listo", "Retiro registrado")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_buy_new(self):
        dlg = BuyDialog(self, "Ingresar inversión")
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.svc.buy(self.client_id, dlg.result["company"], dlg.result["amount"], dlg.result["price"], dlg.result["note"])
                messagebox.showinfo("Listo", "Compra registrada")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_buy_more(self):
        inv_id = self.get_selected_investment_id()
        if not inv_id: return
        dlg = AmountDialog(self, title="Añadir más (BUY)", label="Monto a invertir")
        self.wait_window(dlg)
        if dlg.result:
            d2 = AmountDialog(self, title="Precio por acción", label="Precio por acción")
            self.wait_window(d2)
            if not d2.result:
                return
            price = d2.result["amount"]
            note = dlg.result["note"] or d2.result["note"]
            inv = repo.get_investment(self.conn, inv_id)
            try:
                self.svc.buy(inv["client_id"], inv["company"], dlg.result["amount"], price, note)
                messagebox.showinfo("Listo", "Compra adicional registrada")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_sell(self):
        inv_id = self.get_selected_investment_id()
        if not inv_id: return
        inv = repo.get_investment(self.conn, inv_id)
        dlg = SellDialog(self, default_shares=f"{inv['shares']:.4f}")
        self.wait_window(dlg)
        if dlg.result:
            if not messagebox.askyesno("Confirmar", "¿Confirmar venta (SELL)?"):
                return
            try:
                self.svc.sell(inv_id, dlg.result["shares"], dlg.result["price"], dlg.result["note"])
                messagebox.showinfo("Listo", "Venta registrada")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_update_price(self):
        inv_id = self.get_selected_investment_id()
        if not inv_id: return
        dlg = UpdatePriceDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.svc.update_price(inv_id, dlg.result["price"], dlg.result["note"])
                messagebox.showinfo("Listo", "Precio actualizado")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Historial ----------
    def load_history(self, day: str | None, rng: tuple[str, str] | None):
        for i in self.tvh.get_children():
            self.tvh.delete(i)
        day_arg = day
        date_from = date_to = None
        if rng:
            date_from, date_to = rng
        data = self.svc.get_client_history(self.client_id, day=day_arg, date_from=date_from, date_to=date_to)
        self._last_history_cache = data  # para exportar
        for row in data:
            self.tvh.insert("", "end", values=(
                row["fecha"], row["tipo_general"], row["empresa"], row["detalle"],
                f"{row['monto_cambio_capital']:.2f}" if row["monto_cambio_capital"] != "" else "",
                f"{row['shares']:.4f}" if isinstance(row["shares"], (float, int)) and row["shares"] != "" else row["shares"],
                f"{row['price']:.2f}" if isinstance(row["price"], (float, int)) else "",
            ))

    def apply_day(self):
        day = self.e_day.get().strip()
        if not is_valid_date(day):
            messagebox.showwarning("Validación", "Día inválido. Formato YYYY-MM-DD")
            return
        self.e_from.delete(0, 'end')
        self.e_to.delete(0, 'end')
        self.load_history(day, None)

    def apply_range(self):
        d1 = self.e_from.get().strip()
        d2 = self.e_to.get().strip()
        if not (is_valid_date(d1) and is_valid_date(d2)):
            messagebox.showwarning("Validación", "Rango inválido. Use YYYY-MM-DD")
            return
        self.e_day.delete(0, 'end')
        self.load_history(None, (d1, d2))

    def clear_filters(self):
        self.e_day.delete(0, 'end')
        self.e_from.delete(0, 'end')
        self.e_to.delete(0, 'end')
        self.load_history(None, None)

    def export_csv(self):
        if not getattr(self, "_last_history_cache", None):
            messagebox.showinfo("Exportar", "No hay datos de historial para exportar")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Guardar historial")
        if not path:
            return
        try:
            export_history_csv(path, self._last_history_cache)
            messagebox.showinfo("Éxito", f"Historial exportado a:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
