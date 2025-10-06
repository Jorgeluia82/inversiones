from ttkbootstrap import ttk
import tkinter as tk

class CollapsibleFrame(ttk.Frame):
    def __init__(self, master, title="Sección", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self._expanded = False
        self._header = ttk.Frame(self)
        self._header.grid(row=0, column=0, sticky="ew")
        self._btn = ttk.Button(self._header, text="▶ " + title, command=self.toggle)
        self._btn.pack(side="left", padx=4, pady=4)
        self._body = ttk.Frame(self)
        self._body.grid(row=1, column=0, sticky="nsew")
        self._body.grid_remove()

    def toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            t = self._btn["text"]
            self._btn.configure(text=t.replace("▶", "▼"))
            self._body.grid()
        else:
            t = self._btn["text"]
            self._btn.configure(text=t.replace("▼", "▶"))
            self._body.grid_remove()

    @property
    def body(self):
        return self._body

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tip:
            return
        x, y, *_ = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self.tip, text=self.text, bootstyle="light")
        lbl.pack(ipadx=6, ipady=3)

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class SortableTreeview(ttk.Treeview):
    def heading(self, column, **kwargs):
        if "command" not in kwargs:
            kwargs["command"] = lambda c=column: self._sort_by(c, False)
        super().heading(column, **kwargs)

    def _sort_by(self, col, descending):
        data = [(self.set(k, col), k) for k in self.get_children("")]
        try:
            data.sort(key=lambda t: float(str(t[0]).replace(",", "").replace("$", "")), reverse=descending)
        except Exception:
            data.sort(reverse=descending)
        for index, (_, k) in enumerate(data):
            self.move(k, "", index)
        self.heading(col, command=lambda: self._sort_by(col, not descending))
