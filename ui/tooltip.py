import tkinter as tk


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None

        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")

    def show(self, event=None):

        if self.tip:
            return

        root = self.widget.winfo_toplevel()

        # root基準座標に変換
        x = self.widget.winfo_rootx() - root.winfo_rootx() + 20
        y = (
            self.widget.winfo_rooty()
            - root.winfo_rooty()
            + self.widget.winfo_height()
            + 5
        )

        self.tip = tk.Label(
            root,
            text=self.text,
            bg="#333333",
            fg="white",
            padx=6,
            pady=3,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
        )

        self.tip.place(x=x, y=y)

    def hide(self, event=None):

        if self.tip:
            self.tip.destroy()
            self.tip = None
