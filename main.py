import json
import colorsys
import math

import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox

from PIL import Image, ImageTk
from typing import Optional

# =====================
# 定数
# =====================
SKIN_SIZE = 64
PIXEL_SIZE = 10
MARGIN = 20
CANVAS_SIZE = SKIN_SIZE * PIXEL_SIZE + MARGIN * 2
WHEEL_SIZE = 140
RING_WIDTH = 10

TRANSPARENT = (0, 0, 0, 0)
current_color = (255, 0, 0, 255)  # 赤

current_part = "全体"
edit_second_layer_only = False
last_drawn = None
tool_mode = "draw"  # "draw" or "eyedropper"

USER_PALETTE_SIZE = 12
user_palette = [None] * USER_PALETTE_SIZE
user_palette_buttons = []

current_hue = 0.0  # 0.0〜1.0
current_s = 1.0
current_v = 1.0

wheel_photo = None
sv_photo = None

# =====================
# データ
# =====================
# 第一スキンレイヤーデータ
base_pixels = [[TRANSPARENT for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)]

# 第二スキンレイヤーデータ
overlay_pixels = [[TRANSPARENT for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)]

# ピクセル用idマップ
pixel_items: list[list[Optional[int]]] = [
    [None for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)
]

# =====================
# マイクラ部位定義
# =====================
# =====================
# 第一スキンレイヤー範囲
# =====================
FIRST_LAYER_AREAS = {
    # =====================
    # 頭
    # =====================
    "頭_上": (8, 0, 16, 8),
    "頭_下": (16, 0, 24, 8),
    "頭_右": (0, 8, 8, 16),
    "頭_前": (8, 8, 16, 16),
    "頭_左": (16, 8, 24, 16),
    "頭_後": (24, 8, 32, 16),
    # =====================
    # 体
    # =====================
    "体_上": (20, 16, 28, 20),
    "体_下": (28, 16, 36, 20),
    "体_右": (16, 20, 20, 32),
    "体_前": (20, 20, 28, 32),
    "体_左": (28, 20, 32, 32),
    "体_後": (32, 20, 40, 32),
    # =====================
    # 右腕
    # =====================
    "右腕_上": (44, 16, 48, 20),
    "右腕_下": (48, 16, 52, 20),
    "右腕_右": (40, 20, 44, 32),
    "右腕_前": (44, 20, 48, 32),
    "右腕_左": (48, 20, 52, 32),
    "右腕_後": (52, 20, 56, 32),
    # =====================
    # 右脚
    # =====================
    "右脚_上": (4, 16, 8, 20),
    "右脚_下": (8, 16, 12, 20),
    "右脚_右": (0, 20, 4, 32),
    "右脚_前": (4, 20, 8, 32),
    "右脚_左": (8, 20, 12, 32),
    "右脚_後": (12, 20, 16, 32),
    # =====================
    # 左腕
    # =====================
    "左腕_上": (36, 48, 40, 52),
    "左腕_下": (40, 48, 44, 52),
    "左腕_右": (32, 52, 36, 64),
    "左腕_前": (36, 52, 40, 64),
    "左腕_左": (40, 52, 44, 64),
    "左腕_後": (44, 52, 48, 64),
    # =====================
    # 左脚
    # =====================
    "左脚_上": (20, 48, 24, 52),
    "左脚_下": (24, 48, 28, 52),
    "左脚_右": (16, 52, 20, 64),
    "左脚_前": (20, 52, 24, 64),
    "左脚_左": (24, 52, 28, 64),
    "左脚_後": (28, 52, 32, 64),
}


# =====================
# 第二スキンレイヤー範囲
# =====================
SECOND_LAYER_AREAS = {
    # =====================
    # 頭（帽子）
    # =====================
    "頭(帽子)_上": (40, 0, 48, 8),
    "頭(帽子)_下": (48, 0, 56, 8),
    "頭(帽子)_右": (32, 8, 40, 16),
    "頭(帽子)_前": (40, 8, 48, 16),
    "頭(帽子)_左": (48, 8, 56, 16),
    "頭(帽子)_後": (56, 8, 64, 16),
    # =====================
    # 体（上着）
    # =====================
    "体(上着)_上": (20, 32, 28, 36),
    "体(上着)_下": (28, 32, 36, 36),
    "体(上着)_右": (16, 36, 20, 48),
    "体(上着)_前": (20, 36, 28, 48),
    "体(上着)_左": (28, 36, 32, 48),
    "体(上着)_後": (32, 36, 40, 48),
    # =====================
    # 右腕（袖）
    # =====================
    "右腕(袖)_上": (44, 32, 48, 36),
    "右腕(袖)_下": (48, 32, 52, 36),
    "右腕(袖)_右": (40, 36, 44, 48),
    "右腕(袖)_前": (44, 36, 48, 48),
    "右腕(袖)_左": (48, 36, 52, 48),
    "右腕(袖)_後": (52, 36, 56, 48),
    # =====================
    # 右脚（ズボン）
    # =====================
    "右脚(ズボン)_上": (4, 32, 8, 36),
    "右脚(ズボン)_下": (8, 32, 12, 36),
    "右脚(ズボン)_右": (0, 36, 4, 48),
    "右脚(ズボン)_前": (4, 36, 8, 48),
    "右脚(ズボン)_左": (8, 36, 12, 48),
    "右脚(ズボン)_後": (12, 36, 16, 48),
    # =====================
    # 左腕（袖）
    # =====================
    "左腕(袖)_上": (52, 48, 56, 52),
    "左腕(袖)_下": (56, 48, 60, 52),
    "左腕(袖)_右": (48, 52, 52, 64),
    "左腕(袖)_前": (52, 52, 56, 64),
    "左腕(袖)_左": (56, 52, 60, 64),
    "左腕(袖)_後": (60, 52, 64, 64),
    # =====================
    # 左脚（ズボン）
    # =====================
    "左腕(ズボン)_上": (4, 48, 8, 52),
    "左腕(ズボン)_下": (8, 48, 12, 52),
    "左脚(ズボン)_右": (0, 52, 4, 64),
    "左脚(ズボン)_前": (4, 52, 8, 64),
    "左脚(ズボン)_左": (8, 52, 12, 64),
    "左脚(ズボン)_後": (12, 52, 16, 64),
}

# =====================
# パレット定義
# =====================
PALETTE_COLORS = [
    (0, 0, 0),
    (255, 255, 255),
    (128, 128, 128),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 128, 0),
    (128, 0, 255),
    (0, 128, 255),
]


# =====================
# 描画処理
# =====================
def is_first_layer(x, y):
    for x1, y1, x2, y2 in FIRST_LAYER_AREAS.values():
        if x1 <= x < x2 and y1 <= y < y2:
            return True
    return False


def is_second_layer(x, y):
    for x1, y1, x2, y2 in SECOND_LAYER_AREAS.values():
        if x1 <= x < x2 and y1 <= y < y2:
            return True
    return False


def can_edit_pixel(x, y):
    # 第二レイヤーのみ編集モード
    if not edit_second_layer_only:
        return is_first_layer(x, y)
    else:
        return is_second_layer(x, y)


def draw_layer_invalid_mask():
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            if not edit_second_layer_only:
                if not is_first_layer(x, y):
                    canvas.create_rectangle(
                        MARGIN + x * PIXEL_SIZE,
                        MARGIN + y * PIXEL_SIZE,
                        MARGIN + (x + 1) * PIXEL_SIZE,
                        MARGIN + (y + 1) * PIXEL_SIZE,
                        fill="#000000",
                        stipple="gray50",
                        outline="",
                    )
            else:
                if not is_second_layer(x, y):
                    canvas.create_rectangle(
                        MARGIN + x * PIXEL_SIZE,
                        MARGIN + y * PIXEL_SIZE,
                        MARGIN + (x + 1) * PIXEL_SIZE,
                        MARGIN + (y + 1) * PIXEL_SIZE,
                        fill="#000000",
                        stipple="gray50",
                        outline="",
                    )


def draw_face_frames(face_dict, color="#800000"):
    for name, (x1, y1, x2, y2) in face_dict.items():
        canvas.create_rectangle(
            MARGIN + x1 * PIXEL_SIZE,
            MARGIN + y1 * PIXEL_SIZE,
            MARGIN + x2 * PIXEL_SIZE,
            MARGIN + y2 * PIXEL_SIZE,
            outline=color,
            width=1,
        )
        canvas.create_text(
            MARGIN + (x1 + x2) * PIXEL_SIZE // 2,
            MARGIN + y1 * PIXEL_SIZE - 6,
            text=name,
            fill=color,
            font=("Arial", 7),
        )


def draw_checkerboard():
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            if (x + y) % 2 == 0:
                color = "#b0b0b0"
            else:
                color = "#d0d0d0"
            canvas.create_rectangle(
                MARGIN + x * PIXEL_SIZE,
                MARGIN + y * PIXEL_SIZE,
                MARGIN + (x + 1) * PIXEL_SIZE,
                MARGIN + (y + 1) * PIXEL_SIZE,
                fill=color,
                outline="",
            )


def draw_frameline():
    if not edit_second_layer_only:
        for name, (x1, y1, x2, y2) in FIRST_LAYER_AREAS.items():
            canvas.create_rectangle(
                MARGIN + x1 * PIXEL_SIZE,
                MARGIN + y1 * PIXEL_SIZE,
                MARGIN + x2 * PIXEL_SIZE,
                MARGIN + y2 * PIXEL_SIZE,
                outline="#191970",
                width=1,
            )
            canvas.create_text(
                MARGIN + (x1 + x2) * PIXEL_SIZE // 2,
                MARGIN + y1 * PIXEL_SIZE - 8,
                text=name,
                fill="#191970",
                font=("Arial", 7),
            )

    else:
        for name, (x1, y1, x2, y2) in SECOND_LAYER_AREAS.items():
            canvas.create_rectangle(
                MARGIN + x1 * PIXEL_SIZE,
                MARGIN + y1 * PIXEL_SIZE,
                MARGIN + x2 * PIXEL_SIZE,
                MARGIN + y2 * PIXEL_SIZE,
                outline="#191970",
                width=1,
            )
            canvas.create_text(
                MARGIN + (x1 + x2) * PIXEL_SIZE // 2,
                MARGIN + y1 * PIXEL_SIZE - 8,
                text=name,
                fill="#191970",
                font=("Arial", 7),
            )
    # if current_part == "全体":
    # elif FIRST_LAYER_AREAS[current_part]:
    #    x1, y1, x2, y2 = FIRST_LAYER_AREAS[current_part]
    #    canvas.create_rectangle(
    #        MARGIN + x1 * PIXEL_SIZE,
    #        MARGIN + y1 * PIXEL_SIZE,
    #        MARGIN + x2 * PIXEL_SIZE,
    #        MARGIN + y2 * PIXEL_SIZE,
    #        outline="yellow",
    #        width=3,
    #    )


def draw_pixels(x, y):
    if not edit_second_layer_only:
        r, g, b, a = base_pixels[y][x]
    else:
        r, g, b, a = overlay_pixels[y][x]

    # すでに描画済みなら削除
    if pixel_items[y][x] is not None:
        canvas.delete(pixel_items[y][x])
        pixel_items[y][x] = None

    # 透明なら何も描かない（＝消しゴム）
    if a == 0:
        return

    pixel_items[y][x] = canvas.create_rectangle(
        MARGIN + x * PIXEL_SIZE,
        MARGIN + y * PIXEL_SIZE,
        MARGIN + (x + 1) * PIXEL_SIZE,
        MARGIN + (y + 1) * PIXEL_SIZE,
        fill=f"#{r:02x}{g:02x}{b:02x}",
        outline="",
    )


def redraw():
    canvas.delete("all")
    draw_checkerboard()
    draw_frameline()
    draw_layer_invalid_mask()

    # pixel_items をリセット
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            pixel_items[y][x] = None
            draw_pixels(x, y)


# =====================
# マウス描画
# =====================
def draw_pixel(event):
    global last_drawn

    x = (event.x - MARGIN) // PIXEL_SIZE
    y = (event.y - MARGIN) // PIXEL_SIZE

    if not (0 <= x < SKIN_SIZE and 0 <= y < SKIN_SIZE):
        return

    # ★ スポイトモード
    if tool_mode == "eyedropper":
        pick_color(event)
        set_tool("draw")  # 自動でペンに戻す
        return

    if not can_edit_pixel(x, y):
        return

    if last_drawn == (x, y):
        return

    last_drawn = (x, y)
    if is_first_layer(x, y):
        base_pixels[y][x] = current_color
    elif is_second_layer(x, y):
        overlay_pixels[y][x] = current_color

    draw_pixels(x, y)


def reset_last_drawn(event):
    global last_drawn
    last_drawn = None


# =====================
# 保存 / 読み込み
# =====================
def save_skin():
    path = filedialog.asksaveasfilename(defaultextension=".png")
    if not path:
        return

    img = Image.new("RGBA", (SKIN_SIZE, SKIN_SIZE))
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            bp = base_pixels[y][x]
            op = overlay_pixels[y][x]
            img.putpixel((x, y), op if op[3] > 0 else bp)

    img.save(path)


def load_skin():
    path = filedialog.askopenfilename(filetypes=[("Minecraft Skin", "*.png")])
    if not path:
        return

    img = Image.open(path).convert("RGBA")
    if img.size != (SKIN_SIZE, SKIN_SIZE):
        print("64x64スキン以外は非対応")
        return

    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            pixel = img.getpixel((x, y))
            if is_second_layer(x, y):
                overlay_pixels[y][x] = pixel
            else:
                base_pixels[y][x] = pixel

    redraw()


def save_user_palette():
    path = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("Palette File", "*.json")]
    )
    if not path:
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user_palette, f)

        messagebox.showinfo("保存完了", "ユーザーパレットを保存しました。")
    except Exception as e:
        messagebox.showerror("保存失敗", f"保存中にエラーが発生しました。\n\n{e}")


def load_user_palette():
    global user_palette

    path = filedialog.askopenfilename(
        title="ユーザーパレットを読み込む",
        filetypes=[("User Palette", "*.json")],
    )
    if not path:
        return  # キャンセル

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            loaded = data.get("user_palette")
        elif isinstance(data, list):
            loaded = data
        else:
            messagebox.showerror("読込失敗", "パレット形式が不正です。")
            return

        if not isinstance(loaded, list):
            messagebox.showerror("読込失敗", "パレットデータが不正です。")
            return

        # サイズを合わせる（安全策）
        user_palette = [
            tuple(c) if c is not None else None for c in loaded[:USER_PALETTE_SIZE]
        ]

        # 足りない分を None で埋める
        while len(user_palette) < USER_PALETTE_SIZE:
            user_palette.append(None)

        # ボタン表示更新
        for i in range(USER_PALETTE_SIZE):
            update_user_palette_button(i)

        messagebox.showinfo("読込完了", "ユーザーパレットを読み込みました。")
    except Exception as e:
        messagebox.showerror("読込失敗", f"読み込み中にエラーが発生しました。\n\n{e}")


# =====================
# 色関係
# =====================
def update_color_preview():
    color_preview.delete("all")

    r, g, b, a = current_color

    if a == 0:
        # 透明用チェッカーボード
        size = 10
        for y in range(0, 40, size):
            for x in range(0, 40, size):
                c = "#cccccc" if (x // size + y // size) % 2 == 0 else "#eeeeee"
                color_preview.create_rectangle(
                    x, y, x + size, y + size, fill=c, outline=""
                )
        color_preview.create_text(20, 20, text="透明", fill="#666", font=("Arial", 8))
        color_code_label.configure(text="透明")
    else:
        color_preview.create_rectangle(
            0, 0, 40, 40, fill=f"#{r:02x}{g:02x}{b:02x}", outline=""
        )
        color_code_label.configure(text=f"#{r:02X}{g:02X}{b:02X}")


def choose_color():
    global current_color
    color = colorchooser.askcolor(
        color=f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}"
    )
    if color[0] is None:
        return

    r, g, b = map(int, color[0])
    set_color((r, g, b, 255))


def pick_color(event):
    x = (event.x - MARGIN) // PIXEL_SIZE
    y = (event.y - MARGIN) // PIXEL_SIZE

    if not (0 <= x < SKIN_SIZE and 0 <= y < SKIN_SIZE):
        return

    # 表示優先順位：第二 → 第一
    op = overlay_pixels[y][x]
    if op[3] > 0:
        set_color(op)
        return

    bp = base_pixels[y][x]
    if bp[3] > 0:
        set_color(bp)
        return

    # 何もなければ透明（任意）
    set_color(TRANSPARENT)


def update_palette_selection(selected_rgb):
    for rgb, btn in palette_buttons.items():
        if rgb == selected_rgb:
            btn.configure(relief="solid", bd=0, highlightbackground="darkblue")
        else:
            btn.configure(relief="flat", bd=1, highlightbackground="#888888")

    # ユーザーパレット
    for i, btn in enumerate(user_palette_buttons):
        if user_palette[i] == current_color:
            btn.configure(relief="solid", bd=0, highlightbackground="darkblue")
        else:
            btn.configure(relief="flat", bd=1, highlightbackground="#888888")


def set_palette_color(rgb):
    global current_color
    r, g, b = rgb
    set_color((r, g, b, 255))
    update_palette_selection(rgb)


def set_color(color):
    global current_color
    current_color = color
    update_color_preview()


def set_tool(mode):
    global tool_mode
    tool_mode = mode


# =====================
# ユーザーパレット
# =====================
def select_user_palette_color(index):
    color = user_palette[index]
    if color is None:
        return

    set_palette_color(color)
    update_palette_selection(rgb)


def update_user_palette_button(index):
    palette_btn = user_palette_buttons[index]
    color = user_palette[index]

    if color is None:
        palette_btn.configure(bg="#cccccc")
    else:
        palette_btn.configure(bg=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")


def register_current_color():
    global user_palette

    r, g, b = current_color[:3]

    for i in range(USER_PALETTE_SIZE):
        if user_palette[i] is None:
            user_palette[i] = (r, g, b)
            update_user_palette_button(i)
            return

    # 全部埋まってたら先頭を上書き（好みで変えてOK）
    user_palette[0] = (r, g, b)
    update_user_palette_button(0)


def register_color_to_slot(idx):
    global user_palette

    r, g, b = current_color[:3]  # ← RGBA対策

    user_palette[idx] = (r, g, b)
    update_user_palette_button(idx)


# =====================
# カラーサークル
# =====================
def init_color_wheel():
    draw_hue_ring()
    draw_sv_square()
    draw_wheel_cursor()
    draw_sv_cursor()


def draw_hue_ring():
    global wheel_photo

    cx = cy = WHEEL_SIZE // 2
    radius = WHEEL_SIZE // 2
    inner_radius = radius - RING_WIDTH
    size = WHEEL_SIZE

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = img.load()

    for y in range(WHEEL_SIZE):
        for x in range(WHEEL_SIZE):
            dx = x - cx
            dy = y - cy
            distance = math.sqrt(dx * dx + dy * dy)

            if inner_radius <= distance <= radius:
                angle = math.atan2(dy, dx)
                hue = (angle + math.pi) / (2 * math.pi)

                r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                pixels[x, y] = (
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    255,
                )
    wheel_photo = ImageTk.PhotoImage(img)
    wheel_canvas.delete("all")
    wheel_canvas.create_image(0, 0, anchor="nw", image=wheel_photo)


def draw_sv_square():
    global sv_photo

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2

    sv_size = int((radius - RING_WIDTH - 20) * 2)

    start_x = int(cx - sv_size / 2)
    start_y = int(cy - sv_size / 2)

    img = Image.new("RGBA", (sv_size, sv_size))
    pixels = img.load()

    for y in range(sv_size):
        for x in range(sv_size):

            s = x / sv_size
            v = 1 - (y / sv_size)

            r, g, b = colorsys.hsv_to_rgb(current_hue, s, v)
            pixels[x, y] = (
                int(r * 255),
                int(g * 255),
                int(b * 255),
                255,
            )

    sv_photo = ImageTk.PhotoImage(img)

    wheel_canvas.delete("sv_image")
    wheel_canvas.create_image(
        start_x, start_y, anchor="nw", image=sv_photo, tags="sv_image"
    )

    draw_sv_cursor()


def draw_wheel_cursor():
    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2
    mid_radius = radius - RING_WIDTH / 2

    angle = current_hue * 2 * math.pi - math.pi

    x = cx + math.cos(angle) * mid_radius
    y = cy + math.sin(angle) * mid_radius

    wheel_canvas.create_oval(
        x - 5, y - 5, x + 5, y + 5, outline="black", width=2, tags="cursor"
    )

    wheel_canvas.create_oval(
        x - 4, y - 4, x + 4, y + 4, outline="white", width=2, tags="cursor"
    )


def draw_sv_cursor():
    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2
    sv_size = int((radius - RING_WIDTH - 20) * 2)

    start_x = cx - sv_size / 2
    start_y = cy - sv_size / 2

    x = start_x + current_s * sv_size
    y = start_y + (1 - current_v) * sv_size

    wheel_canvas.create_oval(
        x - 5, y - 5, x + 5, y + 5, outline="black", width=2, tags="sv"
    )

    wheel_canvas.create_oval(
        x - 4, y - 4, x + 4, y + 4, outline="white", width=2, tags="sv"
    )


def redraw_sv_square():
    wheel_canvas.delete("sv")
    wheel_canvas.delete("sv_image")
    draw_sv_square()


def redraw_cursors():
    wheel_canvas.delete("cursor")
    draw_wheel_cursor()


def pick_color_from_wheel(event):
    global current_hue

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2

    dx = event.x - cx
    dy = event.y - cy
    distance = (dx * dx + dy * dy) ** 0.5

    inner_radius = radius - RING_WIDTH

    # リング内ならHue変更
    if inner_radius <= distance <= radius:
        angle = math.atan2(dy, dx)
        current_hue = (angle + math.pi) / (2 * math.pi)
        redraw_sv_square()
        redraw_cursors()

    # 正方形内なら色取得
    else:
        pick_color_from_sv(event)


def pick_color_from_sv(event):
    global current_s, current_v

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2
    sv_size = int((radius - RING_WIDTH - 20) * 2)

    start_x = int(cx - sv_size / 2)
    start_y = int(cy - sv_size / 2)

    if not (
        start_x <= event.x <= start_x + sv_size
        and start_y <= event.y <= start_y + sv_size
    ):
        return

    current_s = (event.x - start_x) / sv_size
    current_v = 1 - ((event.y - start_y) / sv_size)

    r, g, b = colorsys.hsv_to_rgb(current_hue, current_s, current_v)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    set_palette_color((r, g, b))
    redraw_sv_square()


# =====================
# 第二レイヤー
# =====================
def toggle_edit_second_layer():
    global edit_second_layer_only
    edit_second_layer_only = edit_second_layer_var.get()
    redraw()


# =====================
# 部位選択UI
# =====================
def set_part(value):
    global current_part
    current_part = value


# =====================
# GUI
# =====================
root = tk.Tk()
root.title("BlockTailor Studio (Python)")

# 左右レイアウト設定
root.grid_columnconfigure(0, weight=1)  # 左は伸びる
root.grid_columnconfigure(1, weight=0)  # 右は固定
root.grid_rowconfigure(0, weight=1)

# =====================
# Canvas
# =====================
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=0, sticky="nsew")

canvas = tk.Canvas(
    canvas_frame,
    width=CANVAS_SIZE + MARGIN * 2,
    height=CANVAS_SIZE + MARGIN * 2,
    bg="#FFFFFF",
)
canvas.pack(expand=True)

canvas.bind("<Button-1>", draw_pixel)
canvas.bind("<B1-Motion>", draw_pixel)
canvas.bind("<Button-3>", pick_color)
canvas.bind("<ButtonRelease-1>", reset_last_drawn)


# =====================
# 📦 toolbar
# =====================
TOOLBAR_WIDTH = 303

toolbar_container = tk.Frame(root, width=TOOLBAR_WIDTH)
toolbar_container.grid(row=0, column=1, sticky="ns")
toolbar_container.grid_propagate(False)  # 幅固定

# スクロール用Canvas
scroll_canvas = tk.Canvas(toolbar_container, highlightthickness=0)
scroll_canvas.grid(row=0, column=0, sticky="nsew")

# スクロールバー
scrollbar = tk.Scrollbar(
    toolbar_container, orient="vertical", command=scroll_canvas.yview
)
scrollbar.grid(row=0, column=1, sticky="ns")

scroll_canvas.configure(yscrollcommand=scrollbar.set)

# 伸縮設定
toolbar_container.grid_rowconfigure(0, weight=1)
toolbar_container.grid_columnconfigure(0, weight=1)

# 中身のFrame
toolbar = tk.Frame(scroll_canvas)
scroll_canvas.create_window((0, 0), window=toolbar, anchor="nw")
scroll_canvas.configure(width=300)


# サイズ変更時にスクロール範囲更新
def update_scrollregion(event=None):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))


toolbar.bind("<Configure>", update_scrollregion)


def _on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
scroll_canvas.bind_all("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))
scroll_canvas.bind_all("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))


# =========================
# 🎨 カラーセクション
# =========================
color_section = tk.LabelFrame(toolbar, text="🎨 カラー", padx=5, pady=5)
color_section.pack(fill=tk.X, pady=5)


# カラーサークル
wheel_canvas = tk.Canvas(color_section, width=WHEEL_SIZE, height=WHEEL_SIZE)
wheel_canvas.pack()
wheel_canvas.bind("<Button-1>", pick_color_from_wheel)

# カラーパレット
tk.Button(color_section, text="カラーパレット", command=choose_color).pack(
    fill=tk.X, pady=5
)

# 既存カラーパレット
palette_frame = tk.Frame(color_section)
palette_frame.pack(pady=5)

palette_buttons = {}

for i, rgb in enumerate(PALETTE_COLORS):
    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    btn = tk.Button(
        palette_frame,
        bg=hex_color,
        activebackground=hex_color,  # ← 灰色にしない
        width=2,
        height=1,
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground="#888888",
        command=lambda c=rgb: set_palette_color(c),
    )

    btn.grid(row=i // 6, column=i % 6, padx=1, pady=1)
    palette_buttons[rgb] = btn


# =========================
# 👤 ユーザーパレット
# =========================
tk.Label(color_section, text="ユーザーパレット").pack(pady=(10, 2))

user_palette_frame = tk.Frame(color_section)
user_palette_frame.pack(pady=5)

for i in range(USER_PALETTE_SIZE):
    btn = tk.Button(
        user_palette_frame,
        width=2,
        height=1,
        bd=0,
        relief="flat",
        bg="#cccccc",
        command=lambda idx=i: select_user_palette_color(idx),
    )
    btn.grid(row=i // 6, column=i % 6, padx=2, pady=2)
    # ★ 右クリックで登録
    btn.bind("<Button-3>", lambda e, idx=i: register_color_to_slot(idx))
    user_palette_buttons.append(btn)

# 横並び用フレーム
current_color_row = tk.Frame(color_section)
current_color_row.pack(fill="x", pady=5)

# 3列構成にする
current_color_row.columnconfigure(0, weight=1)
current_color_row.columnconfigure(1, weight=0)
current_color_row.columnconfigure(2, weight=0)
current_color_row.columnconfigure(3, weight=1)

# ===== 中央ブロック =====
current_color_block = tk.Frame(current_color_row)
current_color_block.grid(row=0, column=1)

tk.Label(current_color_block, text="現在の色").pack(pady=(0, 2))

color_preview = tk.Canvas(
    current_color_block,
    width=20,
    height=20,
    bg="#ffffff",
    highlightthickness=1,
    highlightbackground="#000000",
)
color_preview.pack()

color_code_label = tk.Label(current_color_block, text="#FF0000", font=("Arial", 9))
color_code_label.pack()

# ===== 登録ボタン =====
tk.Button(current_color_row, text="登録", command=register_current_color).grid(
    row=0, column=2, padx=(15, 0)
)


# パレット保存/読込
palette_io_frame = tk.Frame(color_section)
palette_io_frame.pack(fill=tk.X, pady=2)

tk.Button(palette_io_frame, text="パレット保存", command=save_user_palette).pack(
    side=tk.LEFT, expand=True, fill=tk.X, padx=2
)
tk.Button(palette_io_frame, text="パレット読込", command=load_user_palette).pack(
    side=tk.RIGHT, expand=True, fill=tk.X, padx=2
)

# =========================
# 🖌 ツールセクション
# =========================
tool_section = tk.LabelFrame(toolbar, text="🖌 ツール", padx=5, pady=5)
tool_section.pack(fill=tk.X, pady=5)

tool_row = tk.Frame(tool_section)
tool_row.pack(fill=tk.X)

# ペン
tk.Button(tool_row, text="ペン", command=lambda: set_tool("draw")).pack(fill=tk.X)

# スポイト
tk.Button(tool_row, text="スポイト", command=lambda: set_tool("eyedropper")).pack(
    fill=tk.X
)

# 消しゴム
tk.Button(tool_row, text="消しゴム", command=lambda: set_color(TRANSPARENT)).pack(
    fill=tk.X
)

# =========================
# ⚙ レイヤーセクション
# =========================
layer_section = tk.LabelFrame(toolbar, text="⚙ レイヤー", padx=5, pady=5)
layer_section.pack(fill=tk.X, pady=5)
# 第二レイヤー編集
edit_second_layer_var = tk.BooleanVar(value=False)
tk.Checkbutton(
    layer_section,
    text="第二レイヤー編集",
    variable=edit_second_layer_var,
    command=toggle_edit_second_layer,
).pack(anchor="w")

# =========================
# 💾 ファイルセクション
# =========================
file_section = tk.LabelFrame(toolbar, text="💾 ファイル", padx=5, pady=5)
file_section.pack(fill=tk.X, pady=5)

# 保存
tk.Button(file_section, text="保存", command=save_skin).pack(fill=tk.X, pady=2)

# 読み込み
tk.Button(file_section, text="読込", command=load_skin).pack(fill=tk.X, pady=2)


# パーツ表示
part_var = tk.StringVar(value=current_part)
part_menu_item = {"全体": None, **FIRST_LAYER_AREAS}
part_menu = tk.OptionMenu(toolbar, part_var, *part_menu_item.keys(), command=set_part)
part_menu.pack(fill=tk.X, pady=10)


# =====================
# 起動
# =====================
redraw()
init_color_wheel()
update_color_preview()
root.mainloop()
