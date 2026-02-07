import tkinter as tk
from tkinter import filedialog
from PIL import Image

# =====================
# 設定
# =====================
SKIN_SIZE = 64
PIXEL_SIZE = 10
CANVAS_SIZE = SKIN_SIZE * PIXEL_SIZE
MARGIN_X = 20
MARGIN_Y = 30

TRANSPARENT = (0, 0, 0, 0)

# =====================
# 初期データ
# =====================
pixels = [[(0, 0, 0, 0) for _ in range(SKIN_SIZE)] for _ in range(SKIN_SIZE)]

current_color = (255, 0, 0, 255)  # 赤
current_part = "全体"
show_second_layer = True
show_fine_faces = True
edit_second_layer_only = False

# =====================
# マイクラ部位定義
# =====================
PARTS = {
    "全体": None,
    # 頭
    "頭(前)": (8, 8, 16, 16),
    "頭(後)": (24, 8, 32, 16),
    "頭(右)": (0, 8, 8, 16),
    "頭(左)": (16, 8, 24, 16),
    "頭(上)": (8, 0, 16, 8),
    "頭(下)": (16, 0, 24, 8),
    # 体
    "体(前)": (20, 20, 28, 32),
    "体(後)": (32, 20, 40, 32),
    # 右腕
    "右腕(前)": (44, 20, 48, 32),
    "右腕(後)": (52, 20, 56, 32),
    # 左腕（第二レイヤー基準）
    "左腕(前)": (36, 52, 40, 64),
    "左腕(後)": (44, 52, 48, 64),
}

# =====================
# 全体表示用：完全部位枠
# =====================
PARTS_FULL = {
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
    # 右腕
    "右腕_上": (44, 16, 48, 20),
    "右腕_下": (48, 16, 52, 20),
    "右腕_右": (40, 20, 44, 32),
    "右腕_前": (44, 20, 48, 32),
    "右腕_左": (48, 20, 52, 32),
    "右腕_後": (52, 20, 56, 32),
    # 右脚
    "右脚_上": (4, 16, 8, 20),
    "右脚_下": (8, 16, 12, 20),
    "右脚_右": (0, 20, 4, 32),
    "右脚_前": (4, 20, 8, 32),
    "右脚_左": (8, 20, 12, 32),
    "右脚_後": (12, 20, 16, 32),
    # 左腕
    "左腕_上": (36, 48, 40, 52),
    "左腕_下": (40, 48, 44, 52),
    "左腕_右": (32, 52, 36, 64),
    "左腕_前": (36, 52, 40, 64),
    "左腕_左": (40, 52, 44, 64),
    "左腕_後": (44, 52, 48, 64),
    # 左脚
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
SECOND_LAYER_AREAS = [
    # 頭（帽子）
    (32, 0, 64, 16),
    # 体（上着）
    (16, 32, 40, 48),
    # 右腕
    (40, 32, 56, 48),
    # 左腕
    (32, 48, 48, 64),
    # 右脚
    (0, 32, 16, 48),
    # 左脚
    (16, 48, 32, 64),
]

# =====================
# 第二レイヤー：表示用ラベル枠
# =====================
SECOND_LAYER_LABELS = {
    "頭(帽子)": (32, 0, 64, 16),
    "体(上着)": (16, 32, 40, 48),
    "右腕(袖)": (40, 32, 56, 48),
    "左腕(袖)": (32, 48, 48, 64),
    "右脚(ズボン)": (0, 32, 16, 48),
    "左脚(ズボン)": (16, 48, 32, 64),
}

# =====================
# 第二レイヤー：頭（帽子）面単位
# =====================
SECOND_LAYER_HEAD_FACES = {
    "頭(帽子)_上": (40, 0, 48, 8),
    "頭(帽子)_下": (48, 0, 56, 8),
    "頭(帽子)_右": (32, 8, 40, 16),
    "頭(帽子)_前": (40, 8, 48, 16),
    "頭(帽子)_左": (48, 8, 56, 16),
    "頭(帽子)_後": (56, 8, 64, 16),
}

# =====================
# 第二レイヤー：体（上着）
# =====================
SECOND_LAYER_BODY_FACES = {
    "体(上着)_上": (20, 32, 28, 36),
    "体(上着)_下": (28, 32, 36, 36),
    "体(上着)_右": (16, 36, 20, 48),
    "体(上着)_前": (20, 36, 28, 48),
    "体(上着)_左": (28, 36, 32, 48),
    "体(上着)_後": (32, 36, 40, 48),
}

# =====================
# 第二レイヤー：右腕（袖）
# =====================
SECOND_LAYER_RIGHT_ARM_FACES = {
    "右腕(袖)_上": (44, 32, 48, 36),
    "右腕(袖)_下": (48, 32, 52, 36),
    "右腕(袖)_右": (40, 36, 44, 48),
    "右腕(袖)_前": (44, 36, 48, 48),
    "右腕(袖)_左": (48, 36, 52, 48),
    "右腕(袖)_後": (52, 36, 56, 48),
}
# =====================
# 第二レイヤー：左腕（袖）
# =====================
SECOND_LAYER_LEFT_ARM_FACES = {
    "左腕(袖)_上": (36, 48, 40, 52),
    "左腕(袖)_下": (40, 48, 44, 52),
    "左腕(袖)_右": (32, 52, 36, 64),
    "左腕(袖)_前": (36, 52, 40, 64),
    "左腕(袖)_左": (40, 52, 44, 64),
    "左腕(袖)_後": (44, 52, 48, 64),
}
# =====================
# 第二レイヤー：右脚（ズボン）
# =====================
SECOND_LAYER_RIGHT_LEG_FACES = {
    "右脚(ズボン)_上": (4, 32, 8, 36),
    "右脚(ズボン)_下": (8, 32, 12, 36),
    "右脚(ズボン)_右": (0, 36, 4, 48),
    "右脚(ズボン)_前": (4, 36, 8, 48),
    "右脚(ズボン)_左": (8, 36, 12, 48),
    "右脚(ズボン)_後": (12, 36, 16, 48),
}
# =====================
# 第二レイヤー：左脚（ズボン）
# =====================
SECOND_LAYER_LEFT_LEG_FACES = {
    "左脚(ズボン)_上": (20, 48, 24, 52),
    "左脚(ズボン)_下": (24, 48, 28, 52),
    "左脚(ズボン)_右": (16, 52, 20, 64),
    "左脚(ズボン)_前": (20, 52, 24, 64),
    "左脚(ズボン)_左": (24, 52, 28, 64),
    "左脚(ズボン)_後": (28, 52, 32, 64),
}


# =====================
# GUI
# =====================
root = tk.Tk()
root.title("BlockTailor Studio (Python)")

canvas = tk.Canvas(
    root,
    width=CANVAS_SIZE + MARGIN_X * 2,
    height=CANVAS_SIZE + MARGIN_Y * 2,
    bg="#FFFFFF",
)
canvas.pack(side=tk.LEFT)


# =====================
# 描画処理
# =====================
def can_edit_pixel(x, y):
    if edit_second_layer_only:
        return is_second_layer(x, y)
    return True


def is_second_layer(x, y):
    for x1, y1, x2, y2 in SECOND_LAYER_AREAS:
        if x1 <= x < x2 and y1 <= y < y2:
            return True
    return False


def draw_first_layer_overlay():
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            if not is_second_layer(x, y):
                canvas.create_rectangle(
                    MARGIN_X + x * PIXEL_SIZE,
                    MARGIN_Y + y * PIXEL_SIZE,
                    MARGIN_X + (x + 1) * PIXEL_SIZE,
                    MARGIN_Y + (y + 1) * PIXEL_SIZE,
                    fill="#000000",
                    stipple="gray50",
                    outline="",
                )


# def draw_second_layer_labels():
#    for name, (x1, y1, x2, y2) in SECOND_LAYER_LABELS.items():
#        # 枠
#        canvas.create_rectangle(
#            MARGIN_X + x1 * PIXEL_SIZE,
#            MARGIN_Y + y1 * PIXEL_SIZE,
#            MARGIN_X + x2 * PIXEL_SIZE,
#            MARGIN_Y + y2 * PIXEL_SIZE,
#            outline="#800000",  # 紫（第二レイヤー）
#            width=2,
#        )
#
#        # ラベル文字
#        canvas.create_text(
#            MARGIN_X + (x1 + x2) * PIXEL_SIZE // 2,
#            MARGIN_Y + y1 * PIXEL_SIZE - 10,
#            text=name,
#            fill="#800000",
#            font=("Arial", 9, "bold"),
#        )

# def draw_second_layer_frames():
#    for x1, y1, x2, y2 in SECOND_LAYER_AREAS:
#        canvas.create_rectangle(
#            MARGIN_X + x1 * PIXEL_SIZE,
#            MARGIN_Y + y1 * PIXEL_SIZE,
#            MARGIN_X + x2 * PIXEL_SIZE,
#            MARGIN_Y + y2 * PIXEL_SIZE,
#            outline="#b266ff",  # 紫
#            width=3 if edit_second_layer_only else 1,
#        )


def draw_face_frames(face_dict, color="#800000"):
    for name, (x1, y1, x2, y2) in face_dict.items():
        canvas.create_rectangle(
            MARGIN_X + x1 * PIXEL_SIZE,
            MARGIN_Y + y1 * PIXEL_SIZE,
            MARGIN_X + x2 * PIXEL_SIZE,
            MARGIN_Y + y2 * PIXEL_SIZE,
            outline=color,
            width=1,
        )
        canvas.create_text(
            MARGIN_X + (x1 + x2) * PIXEL_SIZE // 2,
            MARGIN_Y + y1 * PIXEL_SIZE - 6,
            text=name,
            fill=color,
            font=("Arial", 7),
        )


def draw_checkerboard():
    size = PIXEL_SIZE
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            if (x + y) % 2 == 0:
                color = "#b0b0b0"
            else:
                color = "#d0d0d0"
            canvas.create_rectangle(
                MARGIN_X + x * size,
                MARGIN_Y + y * size,
                MARGIN_X + (x + 1) * size,
                MARGIN_Y + (y + 1) * size,
                fill=color,
                outline="",
            )


def redraw():
    canvas.delete("all")

    draw_checkerboard()

    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            # 第二レイヤーOFFなら描かない
            if not show_second_layer and is_second_layer(x, y):
                continue

            r, g, b, a = pixels[y][x]
            if a == 0:
                continue

            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_rectangle(
                MARGIN_X + x * PIXEL_SIZE,
                MARGIN_Y + y * PIXEL_SIZE,
                MARGIN_X + (x + 1) * PIXEL_SIZE,
                MARGIN_Y + (y + 1) * PIXEL_SIZE,
                fill=color,
                outline="",
            )

    # =====================
    # 部位ハイライト
    # =====================
    if current_part == "全体":
        for name, (x1, y1, x2, y2) in PARTS_FULL.items():
            canvas.create_rectangle(
                MARGIN_X + x1 * PIXEL_SIZE,
                MARGIN_Y + y1 * PIXEL_SIZE,
                MARGIN_X + x2 * PIXEL_SIZE,
                MARGIN_Y + y2 * PIXEL_SIZE,
                outline="#191970",
                width=1,
            )
            canvas.create_text(
                MARGIN_X + (x1 + x2) * PIXEL_SIZE // 2,
                MARGIN_Y + y1 * PIXEL_SIZE - 8,
                text=name,
                fill="#191970",
                font=("Arial", 7),
            )
    elif PARTS[current_part]:
        x1, y1, x2, y2 = PARTS[current_part]
        canvas.create_rectangle(
            MARGIN_X + x1 * PIXEL_SIZE,
            MARGIN_Y + y1 * PIXEL_SIZE,
            MARGIN_X + x2 * PIXEL_SIZE,
            MARGIN_Y + y2 * PIXEL_SIZE,
            outline="yellow",
            width=3,
        )

    if edit_second_layer_only:
        draw_first_layer_overlay()

    # 第二レイヤー枠
    # if show_second_layer:
    #    draw_second_layer_frames()
    #    draw_second_layer_labels()  # 大枠（帽子・上着など）

    if show_second_layer and show_fine_faces:
        draw_face_frames(SECOND_LAYER_HEAD_FACES)
        draw_face_frames(SECOND_LAYER_BODY_FACES)
        draw_face_frames(SECOND_LAYER_RIGHT_ARM_FACES)
        draw_face_frames(SECOND_LAYER_LEFT_ARM_FACES)
        draw_face_frames(SECOND_LAYER_RIGHT_LEG_FACES)
        draw_face_frames(SECOND_LAYER_LEFT_LEG_FACES)


# =====================
# マウス描画
# =====================
def draw_pixel(event):
    x = (event.x - MARGIN_X) // PIXEL_SIZE
    y = (event.y - MARGIN_Y) // PIXEL_SIZE

    if not (0 <= x < SKIN_SIZE and 0 <= y < SKIN_SIZE):
        return

    if not can_edit_pixel(x, y):
        return

    pixels[y][x] = current_color
    redraw()


canvas.bind("<Button-1>", draw_pixel)
canvas.bind("<B1-Motion>", draw_pixel)


# =====================
# 保存 / 読み込み
# =====================
def save_skin():
    path = filedialog.asksaveasfilename(
        defaultextension=".png", filetypes=[("PNG Image", "*.png")]
    )
    if not path:
        return

    img = Image.new("RGBA", (SKIN_SIZE, SKIN_SIZE))
    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            img.putpixel((x, y), pixels[y][x])
    img.save(path)


def load_skin():
    path = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
    if not path:
        return

    img = Image.open(path).convert("RGBA")
    if img.size != (SKIN_SIZE, SKIN_SIZE):
        return

    for y in range(SKIN_SIZE):
        for x in range(SKIN_SIZE):
            pixels[y][x] = img.getpixel((x, y))
    redraw()


# =====================
# 色変更（簡易ボタン）
# =====================
def set_color(color):
    global current_color
    current_color = color


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


def toggle_second_layer():
    global show_second_layer
    show_second_layer = not show_second_layer
    redraw()


second_layer_var = tk.BooleanVar(value=True)

tk.Checkbutton(
    toolbar,
    text="第二レイヤー表示",
    variable=second_layer_var,
    command=lambda: (
        globals().__setitem__("show_second_layer", second_layer_var.get()),
        redraw(),
    ),
).pack(fill=tk.X, pady=5)

edit_second_layer_var = tk.BooleanVar(value=False)


def toggle_edit_second_layer():
    global edit_second_layer_only
    edit_second_layer_only = edit_second_layer_var.get()
    redraw()


tk.Checkbutton(
    toolbar,
    text="第二レイヤーのみ編集",
    variable=edit_second_layer_var,
    command=toggle_edit_second_layer,
).pack(fill=tk.X, pady=5)


# =====================
# 部位選択UI
# =====================
def set_part(value):
    global current_part
    current_part = value
    redraw()


part_var = tk.StringVar(value=current_part)

part_menu = tk.OptionMenu(toolbar, part_var, *PARTS.keys(), command=set_part)
part_menu.pack(fill=tk.X, pady=10)

# =====================
# 起動
# =====================
redraw()
root.mainloop()
