import tkinter as tk

from ui.tooltip import ToolTip


class AppToolbar(tk.Frame):
    def __init__(self, parent, on_save, on_load, on_undo, on_redo, on_3dview):
        super().__init__(parent, bd=1, relief="raised")

        btn = tk.Button(self, text="💾", command=on_save)
        btn.pack(side="left", padx=2)
        ToolTip(btn, "保存")

        btn = tk.Button(self, text="📂", command=on_load)
        btn.pack(side="left", padx=2)
        ToolTip(btn, "読込")

        tk.Label(self, text="|").pack(side="left", padx=5)

        btn = tk.Button(self, text="↶", command=on_undo)
        btn.pack(side="left", padx=2)
        ToolTip(btn, "Undo")

        btn = tk.Button(self, text="↷", command=on_redo)
        btn.pack(side="left", padx=2)
        ToolTip(btn, "Redo")

        tk.Label(self, text="|").pack(side="left", padx=5)

        btn = tk.Button(self, text="📽️", command=on_3dview)
        btn.pack(side="left", padx=2)
        ToolTip(btn, "3Dビュー")
