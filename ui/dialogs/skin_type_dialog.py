import tkinter as tk
from ui.dialogs.base_dialog import BaseDialog
from core.skin_types import CLASSIC, SLIM


class SkinTypeDialog(BaseDialog):

    def __init__(self, parent):
        self.skin_type = tk.StringVar(value=CLASSIC)
        self.use_character_maker = tk.BooleanVar(value=True)
        super().__init__(parent, "New Skin")

    def build_body(self, master):

        tk.Label(master, text="Skin Type").pack(pady=(0, 5))

        tk.Radiobutton(
            master,
            text="Classic (Steve)",
            variable=self.skin_type,
            value=CLASSIC,
        ).pack(anchor="w")

        tk.Radiobutton(
            master,
            text="Slim (Alex)",
            variable=self.skin_type,
            value=SLIM,
        ).pack(anchor="w")

        tk.Checkbutton(
            master, text="キャラメイクを行う", variable=self.use_character_maker
        ).pack(anchor="w", pady=(10, 0))

    def get_result(self):
        return {
            "skin_type": self.skin_type.get(),
            "use_character_maker": self.use_character_maker.get(),
        }
