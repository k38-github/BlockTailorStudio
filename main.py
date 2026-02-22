import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser

from PIL import Image
from typing import Optional

from ui.color_controller import ColorController
from ui.color_picker import ColorPicker
from ui.rgb_bars import RGBBars
from ui.user_palette import UserPalette


class BlockTailorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BlockTailor Studio (Python)")
        self.root.grid_columnconfigure(0, weight=1)  # 左は伸びる
        self.root.grid_columnconfigure(1, weight=0)  # 右は固定
        self.root.grid_rowconfigure(0, weight=1)

        # =====================
        # 定数
        # =====================
        self.canvas = None
        self.canvas_frame = None

        self.SKIN_SIZE = 64
        self.PIXEL_SIZE = 10
        self.MARGIN = 20
        self.CANVAS_SIZE = self.SKIN_SIZE * self.PIXEL_SIZE + self.MARGIN * 2

        self.WHEEL_SIZE = 160
        self.SQUARE_SIZE = 160
        self.RING_WIDTH = 14

        self.PALETTE_CELL_SIZE = 24

        self.TRANSPARENT = (0, 0, 0, 0)

        self.TOOLBAR_WIDTH = 350
        self.scroll_canvas = None
        self.scrollbar = None

        self.current_part = "全体"
        self.edit_second_layer_only = False
        self.last_drawn = None
        self.tool_mode = "draw"  # "draw" or "eyedropper"

        self.toolbar_container = None

        self.palette_buttons = {}
        self.USER_PALETTE_SIZE = 36
        self.user_palette = [None] * self.USER_PALETTE_SIZE
        self.user_palette_buttons = []

        self.color_code_label = None

        self.edit_second_layer_var = None

        # =====================
        # クラス定義
        # =====================
        self.controller = None
        self.color_picker = None
        self.rgb = None
        self.color_preview = None

        # =====================
        # データ
        # =====================
        # 第一スキンレイヤーデータ
        self.base_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]

        # 第二スキンレイヤーデータ
        self.overlay_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]

        # ピクセル用idマップ
        self.pixel_items: list[list[Optional[int]]] = [
            [None for _ in range(self.SKIN_SIZE)] for _ in range(self.SKIN_SIZE)
        ]

        # =====================
        # マイクラ部位定義
        # =====================
        # =====================
        # 第一スキンレイヤー範囲
        # =====================
        self.FIRST_LAYER_AREAS = {
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
        self.SECOND_LAYER_AREAS = {
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

        self.setup_ui()

    def setup_ui(self):
        # =====================
        # Canvas
        # =====================
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.CANVAS_SIZE + self.MARGIN * 2,
            height=self.CANVAS_SIZE + self.MARGIN * 2,
            bg="#FFFFFF",
        )
        self.canvas.pack(expand=True)

        self.canvas.bind("<Button-1>", self.draw_pixel)
        self.canvas.bind("<B1-Motion>", self.draw_pixel)
        self.canvas.bind("<Button-3>", self.pick_color)
        self.canvas.bind("<ButtonRelease-1>", self.reset_last_drawn)

        # =====================
        # 📦 toolbar
        # =====================
        self.toolbar_container = tk.Frame(self.root, width=self.TOOLBAR_WIDTH)
        self.toolbar_container.grid(row=0, column=1, sticky="ns")
        self.toolbar_container.grid_propagate(False)  # 幅固定

        # スクロール用Canvas
        self.scroll_canvas = tk.Canvas(self.toolbar_container, highlightthickness=0)
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        # スクロールバー
        self.scrollbar = tk.Scrollbar(
            self.toolbar_container, orient="vertical", command=self.scroll_canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # 伸縮設定
        self.toolbar_container.grid_rowconfigure(0, weight=1)
        self.toolbar_container.grid_columnconfigure(0, weight=1)

        # 中身のFrame
        toolbar = tk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=toolbar, anchor="nw")
        self.scroll_canvas.configure(width=300)

        toolbar.bind("<Configure>", self.update_scrollregion)

        self._enable_parent_scroll()

        # =========================
        # 🎨 カラーセクション
        # =========================
        color_section = tk.LabelFrame(toolbar, text="🎨 カラー", padx=5, pady=5)
        color_section.pack(fill="x", pady=5)

        # カラーサークル
        self.controller = ColorController()
        self.color_picker = ColorPicker(
            color_section, self.WHEEL_SIZE, self.RING_WIDTH, self.controller
        )
        self.color_picker.pack()
        self.color_picker.draw_hue_ring()
        self.color_picker.draw_hue_cursor()
        self.color_picker.draw_sv_square()
        self.color_picker.draw_sv_cursor()

        # RGBバー
        self.rgb = RGBBars(color_section, controller=self.controller)

        # カラーパレット
        tk.Button(color_section, text="カラーパレット", command=self.choose_color).pack(
            fill="x", pady=5
        )

        # =========================
        # 👤 ユーザーパレット
        # =========================
        self.user_palette = UserPalette(
            color_section,
            controller=self.controller,
            slot_size=256,
            cell_size=self.PALETTE_CELL_SIZE,
        )

        # ===== パレット用ボタン =====
        palette_io_frame = tk.Frame(color_section)
        palette_io_frame.pack(fill="x", pady=2)

        # ===== パレット登録/削除 =====
        tk.Button(
            palette_io_frame,
            text="登録",
            command=self.user_palette.register_current_color,
        ).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(
            palette_io_frame, text="削除", command=self.user_palette.clear_selected
        ).pack(side="left", expand=True, fill="x", padx=2)

        # ===== パレット保存/読込 =====
        tk.Button(
            palette_io_frame, text="パレット保存", command=self.user_palette.save
        ).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(
            palette_io_frame, text="パレット読込", command=self.user_palette.load
        ).pack(side="left", expand=True, fill="x", padx=2)

        # =========================
        # 🖌 ツールセクション
        # =========================
        tool_section = tk.LabelFrame(toolbar, text="🖌 ツール", padx=5, pady=5)
        tool_section.pack(fill="x", pady=5)

        tool_row = tk.Frame(tool_section)
        tool_row.pack(fill="x")

        # ペン
        tk.Button(tool_row, text="ペン", command=lambda: self.set_tool("draw")).pack(
            fill="x"
        )

        # スポイト
        tk.Button(
            tool_row, text="スポイト", command=lambda: self.set_tool("eyedropper")
        ).pack(fill="x")

        # 消しゴム
        tk.Button(
            tool_row,
            text="消しゴム",
            command=lambda: self.controller.set_color(self.TRANSPARENT),
        ).pack(fill="x")

        # =========================
        # ⚙ レイヤーセクション
        # =========================
        layer_section = tk.LabelFrame(toolbar, text="⚙ レイヤー", padx=5, pady=5)
        layer_section.pack(fill="x", pady=5)
        # 第二レイヤー編集
        self.edit_second_layer_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            layer_section,
            text="第二レイヤー編集",
            variable=self.edit_second_layer_var,
            command=self.toggle_edit_second_layer,
        ).pack(anchor="w")

        # =========================
        # 💾 ファイルセクション
        # =========================
        file_section = tk.LabelFrame(toolbar, text="💾 ファイル", padx=5, pady=5)
        file_section.pack(fill="x", pady=5)

        # 保存
        tk.Button(file_section, text="保存", command=self.save_skin).pack(
            fill="x", pady=2
        )

        # 読み込み
        tk.Button(file_section, text="読込", command=self.load_skin).pack(
            fill="x", pady=2
        )

        # パーツ表示
        part_var = tk.StringVar(value=self.current_part)
        part_menu_item = {"全体": None, **self.FIRST_LAYER_AREAS}
        part_menu = tk.OptionMenu(
            toolbar, part_var, *part_menu_item.keys(), command=self.set_part
        )
        part_menu.pack(fill="x", pady=10)

        self.redraw()

    # サイズ変更時にスクロール範囲更新
    def update_scrollregion(self, event=None):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _enable_parent_scroll(self):

        def _on_mousewheel(event):
            if hasattr(event, "delta") and event.delta:
                delta = int(-1 * (event.delta / 120))
            else:
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
                else:
                    delta = 0

            self.scroll_canvas.yview_scroll(delta, "units")
            return "break"

        self.scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.scroll_canvas.bind_all("<Button-4>", _on_mousewheel)
        self.scroll_canvas.bind_all("<Button-5>", _on_mousewheel)

    # =====================
    # 描画処理
    # =====================
    def is_first_layer(self, x, y):
        for x1, y1, x2, y2 in self.FIRST_LAYER_AREAS.values():
            if x1 <= x < x2 and y1 <= y < y2:
                return True
        return False

    def is_second_layer(self, x, y):
        for x1, y1, x2, y2 in self.SECOND_LAYER_AREAS.values():
            if x1 <= x < x2 and y1 <= y < y2:
                return True
        return False

    def can_edit_pixel(self, x, y):
        # 第二レイヤーのみ編集モード
        if not self.edit_second_layer_only:
            return self.is_first_layer(x, y)
        else:
            return self.is_second_layer(x, y)

    def draw_layer_invalid_mask(self):
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                if not self.edit_second_layer_only:
                    if not self.is_first_layer(x, y):
                        self.canvas.create_rectangle(
                            self.MARGIN + x * self.PIXEL_SIZE,
                            self.MARGIN + y * self.PIXEL_SIZE,
                            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                            fill="#000000",
                            stipple="gray50",
                            outline="",
                        )
                else:
                    if not self.is_second_layer(x, y):
                        self.canvas.create_rectangle(
                            self.MARGIN + x * self.PIXEL_SIZE,
                            self.MARGIN + y * self.PIXEL_SIZE,
                            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                            fill="#000000",
                            stipple="gray50",
                            outline="",
                        )

    def draw_face_frames(self, face_dict, color="#800000"):
        for name, (x1, y1, x2, y2) in face_dict.items():
            self.canvas.create_rectangle(
                self.MARGIN + x1 * self.PIXEL_SIZE,
                self.MARGIN + y1 * self.PIXEL_SIZE,
                self.MARGIN + x2 * self.PIXEL_SIZE,
                self.MARGIN + y2 * self.PIXEL_SIZE,
                outline=color,
                width=1,
            )
            self.canvas.create_text(
                self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                self.MARGIN + y1 * self.PIXEL_SIZE - 6,
                text=name,
                fill=color,
                font=("Arial", 7),
            )

    def draw_checkerboard(self):
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                if (x + y) % 2 == 0:
                    color = "#b0b0b0"
                else:
                    color = "#d0d0d0"
                self.canvas.create_rectangle(
                    self.MARGIN + x * self.PIXEL_SIZE,
                    self.MARGIN + y * self.PIXEL_SIZE,
                    self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                    self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                    fill=color,
                    outline="",
                )

    def draw_frameline(self):
        if not self.edit_second_layer_only:
            for name, (x1, y1, x2, y2) in self.FIRST_LAYER_AREAS.items():
                self.canvas.create_rectangle(
                    self.MARGIN + x1 * self.PIXEL_SIZE,
                    self.MARGIN + y1 * self.PIXEL_SIZE,
                    self.MARGIN + x2 * self.PIXEL_SIZE,
                    self.MARGIN + y2 * self.PIXEL_SIZE,
                    outline="#191970",
                    width=1,
                )
                self.canvas.create_text(
                    self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                    self.MARGIN + y1 * self.PIXEL_SIZE - 8,
                    text=name,
                    fill="#191970",
                    font=("Arial", 7),
                )

        else:
            for name, (x1, y1, x2, y2) in self.SECOND_LAYER_AREAS.items():
                self.canvas.create_rectangle(
                    self.MARGIN + x1 * self.PIXEL_SIZE,
                    self.MARGIN + y1 * self.PIXEL_SIZE,
                    self.MARGIN + x2 * self.PIXEL_SIZE,
                    self.MARGIN + y2 * self.PIXEL_SIZE,
                    outline="#191970",
                    width=1,
                )
                self.canvas.create_text(
                    self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                    self.MARGIN + y1 * self.PIXEL_SIZE - 8,
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

    def draw_pixels(self, x, y):
        if not self.edit_second_layer_only:
            r, g, b, a = self.base_pixels[y][x]
        else:
            r, g, b, a = self.overlay_pixels[y][x]

        # すでに描画済みなら削除
        if self.pixel_items[y][x] is not None:
            self.canvas.delete(self.pixel_items[y][x])
            self.pixel_items[y][x] = None

        # 透明なら何も描かない（＝消しゴム）
        if a == 0:
            return

        self.pixel_items[y][x] = self.canvas.create_rectangle(
            self.MARGIN + x * self.PIXEL_SIZE,
            self.MARGIN + y * self.PIXEL_SIZE,
            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
            fill=f"#{r:02x}{g:02x}{b:02x}",
            outline="",
        )

    def redraw(self):
        self.canvas.delete("all")
        self.draw_checkerboard()
        self.draw_frameline()
        self.draw_layer_invalid_mask()

        # pixel_items をリセット
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                self.pixel_items[y][x] = None
                self.draw_pixels(x, y)

    # =====================
    # マウス描画
    # =====================
    def draw_pixel(self, event):
        x = (event.x - self.MARGIN) // self.PIXEL_SIZE
        y = (event.y - self.MARGIN) // self.PIXEL_SIZE

        if not (0 <= x < self.SKIN_SIZE and 0 <= y < self.SKIN_SIZE):
            return

        # ★ スポイトモード
        if self.tool_mode == "eyedropper":
            self.pick_color(event)
            self.set_tool("draw")  # 自動でペンに戻す
            return

        if not self.can_edit_pixel(x, y):
            return

        if self.last_drawn == (x, y):
            return

        self.last_drawn = (x, y)

        r, g, b, a = self.controller.get_color()

        if self.is_first_layer(x, y):
            self.base_pixels[y][x] = (r, g, b, a)
        elif self.is_second_layer(x, y):
            self.overlay_pixels[y][x] = (r, g, b, a)

        self.draw_pixels(x, y)

    def reset_last_drawn(self, event):
        self.last_drawn = None

    # =====================
    # 保存 / 読み込み
    # =====================
    def save_skin(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return

        img = Image.new("RGBA", (self.SKIN_SIZE, self.SKIN_SIZE))
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                bp = self.base_pixels[y][x]
                op = self.overlay_pixels[y][x]
                img.putpixel((x, y), op if op[3] > 0 else bp)

        img.save(path)

    def load_skin(self):
        path = filedialog.askopenfilename(filetypes=[("Minecraft Skin", "*.png")])
        if not path:
            return

        img = Image.open(path).convert("RGBA")
        if img.size != (self.SKIN_SIZE, self.SKIN_SIZE):
            print("64x64スキン以外は非対応")
            return

        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                pixel = img.getpixel((x, y))
                if self.is_second_layer(x, y):
                    self.overlay_pixels[y][x] = pixel
                else:
                    self.base_pixels[y][x] = pixel

        self.redraw()

    # =====================
    # 色関係
    # =====================
    def choose_color(self):
        r, g, b, a = self.controller.get_color()

        rgb, _ = colorchooser.askcolor(color=f"#{r:02x}{g:02x}{b:02x}")

        if rgb is None:
            return

        r, g, b = map(int, rgb)
        self.controller.set_color((r, g, b, a))

    def pick_color(self, event):
        x = (event.x - self.MARGIN) // self.PIXEL_SIZE
        y = (event.y - self.MARGIN) // self.PIXEL_SIZE

        if not (0 <= x < self.SKIN_SIZE and 0 <= y < self.SKIN_SIZE):
            return

        # 表示優先順位：第二 → 第一
        op = self.overlay_pixels[y][x]
        if op[3] > 0:
            self.controller.set_color(op)
            return

        bp = self.base_pixels[y][x]
        if bp[3] > 0:
            self.controller.set_color(bp)
            return

        # 何もなければ透明（任意）
        self.controller.set_color(self.TRANSPARENT)

    def set_tool(self, mode):
        self.tool_mode = mode

    # =====================
    # 第二レイヤー
    # =====================
    def toggle_edit_second_layer(self):
        self.edit_second_layer_only = self.edit_second_layer_var.get()
        self.redraw()

    # =====================
    # 部位選択UI
    # =====================
    def set_part(self, value):
        self.current_part = value

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BlockTailorApp()
    app.run()
