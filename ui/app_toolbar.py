import tkinter as tk

from ui.tooltip import ToolTip


class AppToolbar(tk.Frame):
    def __init__(self, parent, on_save, on_load, on_undo, on_redo):
        super().__init__(parent, bd=1, relief="raised")

        self.btn = tk.Button(self, text="💾", command=on_save)
        self.btn.pack(side="left", padx=2)
        ToolTip(self.btn, "保存")

        self.btn = tk.Button(self, text="📂", command=on_load)
        self.btn.pack(side="left", padx=2)
        ToolTip(self.btn, "読込")

        tk.Label(self, text="|").pack(side="left", padx=5)

        self.btn = tk.Button(self, text="↶", command=on_undo)
        self.btn.pack(side="left", padx=2)
        ToolTip(self.btn, "Undo")

        self.btn = tk.Button(self, text="↷", command=on_redo)
        self.btn.pack(side="left", padx=2)
        ToolTip(self.btn, "Redo")
