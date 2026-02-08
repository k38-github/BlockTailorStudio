import tkinter as tk
from tkinter import filedialog
from PIL import Image

# =====================
# 定数
# =====================
SKIN_SIZE = 64
PIXEL_SIZE = 10
MARGIN = 20
CANVAS_SIZE = SKIN_SIZE * PIXEL_SIZE + MARGIN * 2

TRANSPARENT = (0, 0, 0, 0)
current_color = (255, 0, 0, 255)  # 赤

current_part = "全体"
edit_second_layer_only = False

# =====================
# データ
# =====================
# 第一スキンレイヤーデータ
base_pixels = [[TRANSPARENT for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)]

# 第二スキンレイヤーデータ
overlay_pixels = [[TRANSPARENT for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)]

# =====================
# マイクラ部位定義
# =====================
# =====================
# 第一スキンレイヤー範囲
# =====================
FIRST_LAYER_AREAS = {
    # 頭
    "頭_上": (8, 0, 16, 8),
    "頭_下": (16, 0, 24, 8),
    "頭_右": (0, 8, 8, 16),
    "頭_前": (8, 8, 16, 16),
    "頭_左": (16, 8, 24, 16),
    "頭_後": (24, 8, 32, 16),
    # 体
    "体_上": (20, 16, 28, 20),
    "体_下": (28, 16, 36, 20),
    "体_右": (16, 20, 20, 32),
    "体_前": (20, 20, 28, 32),
    "体_左": (28, 20, 32, 32),
    "体_後": (32, 20, 40, 32),
    # 左右腕
    "左右腕_上": (44, 16, 48, 20),
    "左右腕_下": (48, 16, 52, 20),
    "左右腕_右": (40, 20, 44, 32),
    "左右腕_前": (44, 20, 48, 32),
    "左右腕_左": (48, 20, 52, 32),
    "左右腕_後": (52, 20, 56, 32),
    # 左右脚
    "左右脚_上": (4, 16, 8, 20),
    "左右脚_下": (8, 16, 12, 20),
    "左右脚_右": (0, 20, 4, 32),
    "左右脚_前": (4, 20, 8, 32),
    "左右脚_左": (8, 20, 12, 32),
    "左右脚_後": (12, 20, 16, 32),
    ## 左腕
    # "左腕_上": (36, 48, 40, 52),
    # "左腕_下": (40, 48, 44, 52),
    # "左腕_右": (32, 52, 36, 64),
    # "左腕_前": (36, 52, 40, 64),
    # "左腕_左": (40, 52, 44, 64),
    # "左腕_後": (44, 52, 48, 64),
    ## 左脚
    # "左脚_上": (20, 48, 24, 52),
    # "左脚_下": (24, 48, 28, 52),
    # "左脚_右": (16, 52, 20, 64),
    # "左脚_前": (20, 52, 24, 64),
    # "左脚_左": (24, 52, 28, 64),
    # "左脚_後": (28, 52, 32, 64),
}

# =====================
# 第二スキンレイヤー範囲
# =====================
SECOND_LAYER_AREAS = {
    # 頭
    "頭(帽子)_上": (40, 0, 48, 8),
    "頭(帽子)_下": (48, 0, 56, 8),
    "頭(帽子)_右": (32, 8, 40, 16),
    "頭(帽子)_前": (40, 8, 48, 16),
    "頭(帽子)_左": (48, 8, 56, 16),
    "頭(帽子)_後": (56, 8, 64, 16),
    # 体
    "体(上着)_上": (20, 32, 28, 36),
    "体(上着)_下": (28, 32, 36, 36),
    "体(上着)_右": (16, 36, 20, 48),
    "体(上着)_前": (20, 36, 28, 48),
    "体(上着)_左": (28, 36, 32, 48),
    "体(上着)_後": (32, 36, 40, 48),
    # 右腕
    "右腕(袖)_上": (44, 32, 48, 36),
    "右腕(袖)_下": (48, 32, 52, 36),
    "右腕(袖)_右": (40, 36, 44, 48),
    "右腕(袖)_前": (44, 36, 48, 48),
    "右腕(袖)_左": (48, 36, 52, 48),
    "右腕(袖)_後": (52, 36, 56, 48),
    # 左腕
    "左腕(袖)_上": (36, 48, 40, 52),
    "左腕(袖)_下": (40, 48, 44, 52),
    "左腕(袖)_右": (32, 52, 36, 64),
    "左腕(袖)_前": (36, 52, 40, 64),
    "左腕(袖)_左": (40, 52, 44, 64),
    "左腕(袖)_後": (44, 52, 48, 64),
    # 右脚
    "右脚(ズボン)_上": (4, 32, 8, 36),
    "右脚(ズボン)_下": (8, 32, 12, 36),
    "右脚(ズボン)_右": (0, 36, 4, 48),
    "右脚(ズボン)_前": (4, 36, 8, 48),
    "右脚(ズボン)_左": (8, 36, 12, 48),
    "右脚(ズボン)_後": (12, 36, 16, 48),
    # 左脚
    "左脚(ズボン)_上": (20, 48, 24, 52),
    "左脚(ズボン)_下": (24, 48, 28, 52),
    "左脚(ズボン)_右": (16, 52, 20, 64),
    "左脚(ズボン)_前": (20, 52, 24, 64),
    "左脚(ズボン)_左": (24, 52, 28, 64),
    "左脚(ズボン)_後": (28, 52, 32, 64),
}


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


def is_valid_first_layer(x, y):
    # 第二レイヤー領域は除外
    if is_second_layer(x, y):
        return False

    return True


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


def draw_pixels():
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            if not edit_second_layer_only:
                if is_first_layer(x, y):
                    r, g, b, a = base_pixels[y][x]
                    if a > 0:
                        canvas.create_rectangle(
                            MARGIN + x * PIXEL_SIZE,
                            MARGIN + y * PIXEL_SIZE,
                            MARGIN + (x + 1) * PIXEL_SIZE,
                            MARGIN + (y + 1) * PIXEL_SIZE,
                            fill=f"#{r:02x}{g:02x}{b:02x}",
                            outline="",
                        )
            else:
                if is_second_layer(x, y):
                    r, g, b, a = overlay_pixels[y][x]
                    if a > 0:
                        canvas.create_rectangle(
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
    draw_pixels()


# =====================
# マウス描画
# =====================
def draw_pixel(event):
    x = (event.x - MARGIN) // PIXEL_SIZE
    y = (event.y - MARGIN) // PIXEL_SIZE

    if not (0 <= x < SKIN_SIZE and 0 <= y < SKIN_SIZE):
        return

    if not can_edit_pixel(x, y):
        return

    if is_first_layer(x, y):
        base_pixels[y][x] = current_color
    elif is_second_layer(x, y):
        overlay_pixels[y][x] = current_color

    redraw()


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


# =====================
# 色変更（簡易ボタン）
# =====================
def set_color(color):
    global current_color
    current_color = color


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
    redraw()


# =====================
# GUI
# =====================
root = tk.Tk()
root.title("BlockTailor Studio (Python)")

canvas = tk.Canvas(
    root,
    width=CANVAS_SIZE + MARGIN * 2,
    height=CANVAS_SIZE + MARGIN * 2,
    bg="#FFFFFF",
)
canvas.pack(side=tk.LEFT)
canvas.bind("<Button-1>", draw_pixel)
canvas.bind("<B1-Motion>", draw_pixel)

toolbar = tk.Frame(root)
toolbar.pack(side=tk.RIGHT, fill=tk.Y)

tk.Button(toolbar, text="赤", command=lambda: set_color((255, 0, 0, 255))).pack(
    fill=tk.X
)
tk.Button(toolbar, text="緑", command=lambda: set_color((0, 255, 0, 255))).pack(
    fill=tk.X
)
tk.Button(toolbar, text="青", command=lambda: set_color((0, 0, 255, 255))).pack(
    fill=tk.X
)
tk.Button(toolbar, text="黒", command=lambda: set_color((0, 0, 0, 255))).pack(fill=tk.X)
tk.Button(toolbar, text="白", command=lambda: set_color((255, 255, 255, 255))).pack(
    fill=tk.X
)

tk.Button(toolbar, text="消しゴム", command=lambda: set_color(TRANSPARENT)).pack(
    fill=tk.X
)


tk.Button(toolbar, text="保存", command=save_skin).pack(fill=tk.X, pady=10)
tk.Button(toolbar, text="読み込み", command=load_skin).pack(fill=tk.X)


edit_second_layer_var = tk.BooleanVar(value=False)

tk.Checkbutton(
    toolbar,
    text="第二レイヤー編集",
    variable=edit_second_layer_var,
    command=toggle_edit_second_layer,
).pack(fill=tk.X, pady=5)


part_var = tk.StringVar(value=current_part)

part_menu_item = {"全体": None, **FIRST_LAYER_AREAS}
part_menu = tk.OptionMenu(toolbar, part_var, *part_menu_item.keys(), command=set_part)
part_menu.pack(fill=tk.X, pady=10)

# =====================
# 起動
# =====================
redraw()
root.mainloop()
