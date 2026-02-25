import tkinter as tk
from tkinter import colorchooser


class ColorPalette(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        tk.Button(parent, text="カラーパレット", command=self.choose_color).pack(
            fill="x", pady=5
        )

    def choose_color(self):
        r, g, b, a = self.controller.get_color()

        rgb, _ = colorchooser.askcolor(color=f"#{r:02x}{g:02x}{b:02x}")

        if rgb is None:
            return

        r, g, b = map(int, rgb)
        self.controller.set_color((r, g, b, a))
