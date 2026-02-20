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
            self.color_code_label.configure(text="透明")
        else:
            img = self.create_color_preview((r, g, b))
            self.color_code_label.configure(text=f"#{r:02X}{g:02X}{b:02X}")

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
            outline=(120, 120, 120, 255),
            width=self.SCALE,
        )

        img = img.resize((self.SIZE, self.SIZE), Image.Resampling.LANCZOS)

        return img

    def update_color_preview(self):
        self.canvas.delete("all")

        r, g, b, a = self.controller.get_color()

        if a == 0:
            # 透明用チェッカーボード
            size = 10
            for y in range(0, 40, size):
                for x in range(0, 40, size):
                    c = "#cccccc" if (x // size + y // size) % 2 == 0 else "#eeeeee"
                    self.canvas.create_rectangle(
                        x, y, x + size, y + size, fill=c, outline=""
                    )
            self.canvas.create_text(20, 20, text="透明", fill="#666", font=("Arial", 8))
            self.color_code_label.configure(text="透明")
        else:
            self.canvas.create_rectangle(
                0, 0, 40, 40, fill=f"#{r:02x}{g:02x}{b:02x}", outline=""
            )
            self.color_code_label.configure(text=f"#{r:02X}{g:02X}{b:02X}")
