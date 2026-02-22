import json
import tkinter as tk
from tkinter import filedialog, messagebox


class UserPalette:
    def __init__(self, parent, controller, slot_size=256, cell_size=24):
        self.parent = parent
        self.controller = controller

        self.USER_PALETTE_SIZE = slot_size
        self.PALETTE_CELL_SIZE = cell_size

        self.SELECTION_COLOR = "#2d6ea3"

        self.VISIBLE_ROWS = 4
        self.VISIBLE_COLS = 12
        self.VISIBLE_WIDTH = self.PALETTE_CELL_SIZE * self.VISIBLE_COLS
        self.VISIBLE_HEIGHT = self.PALETTE_CELL_SIZE * self.VISIBLE_ROWS

        self.palette = [None] * self.USER_PALETTE_SIZE
        self.buttons = []

        self.next_overwrite_index = 0
        self.selected_index = None

        # コンテナ
        border = tk.Frame(parent, bg="#7ca7cb")
        border.pack(pady=5)
        container = tk.Frame(border, bg="white")
        container.pack(padx=1, pady=1)

        # Canvas
        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 中身フレーム（セルを置く場所）
        self.frame = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window(1, 1, anchor="nw", window=self.frame)

        self._build()
        # self._bind_mousewheel()
        self._enable_palette_scroll()

    def _build(self):
        for i in range(self.USER_PALETTE_SIZE):
            cell = self._create_cell(i)
            cell.grid(row=i // self.VISIBLE_COLS, column=i % self.VISIBLE_COLS)
            self.buttons.append(cell)

        self.frame.update_idletasks()

        # スクロール範囲は中身全体
        width = self.frame.winfo_width()
        height = self.frame.winfo_height()
        self.canvas.config(scrollregion=(0, 0, width + 2, height + 2))

        # 表示サイズは固定（3〜4行分）
        self.canvas.config(width=self.VISIBLE_WIDTH, height=self.VISIBLE_HEIGHT)

    def _create_cell(self, index):
        size = self.PALETTE_CELL_SIZE

        canvas = tk.Canvas(
            self.frame,
            width=size,
            height=size,
            highlightthickness=0,
            bd=1,
            relief="flat",
            takefocus=0,
        )

        # ▼ チェッカー（backgroundタグ）
        self.draw_checker(canvas, 0, 0, size, cell=6)

        # ▼ 色表示（上に乗る）
        canvas.create_rectangle(
            0,
            0,
            size,
            size,
            fill="",
            outline="",
            tags="color",
        )

        # ▼ 選択枠（最上位）
        canvas.create_rectangle(
            1,
            1,
            size,
            size,
            outline="white",
            width=1,
            tags="selection",
            state="hidden",
        )

        canvas.bind("<Button-1>", lambda e, i=index: self.select(i))
        canvas.bind("<Button-3>", lambda e, i=index: self.register(i))
        canvas.bind("<Double-Button-1>", lambda e, i=index: self.clear(i))

        return canvas

    def draw_checker(self, canvas, x, y, size, cell=8):
        colors = ["#b0b0b0", "#d0d0d0"]

        for row in range(0, size, cell):
            for col in range(0, size, cell):
                color = colors[((row // cell) + (col // cell)) % 2]
                canvas.create_rectangle(
                    x + col,
                    y + row,
                    x + col + cell,
                    y + row + cell,
                    fill=color,
                    outline="",
                )

    def select(self, index):
        self.selected_index = index
        self.update_selection()

        color = self.palette[index]
        if color is None:
            return

        r, g, b = color
        self.controller.set_color((r, g, b, 255))

    def register(self, index):
        r, g, b, _ = self.controller.get_color()
        self.palette[index] = (r, g, b)
        self.update_button(index)

    def clear_selected(self):
        if self.selected_index is None:
            return

        self.clear(self.selected_index)

    def clear(self, index):
        # 空セルなら何もしない
        if self.palette[index] is None:
            return

        # データ削除
        self.palette[index] = None

        # 表示更新
        self.update_button(index)

        # もし選択中だったら解除
        if self.selected_index == index:
            self.selected_index = None
            self.update_selection()

    def update_button(self, index):
        color = self.palette[index]
        if color:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.buttons[index].itemconfig("color", fill=hex_color)
        else:
            hex_color = "#cccccc"
            self.buttons[index].itemconfig("color", fill="")

    def update_selection(self):
        for i, btn in enumerate(self.buttons):
            if i == self.selected_index:
                btn.itemconfig(
                    "selection", state="normal", outline=self.SELECTION_COLOR
                )
            else:
                btn.itemconfig("selection", state="hidden")

    def save(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("Palette File", "*.json")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.palette, f)

            messagebox.showinfo("保存完了", "ユーザーパレットを保存しました。")
        except Exception as e:
            messagebox.showerror("保存失敗", f"保存中にエラーが発生しました。\n\n{e}")

    def load(self):
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
            self.palette = [
                tuple(c) if c is not None else None
                for c in loaded[: self.USER_PALETTE_SIZE]
            ]

            # 足りない分を None で埋める
            while len(self.palette) < self.USER_PALETTE_SIZE:
                self.palette.append(None)

            # ボタン表示更新
            for i in range(self.USER_PALETTE_SIZE):
                self.update_button(i)

            messagebox.showinfo("読込完了", "ユーザーパレットを読み込みました。")
        except Exception as e:
            messagebox.showerror(
                "読込失敗", f"読み込み中にエラーが発生しました。\n\n{e}"
            )

    def register_current_color(self):
        if self.selected_index is None:
            return

        r, g, b, _ = self.controller.get_color()

        idx = self.selected_index
        self.palette[idx] = (r, g, b)
        self.update_button(idx)

    # =====================================================
    # マウスホイール
    # =====================================================
    def _enable_palette_scroll(self):

        def _on_mousewheel(event):
            # Windows / mac
            if hasattr(event, "delta") and event.delta:
                delta = int(-1 * (event.delta / 120))
            else:
                # Linux
                if event.num == 4:  # 上
                    delta = -1
                elif event.num == 5:  # 下
                    delta = 1
                else:
                    delta = 0

            self.canvas.yview_scroll(delta, "units")
            return "break"

        widgets = [self.canvas, self.frame] + self.buttons

        for w in widgets:
            w.bind("<MouseWheel>", _on_mousewheel)  # Win / mac
            w.bind("<Button-4>", _on_mousewheel)  # Linux 上
            w.bind("<Button-5>", _on_mousewheel)  # Linux 下
