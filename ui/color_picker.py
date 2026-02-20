import tkinter as tk
import math
import colorsys
from PIL import Image, ImageTk, ImageDraw

from ui.color_preview import ColorPreview
from ui.cursor_factory import create_cursor_image


class ColorPicker(tk.Frame):
    def __init__(self, parent, size, ring_width, controller):
        super().__init__(parent)

        # サイズ設定
        self.WHEEL_SIZE = size
        self.SQUARE_SIZE = size
        self.RING_WIDTH = ring_width
        self.SV_MARGIN = 25  # リングとスクエアの余白
        self.PREVIEW_SPACE = 55
        self.CANVAS_SIZE_X = self.WHEEL_SIZE + self.PREVIEW_SPACE
        self.CANVAS_SIZE_Y = self.WHEEL_SIZE

        # HSV状態
        self.current_hue = 0.0
        self.current_s = 1
        self.current_v = 1

        # 色状態
        self.current_rgb = (0, 0, 0)
        self.controller = controller
        self.controller.add_observer(self.set_rgba)

        # アクティブ操作エリア
        self.active_area = None
        self.internal_update = False

        # ==========================
        # レイアウト構造
        # ==========================
        # Canvas
        self.canvas = tk.Canvas(
            self, width=self.CANVAS_SIZE_X, height=self.CANVAS_SIZE_Y
        )
        self.canvas.pack()

        self.preview = ColorPreview(self.canvas, controller)
        self.canvas.create_window(
            0,
            self.WHEEL_SIZE,
            window=self.preview,
            anchor="sw",
        )

        # ==========================
        # カラーカーソル初期化
        # ==========================
        self.wheel_photo = None
        self.sv_photo = None

        self.cursor_photo = create_cursor_image()
        self.cursor_id = self.canvas.create_image(
            self.CANVAS_SIZE_X // 2,
            self.CANVAS_SIZE_Y // 2,
            image=self.cursor_photo,
            anchor="center",
        )

        self.sv_cursor_photo = create_cursor_image()
        self.sv_cursor_id = self.canvas.create_image(
            0, 0, image=self.sv_cursor_photo, anchor="center"
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def draw_hue_ring(self):
        scale = 3
        size = self.WHEEL_SIZE * scale
        cx = cy = size // 2
        radius = size // 2 - (scale * 2)
        inner_radius = radius - (self.RING_WIDTH * scale)

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        pixels = img.load()

        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                distance = math.sqrt(dx * dx + dy * dy)

                if inner_radius - 1 <= distance <= radius + 1:
                    angle = math.atan2(dy, dx)
                    hue = (angle + math.pi) / (2 * math.pi)

                    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                    pixels[x, y] = (
                        int(r * 255),
                        int(g * 255),
                        int(b * 255),
                        255,
                    )

        draw = ImageDraw.Draw(img)
        out_border_width = scale

        # 外枠
        draw.ellipse(
            (
                out_border_width // 2,
                out_border_width // 2,
                size - out_border_width // 2 - 1,
                size - out_border_width // 2 - 1,
            ),
            outline=(70, 130, 182, 180),
            width=out_border_width,
        )

        inner_border_width = scale

        # --- 内枠 ---
        inner_left = cx - inner_radius
        inner_top = cy - inner_radius
        inner_right = cx + inner_radius
        inner_bottom = cy + inner_radius

        draw.ellipse(
            (
                inner_left,
                inner_top,
                inner_right - 1,
                inner_bottom - 1,
            ),
            outline=(70, 130, 182, 180),
            width=inner_border_width,
        )

        img = img.resize(
            (self.WHEEL_SIZE - 1, self.WHEEL_SIZE - 1), Image.Resampling.LANCZOS
        )

        self.wheel_photo = ImageTk.PhotoImage(img)
        self.canvas.delete("ring")
        self.canvas.create_image(
            self.CANVAS_SIZE_X / 2,
            self.CANVAS_SIZE_Y / 2,
            anchor="center",
            image=self.wheel_photo,
            tags="ring",
        )
        self.draw_hue_cursor()
        self.canvas.tag_raise(self.cursor_id)

    def draw_hue_cursor(self):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2

        outer = self.WHEEL_SIZE / 2 - 1
        inner = outer - self.RING_WIDTH
        cursor_radius = (outer + inner) / 2

        angle = self.current_hue * 2 * math.pi - math.pi

        x = cx + cursor_radius * math.cos(angle)
        y = cy + cursor_radius * math.sin(angle)

        self.canvas.coords(self.cursor_id, x, y)

    def pick_color_from_wheel(self, event):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2
        outer = self.WHEEL_SIZE / 2
        inner = outer - self.RING_WIDTH

        dx = event.x - cx
        dy = event.y - cy
        # distance = (dx * dx + dy * dy) ** 0.5

        # if inner <= distance <= outer:

        # --- 角度だけ取得 ---
        angle = math.atan2(dy, dx)
        self.current_hue = (angle + math.pi) / (2 * math.pi)

        # 🔥 半径は固定（リング中央）
        cursor_radius = (outer + inner) / 2 - 2

        x = cx + cursor_radius * math.cos(angle)
        y = cy + cursor_radius * math.sin(angle)

        self.canvas.coords(self.cursor_id, x, y)
        self.update_controller_color()

        self.draw_sv_square()
        self.draw_hue_cursor()

    def draw_sv_square(self):
        cx = self.CANVAS_SIZE_X / 2 + 1
        cy = self.CANVAS_SIZE_Y / 2 + 1
        radius = self.SQUARE_SIZE // 2

        sv_size = int((radius - self.RING_WIDTH - self.SV_MARGIN) * 2)

        img = Image.new("RGBA", (sv_size, sv_size))
        pixels = img.load()

        for y in range(sv_size):
            for x in range(sv_size):

                s = x / sv_size
                v = 1 - (y / sv_size)

                r, g, b = colorsys.hsv_to_rgb(self.current_hue, s, v)
                pixels[x, y] = (
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    255,
                )

        # 枠を描く
        draw = ImageDraw.Draw(img)

        # ① 半透明外枠（少し太め）
        draw.rectangle(
            (0, 0, sv_size - 1, sv_size - 1),
            outline=(70, 30, 132, 140),
            width=1,  # RGBA
        )

        # ② 内側1px白枠
        draw.rectangle(
            (1, 1, sv_size - 2, sv_size - 2), outline=(255, 255, 255, 255), width=1
        )

        self.sv_photo = ImageTk.PhotoImage(img)
        self.canvas.delete("sv_image")
        self.canvas.create_image(
            cx, cy, anchor="center", image=self.sv_photo, tags="sv_image"
        )

        self.draw_sv_cursor()
        self.canvas.tag_raise(self.sv_cursor_id)

    def draw_sv_cursor(self):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2
        radius = self.SQUARE_SIZE // 2

        sv_size = int((radius - self.RING_WIDTH - self.SV_MARGIN) * 2)

        start_x = cx - sv_size / 2
        start_y = cy - sv_size / 2

        x = start_x + self.current_s * sv_size
        y = start_y + (1 - self.current_v) * sv_size

        # 画像カーソルは中心座標のみ
        self.canvas.coords(self.sv_cursor_id, x, y)

    def pick_color_from_sv(self, event):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2
        radius = self.SQUARE_SIZE // 2
        sv_size = int((radius - self.RING_WIDTH - self.SV_MARGIN) * 2)

        start_x = int(cx - sv_size / 2)
        start_y = int(cy - sv_size / 2)

        x = min(max(event.x, start_x), start_x + sv_size)
        y = min(max(event.y, start_y), start_y + sv_size)

        self.current_s = (x - start_x) / sv_size
        self.current_v = 1 - ((y - start_y) / sv_size)

        self.update_controller_color()

        self.draw_sv_square()
        self.draw_sv_cursor()

    def combined_pick_color(self, event):
        self.pick_color_from_wheel(event)
        self.pick_color_from_sv(event)

    def set_rgba(self, rgba):
        # 🔥 自分が更新したときは何もしない
        if self.internal_update:
            return

        r, g, b, a = rgba

        # 🔥 完全黒はHSVを壊さない
        if r == 0 and g == 0 and b == 0:
            self.current_v = 0
            # hue と saturation は維持
        else:
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

            # 無彩色（S=0）のときは hue を維持
            if s == 0:
                self.current_s = 0
                self.current_v = v
            else:
                self.current_hue = h
                self.current_s = s
                self.current_v = v

        self.draw_hue_cursor()
        self.draw_sv_square()
        self.draw_sv_cursor()

    def update_controller_color(self):
        r, g, b = colorsys.hsv_to_rgb(
            self.current_hue,
            self.current_s,
            self.current_v,
        )
        rgba = (int(r * 255), int(g * 255), int(b * 255), 255)

        self.internal_update = True
        self.controller.set_color(rgba)
        self.internal_update = False

    # ==========================
    # イベント制御
    # ==========================
    def on_press(self, event):
        if self.is_in_wheel(event):
            self.active_area = "wheel"
            self.pick_color_from_wheel(event)
        elif self.is_in_sv(event):
            self.active_area = "sv"
            self.pick_color_from_sv(event)

    def on_drag(self, event):
        if self.active_area == "wheel":
            self.pick_color_from_wheel(event)
        elif self.active_area == "sv":
            self.pick_color_from_sv(event)

    def on_release(self, event):
        self.active_area = None

    # ==========================
    # 判定関数
    # ==========================
    def is_in_wheel(self, event):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2
        outer = self.WHEEL_SIZE / 2
        inner = outer - self.RING_WIDTH

        dx = event.x - cx
        dy = event.y - cy
        distance = (dx * dx + dy * dy) ** 0.5

        return inner <= distance <= outer

    def is_in_sv(self, event):
        cx = self.CANVAS_SIZE_X / 2
        cy = self.CANVAS_SIZE_Y / 2
        radius = self.SQUARE_SIZE // 2
        sv_size = int((radius - self.RING_WIDTH - self.SV_MARGIN) * 2)

        start_x = int(cx - sv_size / 2)
        start_y = int(cy - sv_size / 2)

        return (
            start_x <= event.x <= start_x + sv_size
            and start_y <= event.y <= start_y + sv_size
        )
