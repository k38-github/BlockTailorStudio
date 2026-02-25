import tkinter as tk
from PIL import Image, ImageTk


class RGBBars(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.RGB_BAR_WIDTH = 256
        self.RGB_BAR_HEIGHT = 12

        # 色状態
        self.controller = controller
        self.controller.add_observer(self.set_rgba)

        self.current_rgb = (0, 0, 0)

        self.r_scale = None
        self.g_scale = None
        self.b_scale = None

        self.r_bar = None
        self.g_bar = None
        self.b_bar = None

        self.r_value_label = None
        self.g_value_label = None
        self.b_value_label = None

        self.rgb_frame = None

        self.rgb_frame = tk.Frame(parent)
        self.rgb_frame.pack(fill="x", pady=10)

        self.r_bar, self.r_value_label = self.create_rgb_row("r")
        self.g_bar, self.g_value_label = self.create_rgb_row("g")
        self.b_bar, self.b_value_label = self.create_rgb_row("b")

    # -----------------------------
    # UI作成
    # -----------------------------

    def create_rgb_row(self, channel):
        row = tk.Frame(self)
        row.pack(fill="x", pady=4)

        label = tk.Label(row, text=channel.upper(), width=2)
        label.pack(side="left")

        bar = self.create_rgb_bar(row, channel)
        bar.pack(side="left", fill="x", expand=True)

        value_label = tk.Label(row, text="0", width=4, anchor="e")
        value_label.pack(side="right")

        return bar, value_label

    def create_rgb_bar(self, parent, channel):
        canvas = tk.Canvas(
            parent,
            width=self.RGB_BAR_WIDTH,
            height=self.RGB_BAR_HEIGHT,
            highlightthickness=0,
            bd=0,
        )

        # --- グラデーション生成 ---
        img = Image.new("RGB", (self.RGB_BAR_WIDTH, self.RGB_BAR_HEIGHT))
        pixels = img.load()

        for x in range(self.RGB_BAR_WIDTH):
            value = x
            for y in range(self.RGB_BAR_HEIGHT):
                if channel == "r":
                    pixels[x, y] = (value, 0, 0)
                elif channel == "g":
                    pixels[x, y] = (0, value, 0)
                elif channel == "b":
                    pixels[x, y] = (0, 0, value)

        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo  # 参照保持重要

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

        value = max(0, min(255, event.x))

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
        canvas.create_line(
            value, 0, value, self.RGB_BAR_HEIGHT, fill="white", width=2, tags="cursor"
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
