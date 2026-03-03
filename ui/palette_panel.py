import tkinter as tk


class PaletteIOPanel(tk.Frame):
    def __init__(self, parent, user_palette):
        super().__init__(parent)
        self.user_palette = user_palette
        self._build()

    def _build(self):
        tk.Button(
            self,
            text="登録",
            command=self.user_palette.register_current_color,
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            self,
            text="削除",
            command=self.user_palette.clear_selected,
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            self,
            text="パレット保存",
            command=self.user_palette.save,
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            self,
            text="パレット読込",
            command=self.user_palette.load,
        ).pack(side="left", expand=True, fill="x", padx=2)
