import tkinter as tk


class FilePanel(tk.LabelFrame):
    def __init__(self, parent, on_save, on_load):
        super().__init__(parent, text="💾 ファイル", padx=5, pady=5)

        self.pack(fill="x", pady=5)

        tk.Button(self, text="保存", command=on_save).pack(
            side="left", expand=True, fill="x", padx=5, pady=5
        )

        tk.Button(self, text="読込", command=on_load).pack(
            side="left", expand=True, fill="x", padx=5, pady=5
        )
