import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from canvas.canvas_scroll_frame import CanvasScrollFrame
from canvas.skin_canvas import SkinCanvas
from controller.skin_controller import SkinController
from core.skin_file_manager import SkinFileManager
from core.skin_model import SkinModel
from skin_maker.skin_maker import SkinMaker
from skin_maker.template_manager import TemplateManager
from tools.tool_manager import ToolManager
from ui.app_toolbar import AppToolbar
from ui.color_controller import ColorController
from ui.color_palette import ColorPalette
from ui.color_picker import ColorPicker
from ui.dialogs.skin_type_dialog import SkinTypeDialog
from ui.menu_bar import MenuBar
from ui.palette_panel import PaletteIOPanel
from ui.rgb_bars import RGBBars
from ui.scrollable_frame import ScrollableFrame
from ui.toolbar_view import ToolbarView
from ui.tools_panel import ToolsPanel
from ui.user_palette import UserPalette
from core.skin_areas import FIRST_LAYER_AREAS, SECOND_LAYER_AREAS
from skin_maker.skin_composer import SkinComposer


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
        self.menu_bar = None
        self.app_toolbar = None
        self.toolbar = None
        self.model = None

        self.color_controller = None
        self.color_picker = None
        self.rgb = None
        self.color_preview = None
        self.color_palette = None
        self.user_palette = None
        self.palette_panel = None

        self.part_label = None
        self.skin_controller = None
        self.tool_manager = None
        self.tools_panel = None

        self.history_panel = None

        self.canvas_area = None
        self.canvas = None
        self.toolbar_view = None

        self.file_panel = None
        self.file_manager = None

        # =====================
        # スキンメーカー
        # =====================
        self.template_manager = None
        self.skin_composer = None
        self.skin_maker = None

        # =====================
        # 初期セットアップ
        # =====================
        self.root = tk.Tk()
        self.root.title("BlockTailor Studio")
        self.root.geometry("1020x900")
        self.root.grid_columnconfigure(0, weight=1)  # 左は伸びる
        self.root.grid_columnconfigure(1, weight=0)  # 右は固定
        self.root.grid_rowconfigure(0, weight=0)  # toolbar
        self.root.grid_rowconfigure(1, weight=1)  # canvas
        self.root.grid_rowconfigure(2, weight=0)  # status

        self.setup_ui()

    def setup_ui(self):
        # =====================
        # モデル
        # =====================
        self.model = SkinModel()

        # =====================
        # スキンメーカー
        # =====================
        self.template_manager = TemplateManager()

        self.skin_composer = SkinComposer(self.model)

        self.skin_maker = SkinMaker(self.template_manager, self.skin_composer)

        # =====================
        # カラー
        # =====================
        self.color_controller = ColorController()

        # =====================
        # コントローラ
        # =====================
        self.skin_controller = SkinController(self.model, self.color_controller)

        # =====================
        # メニューバー
        # =====================
        self.menu_bar = MenuBar(self.root, self)

        # =====================
        # 🧰 アプリツールバー
        # =====================
        self.app_toolbar = AppToolbar(
            self.root,
            on_save=self.save_skin,
            on_load=self.load_skin,
            on_undo=self.skin_controller.undo,
            on_redo=self.skin_controller.redo,
            on_3dview=self.start_preview,
        )
        self.app_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # =====================
        # 📦 ツールバー
        # =====================
        self.toolbar = ScrollableFrame(self.root, width=320)
        self.toolbar.grid(row=1, column=1, sticky="ns")
        toolbar = self.toolbar.content

        # =========================
        # 🎨 カラーセクション
        # =========================
        color_section = tk.LabelFrame(toolbar, text="🎨 カラー", padx=5, pady=5)
        color_section.pack(fill="x", pady=5)

        # カラーサークル
        self.color_picker = ColorPicker(
            color_section, self.WHEEL_SIZE, self.RING_WIDTH, self.color_controller
        )
        self.color_picker.pack()

        # RGBバー
        self.rgb = RGBBars(color_section, controller=self.color_controller)
        self.rgb.pack(fill="x", pady=10)

        # カラーパレット
        self.color_palette = ColorPalette(color_section, self.color_controller)
        self.color_palette.pack()

        # ユーザーパレット
        self.user_palette = UserPalette(
            color_section,
            self.color_controller,
        )
        self.user_palette.pack(fill="both", expand=True)

        # パレット用ボタン
        self.palette_panel = PaletteIOPanel(color_section, self.user_palette)
        self.palette_panel.pack(fill="x", pady=5)

        # =========================
        # 🖌 ツールセクション
        # =========================
        self.tool_manager = ToolManager()
        self.tools_panel = ToolsPanel(toolbar, self.tool_manager)
        self.tools_panel.pack(fill="x")

        # =========================
        # スキンキャンバスセクション
        # =========================
        self.canvas_area = CanvasScrollFrame(self.root)
        self.canvas_area.grid(row=1, column=0, sticky="nsew")

        self.canvas = SkinCanvas(
            self.canvas_area.content,
            self.model,
            self.skin_controller,
            self.tool_manager,
            self,
        )
        self.canvas.pack()

        self.part_label = tk.Label(
            self.root, text="Part : 全体", anchor="w", relief="sunken", padx=5
        )
        self.part_label.grid(row=2, column=0, sticky="ew")

        self.skin_controller.set_on_change(self.canvas.redraw_all)

        self.root.bind("<Control-z>", lambda e: self.skin_controller.undo())
        self.root.bind("<Control-y>", lambda e: self.skin_controller.redo())

        # =========================
        # ⚙ レイヤーセクション
        # =========================
        self.toolbar_view = ToolbarView(toolbar, self.model, self.canvas)

        # =====================
        # スキンメーカーセクション
        # =====================
        skin_maker_section = tk.LabelFrame(toolbar, text="🧬 スキンメーカー")
        skin_maker_section.pack(fill="x", pady=5)

        for category, templates in self.template_manager.templates.items():

            frame = tk.LabelFrame(skin_maker_section, text=category)
            frame.pack(fill="x", pady=2)

            for template in templates:

                btn = tk.Button(
                    frame,
                    text=template["name"],
                    command=lambda c=category, t=template: self.select_template(c, t),
                )

                btn.pack(side="left", padx=2, pady=2)

        # =====================
        # ファイルセクション
        # =====================
        self.file_manager = SkinFileManager(self.model)

    # =====================
    # 新規作成 / 保存 / 読み込み
    # =====================
    def new_skin(self):

        if not messagebox.askyesno(
            "New Skin", "現在の作業内容を破棄して新規作成しますか？"
        ):
            return

        dialog = SkinTypeDialog(self.root)
        skin_type = dialog.result

        if skin_type is None:
            return

        self.skin_controller.new_skin(skin_type)
        self.canvas.redraw_all()

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

        if self.current_part == value:
            return

        self.current_part = value
        self.part_label.config(text=f"Part : {value}")

    def select_template(self, category, template):
        self.skin_maker.select(category, template)
        self.skin_maker.build()
        self.canvas.redraw_all()

    def start_preview(self):

        img = self.model.export_image()

        if hasattr(self, "preview_dialog") and self.preview_dialog.winfo_exists():
            self.preview_dialog.update_texture(img)
            self.preview_dialog.lift()
            return

        from preview.preview_dialog import PreviewDialog

        self.preview_dialog = PreviewDialog(self.root, img)

    def run(self):
        self.root.mainloop()
