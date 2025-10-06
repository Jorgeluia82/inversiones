import sys
try:
    import ttkbootstrap as tb
    from ttkbootstrap import ttk
except ModuleNotFoundError:
    print("Falta ttkbootstrap. Instálalo con: pip install ttkbootstrap", file=sys.stderr)
    raise

from data.db import get_connection, ensure_schema_and_seed
from ui.home_view import HomeView
from ui.client_view import ClientView


class App(tb.Window):
    def __init__(self):
        # Tema inicial
        super().__init__(themename="cosmo")
        self.title("Base de datos para inversiones")
        self.geometry("1100x720")
        self.minsize(980, 640)

        # ===== Topbar con botón de tema (arriba a la derecha) =====
        self.theme_cycle = [
            "cosmo", "darkly", "flatly", "cyborg",
            "journal", "litera", "minty", "yeti", "pulse", "sandstone", "united", "morph"
        ]
        self._theme_index = 0  # "cosmo"
        self.topbar = ttk.Frame(self, padding=(8, 6))
        self.topbar.pack(side="top", fill="x")

        # separador visual a la izquierda (opcional: placeholder de título global)
        self._title_lbl = ttk.Label(self.topbar, text="", anchor="w")
        self._title_lbl.pack(side="left", expand=True, fill="x")

        self.btn_theme = ttk.Button(
            self.topbar,
            text=f"Tema: {self.theme_cycle[self._theme_index]}",
            command=self._switch_theme,
            bootstyle="secondary"
        )
        self.btn_theme.pack(side="right")

        # ===== Contenedor de vistas =====
        self.container = ttk.Frame(self, padding=0)
        self.container.pack(fill="both", expand=True)

        # DB
        self.conn = get_connection()
        ensure_schema_and_seed(self.conn)

        # Routing simple
        self.frames = {}
        self.show_home()

    # -------- Tema --------
    def _switch_theme(self):
        self._theme_index = (self._theme_index + 1) % len(self.theme_cycle)
        new_theme = self.theme_cycle[self._theme_index]
        # Cambia el tema en caliente
        self.style.theme_use(new_theme)
        # Refresca texto del botón
        self.btn_theme.configure(text=f"Tema: {new_theme}")

    # -------- Navegación --------
    def clear_frame(self):
        for child in self.container.winfo_children():
            child.destroy()

    def show_home(self):
        self.clear_frame()
        frame = HomeView(self.container, app=self)
        frame.pack(fill="both", expand=True)
        self.frames["home"] = frame
        # (opcional) título global
        self._title_lbl.configure(text="")

    def open_client(self, client_id: int):
        self.clear_frame()
        frame = ClientView(self.container, app=self, client_id=client_id)
        frame.pack(fill="both", expand=True)
        self.frames["client"] = frame
        # (opcional) título global
        self._title_lbl.configure(text="")

if __name__ == "__main__":
    app = App()
    app.mainloop()
