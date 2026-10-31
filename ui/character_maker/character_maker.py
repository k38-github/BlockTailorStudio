import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image


class CharacterMaker(tk.Toplevel):

    TABS = ["skin", "face", "hair", "clothes", "accessory"]

    def __init__(self, parent, controller, template_manager):
        super().__init__(parent)

        self.title("Character Maker")
        self.geometry("900x600")

        self.controller = controller
        self.template_manager = template_manager

        # 状態
        self.current_tab = "skin"
        self.selected = {tab: None for tab in self.TABS}

        # ===== レイアウト =====
        self.build_layout()

        # 初期描画
        self.build_tabs()
        self.build_items()
        self.build_preview()
        self.build_bottom()

        self.after(100, self.ensure_preview_open)

    # =========================
    # レイアウト
    # =========================
    def build_layout(self):

        # 上：タブ
        self.tab_frame = tk.Frame(self, height=40)
        self.tab_frame.pack(fill="x")

        # 中央
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # 左：一覧
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # 右：2Dプレビュー
        self.preview_frame = tk.Frame(self.main_frame, width=300, bg="#222")
        self.preview_frame.pack(side="left", fill="y")

        # 下：ボタン
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill="x")

    # =========================
    # タブUI
    # =========================
    def build_tabs(self):

        for widget in self.tab_frame.winfo_children():
            widget.destroy()

        for tab in self.TABS:
            btn = tk.Button(
                self.tab_frame,
                text=tab.capitalize(),
                command=lambda t=tab: self.select_tab(t),
                relief="sunken" if tab == self.current_tab else "raised",
            )
            btn.pack(side="left", padx=5, pady=5)

    def select_tab(self, tab):
        self.current_tab = tab
        self.build_tabs()
        self.build_items()

    # =========================
    # 一覧UI（スクロール付き）
    # =========================
    def build_items(self):

        for widget in self.left_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.left_frame)
        scrollbar = ttk.Scrollbar(
            self.left_frame, orient="vertical", command=canvas.yview
        )
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ▼ テンプレ取得
        items = self.get_items(self.current_tab)

        self.tk_images = []  # ←重要：参照保持

        for i, template in enumerate(items):

            frame = tk.Frame(scroll_frame, bd=2, relief="solid")

            # ▼ 画像縮小（サムネ化）
            img = template["image"].copy()
            img.thumbnail((64, 64))

            tk_img = ImageTk.PhotoImage(img)
            self.tk_images.append(tk_img)  # ←消えないように保持

            btn = tk.Button(
                frame, image=tk_img, command=lambda t=template: self.select_item(t)
            )
            btn.pack()

            # ▼ 選択状態
            if self.selected[self.current_tab] == template:
                frame.config(bg="yellow")

            frame.grid(row=i // 4, column=i % 4, padx=5, pady=5)

    def select_item(self, item):
        self.selected[self.current_tab] = item
        self.build_items()
        self.update_preview()

    # =========================
    # プレビュー
    # =========================
    def build_preview(self):

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.preview_label = tk.Label(self.preview_frame, bg="#222")
        self.preview_label.pack(expand=True)

        self.update_preview()  # ← 初期表示

    def update_preview(self):

        preview_model = self.create_preview_model()

        from skin_maker.skin_composer import SkinComposer

        composer = SkinComposer(preview_model)

        # 選択中テンプレだけ適用
        templates = [t for t in self.selected.values() if t is not None]
        composer.apply_templates(templates)

        # 画像取得（SkinModelに応じて）
        img = preview_model.get_image()

        img_2d = img.resize((512, 512), Image.NEAREST)
        self.tk_preview = ImageTk.PhotoImage(img_2d)
        self.preview_label.config(image=self.tk_preview)

        if hasattr(self.controller, "update_3d_preview"):
            self.controller.update_3d_preview(img)

    # =========================
    # 下ボタン
    # =========================
    def build_bottom(self):

        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        apply_btn = tk.Button(
            self.bottom_frame, text="適用", command=self.apply_character
        )
        apply_btn.pack(side="right", padx=10, pady=10)

        cancel_btn = tk.Button(
            self.bottom_frame, text="キャンセル", command=self.destroy
        )
        cancel_btn.pack(side="right")

    def apply_character(self):

        templates = [
            self.selected[k]
            for k in ["skin", "clothes", "hair", "accessory"]
            if self.selected.get(k)
        ]

        # 親に渡す
        if hasattr(self.controller, "apply_character"):
            self.controller.apply_character(templates)

        self.destroy()

    # =========================
    # ダミーデータ
    # =========================
    def get_items(self, category):
        return self.template_manager.templates.get(category, [])

    def create_preview_model(self):
        from core.skin_model import SkinModel

        return SkinModel()

    def ensure_preview_open(self):

        if (
            not hasattr(self.controller, "preview_dialog")
            or not self.controller.preview_dialog.winfo_exists()
        ):
            self.controller.start_preview()
