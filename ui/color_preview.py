import tkinter as tk

from PIL import ImageTk, Image, ImageDraw


class ColorPreview(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller
        self.controller.add_observer(self.on_color_changed)

        self.SIZE = 25
        self.RADIUS = 4
        self.SCALE = 3

        self.canvas = tk.Canvas(
            self,
            width=self.SIZE,
            height=self.SIZE,
            bd=0,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.color_code_label = tk.Label(self, font=("Consolas", 7))
        self.color_code_label.pack()

        self.preview_image = None
        self.image_id = self.canvas.create_image(
            self.SIZE // 2, self.SIZE // 2, anchor="center"
        )

        self.on_color_changed(self.controller.get_color())

    # ==========================
    # 色変更通知
    # ==========================
    def on_color_changed(self, rgba):
        r, g, b, a = rgba
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        if a == 0:
            img = self.create_transparent_preview()
            self.color_code_label.configure(text="#######")
        else:
            img = self.create_color_preview((r, g, b))
            self.color_code_label.configure(text=hex_color)

        self.preview_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.preview_image)

    # ==========================
    # 通常カラー
    # ==========================
    def create_color_preview(self, rgb):
        size = self.SIZE * self.SCALE
        radius = self.RADIUS * self.SCALE

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = self.SCALE

        draw.rounded_rectangle(
            (margin, margin, size - margin - 1, size - margin - 1),
            radius=radius - margin,
            fill=rgb + (255,),
            outline=(70, 130, 182, 180),
            width=self.SCALE,
        )

        # 縮小してアンチエイリアス
        img = img.resize((self.SIZE, self.SIZE), Image.Resampling.LANCZOS)

        return img

    # ==========================
    # 透明表示
    # ==========================
    def create_transparent_preview(self):
        size = self.SIZE * self.SCALE
        radius = self.RADIUS * self.SCALE
        margin = self.SCALE

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        checker = 8 * self.SCALE

        for y in range(0, size, checker):
            for x in range(0, size, checker):
                c = (
                    (200, 200, 200, 255)
                    if (x // checker + y // checker) % 2 == 0
                    else (235, 235, 235, 255)
                )
                draw.rectangle((x, y, x + checker, y + checker), fill=c)

        draw.rounded_rectangle(
            (margin, margin, size - margin - 1, size - margin - 1),
            radius=radius - margin,
            outline=(70, 130, 182, 180),
            width=self.SCALE,
        )

        img = img.resize((self.SIZE, self.SIZE), Image.Resampling.LANCZOS)

        return img
