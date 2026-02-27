import tkinter as tk
from tkinter import filedialog

from canvas.skin_canvas import SkinCanvas
from core.skin_file_manager import SkinFileManager
from core.skin_model import SkinModel
from tools.tool_manager import ToolManager
from ui.color_controller import ColorController
from ui.color_palette import ColorPalette
from ui.color_picker import ColorPicker
from ui.file_panel import FilePanel
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

        self.file_panel = None
        self.file_manager = None

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
        self.file_panel = FilePanel(
            toolbar, on_save=self.save_skin, on_load=self.load_skin
        )
        self.file_panel.pack()
        self.file_manager = SkinFileManager(self.model)

    # =====================
    # 保存 / 読み込み
    # =====================
    def save_skin(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return
        self.file_manager.save(path)

    def load_skin(self):
        path = filedialog.askopenfilename(filetypes=[("Minecraft Skin", "*.png")])
        if not path:
            return

        if self.file_manager.load(path):
            self.canvas.redraw()

    def set_part(self, value):
        self.current_part = value

    def run(self):
        self.root.mainloop()
