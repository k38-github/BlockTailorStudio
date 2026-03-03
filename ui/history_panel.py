import tkinter as tk


class HistoryPanel(tk.LabelFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, text="📖履歴", padx=5, pady=5)

        undo_btn = tk.Button(self, text="↶ Undo", command=controller.undo)
        undo_btn.pack(side="left", expand=True, fill="x")

        redo_btn = tk.Button(self, text="↷ Redo", command=controller.redo)
        redo_btn.pack(side="left", expand=True, fill="x")
