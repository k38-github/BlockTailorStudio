import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class RGBBars(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.RGB_BAR_WIDTH = 256
        self.RGB_BAR_HEIGHT = 14

        # 色状態
        self.controller = controller
        self.controller.add_observer(self.set_rgba)

        self.bar_images = {}
        self.current_rgb = (0, 0, 0)

        self.r_bar = None
        self.g_bar = None
        self.b_bar = None

        self.r_value_label = None
        self.g_value_label = None
        self.b_value_label = None

        self.r_bar, self.r_value_label = self.create_rgb_row("r")
        self.g_bar, self.g_value_label = self.create_rgb_row("g")
        self.b_bar, self.b_value_label = self.create_rgb_row("b")

        self.set_rgba((0, 0, 0, 255))

    # -----------------------------
    # UI作成
    # -----------------------------

    def create_rgb_row(self, channel):
        row = tk.Frame(self)
        row.pack(fill="x", pady=4)

        label = tk.Label(row, text=channel.upper(), width=1, font=("Arial", 9))
        label.pack(side="left", padx=(0, 10))

        bar = self.create_rgb_bar(row, channel)
        bar.pack(side="left", fill="x", expand=True)

        value_label = tk.Label(
            row,
            text="0",
            width=3,
            anchor="e",
            font=("Arial", 9),
        )
        value_label.pack(side="right")

        return bar, value_label

    def create_rgb_bar(self, parent, channel):

        # すでに作ってたら再利用
        if channel in self.bar_images:
            photo = self.bar_images[channel]
        else:
            # --- 画像生成 ---
            w, h = self.RGB_BAR_WIDTH, self.RGB_BAR_HEIGHT
            img = Image.new("RGBA", (w, h))

            pixels = img.load()

            for x in range(w):
                value = x
                for y in range(h):
                    if channel == "r":
                        pixels[x, y] = (value, 0, 0, 255)
                    elif channel == "g":
                        pixels[x, y] = (0, value, 0, 255)
                    else:
                        pixels[x, y] = (0, 0, value, 255)

            # --- マスク ---
            mask = Image.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask)

            radius = 4
            mask_draw.rounded_rectangle([1, 1, w - 2, h - 2], radius=radius, fill=255)

            img.putalpha(mask)

            # --- 枠 ---
            draw = ImageDraw.Draw(img)

            draw.rounded_rectangle(
                [1, 1, w - 2, h - 2],
                radius=radius,
                outline=(70, 130, 182, 180),
            )

            draw.rounded_rectangle(
                [2, 2, w - 3, h - 3],
                radius=radius - 1,
                outline=(255, 255, 255, 255),
            )

            photo = ImageTk.PhotoImage(img)

            # キャッシュ保存
            self.bar_images[channel] = photo

        # --- Canvasは毎回作る ---
        canvas = tk.Canvas(
            parent,
            width=self.RGB_BAR_WIDTH,
            height=self.RGB_BAR_HEIGHT + 6,
            highlightthickness=0,
            bd=0,
            bg=parent.cget("bg"),
        )

        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo

        canvas.channel = channel

        canvas.bind("<Button-1>", self.on_click)
        canvas.bind("<B1-Motion>", self.on_click)

        return canvas

    # -----------------------------
    # 操作処理
    # -----------------------------
    def on_click(self, event):
        canvas = event.widget
        channel = canvas.channel

        value = int(event.x / (self.RGB_BAR_WIDTH - 1) * 255)
        value = max(0, min(255, value))

        # 現在色取得
        r, g, b = self.get_rgb()

        if channel == "r":
            r = value
        elif channel == "g":
            g = value
        elif channel == "b":
            b = value

        self.set_rgba((r, g, b, 255))
        self.controller.set_color((r, g, b, 255))

    def get_rgb(self):
        r = int(self.r_value_label.cget("text"))
        g = int(self.g_value_label.cget("text"))
        b = int(self.b_value_label.cget("text"))
        return r, g, b

    # -----------------------------
    # カーソル描画
    # -----------------------------
    def draw_cursor(self, canvas, value):
        canvas.delete("cursor")

        h = self.RGB_BAR_HEIGHT
        size = 4
        w = self.RGB_BAR_WIDTH

        x = int(value / 255 * (w - 1))
        x = max(size, min(w - size, x))

        canvas.create_polygon(
            x,
            h,
            x - size,
            h + size,
            x + size,
            h + size,
            fill="white",
            outline="#4682B4",
            width=1,
            tags="cursor",
        )

    # -----------------------------
    # 外部からRGBAをセット
    # -----------------------------
    def set_rgba(self, rgba):
        r, g, b, a = rgba

        self.current_rgb = (r, g, b)

        self.draw_cursor(self.r_bar, r)
        self.draw_cursor(self.g_bar, g)
        self.draw_cursor(self.b_bar, b)

        self.r_value_label.config(text=str(r))
        self.g_value_label.config(text=str(g))
        self.b_value_label.config(text=str(b))
