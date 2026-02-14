import json
import colorsys
import math

import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox

from PIL import Image, ImageTk
from PIL import ImageDraw
from typing import Optional

# =====================
# 定数
# =====================
SKIN_SIZE = 64
PIXEL_SIZE = 10
MARGIN = 20
CANVAS_SIZE = SKIN_SIZE * PIXEL_SIZE + MARGIN * 2
WHEEL_SIZE = 140
RING_WIDTH = 12

RGB_BAR_WIDTH = 256
RGB_BAR_HEIGHT = 12

TRANSPARENT = (0, 0, 0, 0)
current_color = (255, 0, 0, 255)  # 赤

current_part = "全体"
edit_second_layer_only = False
last_drawn = None
tool_mode = "draw"  # "draw" or "eyedropper"

USER_PALETTE_SIZE = 36
user_palette = [None] * USER_PALETTE_SIZE
user_palette_buttons = []

current_hue = 0.0  # 0.0〜1.0
current_s = 1.0
current_v = 1.0

wheel_photo = None
sv_photo = None

sv_cursor_photo = None
sv_cursor_id = None
cursor_photo = None
cursor_id = None


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
    for rgb, canvas in palette_buttons.items():
        if rgb == selected_rgb:
            canvas.itemconfig("selection", state="normal", outline="#000000")
        else:
            canvas.itemconfig("selection", state="hidden", outline="#888888")

    # ユーザーパレット
    for i, canvas in enumerate(user_palette_buttons):
        if user_palette[i] == selected_rgb:
            canvas.itemconfig("selection", state="normal", outline="#000000")
        else:
            canvas.itemconfig("selection", state="hidden", outline="#888888")


def set_palette_color(rgb):
    global current_color
    r, g, b = rgb
    set_color((r, g, b, 255))
    update_palette_selection(rgb)
    r_scale.set(r)
    g_scale.set(g)
    b_scale.set(b)


def set_color(color):
    global current_color
    current_color = color
    update_color_preview()


def set_tool(mode):
    global tool_mode
    tool_mode = mode


# =====================
# カラーパレット
# =====================
PALETTE_CELL_SIZE = 24


def create_palette_cell(parent, rgb):
    size = PALETTE_CELL_SIZE
    hex_color = "#%02x%02x%02x" % rgb

    canvas = tk.Canvas(parent, width=size, height=size, highlightthickness=0, bd=0)

    # 色本体
    canvas.create_rectangle(
        2, 2, size - 2, size - 2, fill=hex_color, outline="#808080", tags="color"
    )

    # 選択枠（最初は非表示）
    canvas.create_rectangle(
        1,
        1,
        size - 1,
        size - 1,
        outline="white",
        width=1,
        tags="selection",
        state="hidden",
    )

    canvas.bind("<Button-1>", lambda e: set_palette_color(rgb))

    return canvas


# =====================
# ユーザーパレット
# =====================
def create_user_palette_cell(parent):
    size = PALETTE_CELL_SIZE
    rgb = user_palette[i] if i < len(user_palette) else None

    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        highlightthickness=0,
        bd=0,
    )

    # 背景色（未登録ならグレー）
    if rgb:
        hex_color = "#%02x%02x%02x" % rgb
    else:
        hex_color = "#cccccc"

    canvas.create_rectangle(
        2,
        2,
        size - 2,
        size - 2,
        fill=hex_color,
        outline="#808080",
        tags="color",
    )

    # 選択枠（非表示）
    canvas.create_rectangle(
        1,
        1,
        size - 1,
        size - 1,
        outline="white",
        width=1,
        tags="selection",
        state="hidden",
    )

    # 左クリック：選択
    canvas.bind("<Button-1>", lambda e, idx=i: select_user_palette_color(idx))

    # 右クリック：登録
    canvas.bind("<Button-3>", lambda e, idx=i: register_color_to_slot(idx))

    return canvas


def select_user_palette_color(index):
    color = user_palette[index]
    if color is None:
        return

    set_palette_color(color)
    update_palette_selection(color)


def update_user_palette_button(index):
    cell = user_palette_buttons[index]
    color = user_palette[index]

    if color is None:
        hex_color = "#cccccc"
    else:
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    cell.itemconfig("color", fill=hex_color)


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
    global cursor_photo
    global cursor_id
    global sv_cursor_photo
    global sv_cursor_id

    draw_hue_ring()
    cursor_photo = create_cursor_image()
    cursor_id = wheel_canvas.create_image(
        WHEEL_SIZE // 2, WHEEL_SIZE // 2, image=cursor_photo, anchor="center"
    )
    redraw_hue_cursor()
    sv_cursor_photo = create_cursor_image()
    sv_cursor_id = wheel_canvas.create_image(
        0, 0, image=sv_cursor_photo, anchor="center"
    )
    draw_sv_square()
    redraw_sv_cursor()


def draw_hue_ring():
    global wheel_photo

    scale = 3
    size = WHEEL_SIZE * scale
    cx = cy = size // 2
    radius = size // 2 - (scale * 2)
    inner_radius = radius - (RING_WIDTH * scale)

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

    img = img.resize((WHEEL_SIZE - 1, WHEEL_SIZE - 1), Image.Resampling.LANCZOS)

    wheel_photo = ImageTk.PhotoImage(img)
    wheel_canvas.delete("all")
    wheel_canvas.create_image(
        WHEEL_SIZE / 2, WHEEL_SIZE / 2, anchor="center", image=wheel_photo
    )


def draw_sv_square():
    global sv_photo

    cx = WHEEL_SIZE / 2 + 1
    cy = WHEEL_SIZE / 2 + 1
    radius = WHEEL_SIZE // 2

    sv_size = int((radius - RING_WIDTH - 20) * 2)

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

    # 枠を描く
    draw = ImageDraw.Draw(img)

    # ① 半透明外枠（少し太め）
    draw.rectangle(
        (0, 0, sv_size - 1, sv_size - 1), outline=(70, 30, 132, 140), width=1  # RGBA
    )

    # ② 内側1px白枠
    draw.rectangle(
        (1, 1, sv_size - 2, sv_size - 2), outline=(255, 255, 255, 255), width=1
    )

    sv_photo = ImageTk.PhotoImage(img)
    wheel_canvas.delete("sv_image")
    wheel_canvas.create_image(cx, cy, anchor="center", image=sv_photo, tags="sv_image")

    redraw_sv_cursor()
    wheel_canvas.tag_raise(sv_cursor_id)


def create_cursor_image(diameter=14, scale=3):
    size = diameter * scale
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    outer_width = 3 * scale
    inner_width = 1 * scale

    # 外黒リング
    draw.ellipse(
        (
            outer_width // 2,
            outer_width // 2,
            size - outer_width // 2 - 1,
            size - outer_width // 2 - 1,
        ),
        outline=(70, 130, 182, 180),
        width=outer_width,
    )

    # 内白リング
    draw.ellipse(
        (
            outer_width,
            outer_width,
            size - outer_width - 1,
            size - outer_width - 1,
        ),
        outline=(255, 255, 255, 255),
        width=inner_width,
    )

    img = img.resize((diameter, diameter), Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(img)


def redraw_hue_cursor():
    global cursor_id

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE / 2
    inner_radius = radius - RING_WIDTH - 2

    # リング中央半径
    cursor_radius = inner_radius + (RING_WIDTH / 2)

    angle = current_hue * 2 * math.pi - math.pi

    x = cx + cursor_radius * math.cos(angle)
    y = cy + cursor_radius * math.sin(angle)

    # 画像カーソルは中心座標だけ
    wheel_canvas.coords(cursor_id, x, y)


def redraw_sv_square():
    wheel_canvas.delete("sv")
    wheel_canvas.delete("sv_image")
    draw_sv_square()
    wheel_canvas.tag_raise(sv_cursor_id)


def redraw_sv_cursor():
    global sv_cursor_id

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2

    sv_size = int((radius - RING_WIDTH - 20) * 2)

    start_x = cx - sv_size / 2
    start_y = cy - sv_size / 2

    x = start_x + current_s * sv_size
    y = start_y + (1 - current_v) * sv_size

    # 画像カーソルは中心座標のみ
    wheel_canvas.coords(sv_cursor_id, x, y)


def pick_color_from_wheel(event):
    global current_hue
    global cursor_id

    cx = WHEEL_SIZE / 2
    cy = WHEEL_SIZE / 2
    radius = WHEEL_SIZE // 2 - 2

    dx = event.x - cx
    dy = event.y - cy
    distance = (dx * dx + dy * dy) ** 0.5

    inner_radius = radius - RING_WIDTH

    # リング内ならHue変更
    if inner_radius <= distance <= radius:
        angle = math.atan2(dy, dx)
        current_hue = (angle + math.pi) / (2 * math.pi)

        # リング外に出ないよう制限
        if distance > radius:
            scale_factor = radius / distance
            dx *= scale_factor
            dy *= scale_factor

        wheel_canvas.coords(cursor_id, cx + dx, cy + dy)

        redraw_sv_square()
        redraw_hue_cursor()

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
# RGBバー
# =====================
def update_from_rgb():
    global current_hue, current_s, current_v

    r = r_scale.get() / 255
    g = g_scale.get() / 255
    b = b_scale.get() / 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    current_hue = h
    current_s = s
    current_v = v

    redraw_sv_square()
    redraw_hue_cursor()


def create_rgb_row(channel):
    row_frame = tk.Frame(rgb_frame)

    # 左ラベル
    label = tk.Label(row_frame, text=channel.upper(), width=2)
    label.pack(side="left")

    # バー
    bar = create_rgb_bar(row_frame, channel)
    bar.pack(side="left", fill="x", expand=True)

    # 右数値ラベル
    value_label = tk.Label(row_frame, text="0", width=4, anchor="e")
    value_label.pack(side="right")

    row_frame.pack(fill="x", pady=4)

    return bar, value_label


def create_rgb_bar(parent, channel):
    canvas = tk.Canvas(
        parent,
        width=RGB_BAR_WIDTH,
        height=RGB_BAR_HEIGHT,
        highlightthickness=0,
        bd=0,
    )

    # --- グラデーション生成 ---
    img = Image.new("RGB", (RGB_BAR_WIDTH, RGB_BAR_HEIGHT))
    pixels = img.load()

    for x in range(RGB_BAR_WIDTH):
        value = x
        for y in range(RGB_BAR_HEIGHT):
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

    canvas.bind("<Button-1>", on_rgb_bar_click)
    canvas.bind("<B1-Motion>", on_rgb_bar_click)

    return canvas


def get_current_rgb():
    r, g, b = colorsys.hsv_to_rgb(current_hue, current_s, current_v)
    return int(r * 255), int(g * 255), int(b * 255)


def on_rgb_bar_click(event):
    global current_hue, current_s, current_v

    canvas = event.widget
    channel = canvas.channel

    value = max(0, min(255, event.x))

    # 現在色取得
    r, g, b = get_current_rgb()

    if channel == "r":
        r = value
    elif channel == "g":
        g = value
    elif channel == "b":
        b = value

    # HSVへ変換
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    current_hue = h
    current_s = s
    current_v = v

    update_all_from_hsv()


def update_all_from_hsv():
    r, g, b = colorsys.hsv_to_rgb(current_hue, current_s, current_v)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    set_palette_color((r, g, b))

    redraw_sv_square()
    redraw_hue_cursor()
    redraw_rgb_cursors(r, g, b)


def draw_rgb_cursor(canvas, value):
    canvas.delete("cursor")

    x = value

    canvas.create_line(x, 0, x, RGB_BAR_HEIGHT, fill="white", width=2, tags="cursor")


def redraw_rgb_cursors(r, g, b):
    draw_rgb_cursor(r_bar, r)
    draw_rgb_cursor(g_bar, g)
    draw_rgb_cursor(b_bar, b)

    r_value_label.config(text=str(r))
    g_value_label.config(text=str(g))
    b_value_label.config(text=str(b))


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
TOOLBAR_WIDTH = 350

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
wheel_canvas.bind("<B1-Motion>", pick_color_from_wheel)

# RGBバー
rgb_frame = tk.Frame(color_section)
rgb_frame.pack(fill="x", pady=10)

r_scale = tk.Scale(
    rgb_frame, from_=0, to=255, orient="horizontal", label="R", command=update_from_rgb
)

g_scale = tk.Scale(
    rgb_frame, from_=0, to=255, orient="horizontal", label="G", command=update_from_rgb
)

b_scale = tk.Scale(
    rgb_frame, from_=0, to=255, orient="horizontal", label="B", command=update_from_rgb
)

r_bar, r_value_label = create_rgb_row("r")
g_bar, g_value_label = create_rgb_row("g")
b_bar, b_value_label = create_rgb_row("b")

r_bar.pack(pady=4)
g_bar.pack(pady=4)
b_bar.pack(pady=4)

# 初期カーソル描画
r, g, b = get_current_rgb()
redraw_rgb_cursors(r, g, b)


# カラーパレット
tk.Button(color_section, text="カラーパレット", command=choose_color).pack(
    fill=tk.X, pady=5
)

# 既存カラーパレット
palette_frame = tk.Frame(color_section)
palette_frame.pack(pady=5)

palette_buttons = {}
for rgb in PALETTE_COLORS:
    cell = create_palette_cell(palette_frame, rgb)
    cell.pack(side="left", padx=1, pady=1)
    palette_buttons[rgb] = cell


# =========================
# 👤 ユーザーパレット
# =========================
tk.Label(color_section, text="ユーザーパレット").pack(pady=(10, 2))

user_palette_frame = tk.Frame(color_section)
user_palette_frame.pack(pady=5)

for i in range(USER_PALETTE_SIZE):
    cell = create_user_palette_cell(user_palette_frame)
    cell.grid(row=i // 12, column=i % 12, padx=1, pady=1)

    user_palette_buttons.append(cell)

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
