import tkinter as tk

from preview.skin_preview_3d import SkinPreview


class PreviewDialog(tk.Toplevel):

    def __init__(self, parent, img):
        super().__init__(parent)

        self.title("3D Preview")
        self.geometry("420x520")

        # Panda3D用フレーム
        self.frame = tk.Frame(self, bg="black")
        self.frame.pack(fill="both", expand=True)

        self.update()

        # Panda3D起動
        self.renderer = SkinPreview(self.frame, img)

        # Panda3D更新ループ
        self.after(16, self.update_loop)

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.show_second_layer = tk.BooleanVar(value=True)

        check = tk.Checkbutton(
            self,
            text="Second Layer",
            variable=self.show_second_layer,
            command=self.toggle_second_layer,
        )
        check.pack(anchor="w", padx=10, pady=5)

    def toggle_second_layer(self):

        if not self.renderer:
            return

        if self.show_second_layer.get():
            self.renderer.show_second_layer()
        else:
            self.renderer.hide_second_layer()

    def update_skin(self, img):

        if self.renderer:
            self.renderer.update_texture(img)

    def update_loop(self):
        self.renderer.taskMgr.step()
        self.after(16, self.update_loop)

    def close(self):

        if self.renderer:
            self.renderer.destroy()

        self.destroy()
