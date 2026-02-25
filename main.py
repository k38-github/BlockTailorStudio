import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL.ImageOps import expand

from canvas import skin_canvas
from canvas.skin_canvas import SkinCanvas
from core.skin_model import SkinModel
from tools.tool_manager import ToolManager
from ui.color_controller import ColorController
from ui.color_palette import ColorPalette
from ui.color_picker import ColorPicker
from ui.palette_panel import PaletteIOPanel
from ui.rgb_bars import RGBBars
from ui.scrollable_frame import ScrollableFrame
from ui.toolbar_view import ToolbarView
from ui.tools_panel import ToolsPanel
from ui.user_palette import UserPalette
from core.skin_areas import FIRST_LAYER_AREAS, SECOND_LAYER_AREAS


class BlockTailorApp:
    def __init__(self):

        # =====================
        # 定数
        # =====================
        self.WHEEL_SIZE = 160
        self.SQUARE_SIZE = 160
        self.RING_WIDTH = 14

        self.first_layer_areas = FIRST_LAYER_AREAS
        self.second_layer_areas = SECOND_LAYER_AREAS

        self.current_part = "全体"

        # =====================
        # クラス定義
        # =====================
        self.toolbar = None
        self.model = None

        self.controller = None
        self.color_picker = None
        self.rgb = None
        self.color_preview = None
        self.color_palette = None
        self.user_palette = None
        self.palette_panel = None

        self.tool_manager = None
        self.tools_panel = None

        self.canvas = None
        self.toolbar_view = None

        # =====================
        # 初期セットアップ
        # =====================
        self.root = tk.Tk()
        self.root.title("BlockTailor Studio (Python)")
        self.root.grid_columnconfigure(0, weight=1)  # 左は伸びる
        self.root.grid_columnconfigure(1, weight=0)  # 右は固定
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):

        # =====================
        # 📦 toolbar
        # =====================
        self.toolbar = ScrollableFrame(self.root)
        self.toolbar.grid(row=0, column=1, sticky="ns")
        toolbar = self.toolbar.content

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

        # RGBバー
        self.rgb = RGBBars(color_section, controller=self.controller)
        self.rgb.pack(fill="x", pady=10)

        # カラーパレット
        self.color_palette = ColorPalette(color_section, self.controller)
        self.color_palette.pack()

        # ユーザーパレット
        self.user_palette = UserPalette(
            color_section,
            self.controller,
        )
        self.user_palette.pack(fill="both", expand=True)

        # パレット用ボタン
        self.palette_panel = PaletteIOPanel(color_section, self.user_palette)
        self.palette_panel.pack(fill="x", pady=5)

        # =========================
        # 🖌 ツールセクション
        # =========================
        self.tool_manager = ToolManager()
        self.tool_manager.set_tool("pen")

        self.tools_panel = ToolsPanel(toolbar, self.tool_manager)
        self.tools_panel.pack(fill="x")

        # =========================
        # スキンキャンバスセクション
        # =========================
        self.model = SkinModel()
        self.canvas = SkinCanvas(
            self.root, self.model, self.controller, self.tool_manager
        )

        # =========================
        # ⚙ レイヤーセクション
        # =========================
        self.toolbar_view = ToolbarView(toolbar, self.model, self.canvas)

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
        part_menu_item = {"全体": None, **self.first_layer_areas}
        part_menu = tk.OptionMenu(
            toolbar, part_var, *part_menu_item.keys(), command=self.set_part
        )
        part_menu.pack(fill="x", pady=10)
        skin_canvas.SkinCanvas.redraw(self.canvas)

    # =====================
    # 保存 / 読み込み
    # =====================
    def save_skin(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return

        img = Image.new("RGBA", (self.model.SKIN_SIZE, self.model.SKIN_SIZE))
        for y in range(self.model.SKIN_SIZE):
            for x in range(self.model.SKIN_SIZE):
                bp = self.model.base_pixels[y][x]
                op = self.model.overlay_pixels[y][x]
                img.putpixel((x, y), op if op[3] > 0 else bp)

        img.save(path)

    def load_skin(self):
        path = filedialog.askopenfilename(filetypes=[("Minecraft Skin", "*.png")])
        if not path:
            return

        img = Image.open(path).convert("RGBA")
        if img.size != (self.model.SKIN_SIZE, self.model.SKIN_SIZE):
            print("64x64スキン以外は非対応")
            return

        for y in range(self.model.SKIN_SIZE):
            for x in range(self.model.SKIN_SIZE):
                pixel = img.getpixel((x, y))
                if self.model.is_second_layer(x, y):
                    self.model.overlay_pixels[y][x] = pixel
                else:
                    self.model.base_pixels[y][x] = pixel

        skin_canvas.SkinCanvas.redraw(self.canvas)

    def set_part(self, value):
        self.current_part = value

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BlockTailorApp()
    app.run()
