import tkinter as tk

from PIL import ImageTk, Image, ImageDraw


class ColorPreview(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.editing = False
        self.internal_update = False

        self.controller = controller
        self.controller.add_observer(self.on_color_changed)

        self.SIZE = 18
        self.RADIUS = 4
        self.SCALE = 3

        self.canvas = tk.Canvas(
            self,
            width=self.SIZE,
            height=self.SIZE,
            bd=0,
            highlightthickness=0,
        )
        self.canvas.pack()

        vcmd = (self.register(self.validate_hex), "%P")
        self.color_entry = tk.Entry(
            self,
            font=("Consolas", 7),
            width=7,
            justify="center",
            validate="key",
            validatecommand=vcmd,
        )
        self.color_entry.pack(pady=2)

        self.color_entry.insert(0, "#000000")

        self.color_entry.bind("<Return>", self.on_color_code_entered)
        self.color_entry.bind("<Escape>", self.on_color_code_entered)
        self.color_entry.bind("<KeyRelease>", self.on_text_changed)
        self.color_entry.bind("<FocusIn>", self.on_focus_in)
        self.color_entry.bind("<FocusOut>", self.on_focus_out)
        self.bind_all("<Button-1>", self.on_global_click, add="+")

        self.preview_image = None
        self.image_id = self.canvas.create_image(
            self.SIZE // 2, self.SIZE // 2, anchor="center"
        )

        self.on_color_changed(self.controller.get_color())

    # ==========================
    # 色変更通知
    # ==========================
    def on_color_changed(self, rgba):
        r, g, b, a = rgba
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        if a == 0:
            img = self.create_transparent_preview()

            self.internal_update = True

            self.color_entry.configure(validate="none", fg="gray")
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, "透明")
            self.color_entry.configure(validate="key")

            self.internal_update = False
        else:
            img = self.create_color_preview((r, g, b))

            if not self.editing:
                self.color_entry.configure(validate="none", fg="black")

                self.color_entry.delete(0, tk.END)
                self.color_entry.insert(0, hex_color)

                self.color_entry.configure(validate="key")

        self.preview_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.preview_image)

    def on_color_code_entered(self, event=None):
        code = self.color_entry.get().strip()

        if not code:
            return

        if not code.startswith("#"):
            code = "#" + code

        if not self.is_valid_hex(code):
            self.revert_to_controller_color()

            self.editing = False
            self.winfo_toplevel().focus_set()
            return

        r, g, b = self.hex_to_rgb(code)

        self.controller.set_color((r, g, b, 255))

        self.editing = False
        self.winfo_toplevel().focus_set()

    # ==========================
    # ★ HEXチェック
    # ==========================
    def is_valid_hex(self, code):
        if len(code) != 7:
            return False
        try:
            int(code[1:], 16)
            return True
        except ValueError:
            return False

    # ==========================
    # ★ HEX → RGB
    # ==========================
    def hex_to_rgb(self, code):
        code = code.lstrip("#")
        return tuple(int(code[i : i + 2], 16) for i in (0, 2, 4))

    def validate_hex(self, new_value):
        if self.internal_update:
            return True

        # 空は許可しない（常に#を維持）
        if new_value == "":
            return False

        # 必ず # から始まる
        if not new_value.startswith("#"):
            return False

        # #だけは残す
        if new_value == "#":
            return True

        # 長さ制限（# + 6桁）
        if len(new_value) > 7:
            return False

        # # の後ろだけチェック
        hex_part = new_value[1:]

        # 16進数チェック
        for c in hex_part:
            if c not in "0123456789abcdefABCDEF":
                return False

        return True

    def fix_cursor(self, event):
        if self.color_entry.index(tk.INSERT) == 0:
            self.color_entry.icursor(1)

    def on_text_changed(self, event=None):
        if self.internal_update:
            return

        text = self.color_entry.get()

        if self.is_complete_hex(text):
            # 正常
            self.color_entry.configure(bg="white")

            r, g, b = self.hex_to_rgb(text)
            self.controller.set_color((r, g, b, 255))
        else:
            # 異常（薄い赤）
            self.color_entry.configure(bg="#ffcccc")

    def is_complete_hex(self, text):
        if len(text) != 7:
            return False

        if not text.startswith("#"):
            return False

        try:
            int(text[1:], 16)
            return True
        except ValueError:
            return False

    def on_focus_in(self, event):
        self.editing = True

    def on_focus_out(self, event):
        text = self.color_entry.get()

        if self.is_complete_hex(text):
            r, g, b = self.hex_to_rgb(text)
            self.controller.set_color((r, g, b, 255))
        else:
            self.revert_to_controller_color()

        self.editing = False

    def revert_to_controller_color(self):
        rgba = self.controller.get_color()
        r, g, b, _ = rgba
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        self.internal_update = True

        self.color_entry.configure(validate="none")
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, hex_color)
        self.color_entry.configure(validate="key")
        self.color_entry.configure(bg="white")

        self.internal_update = False

    def on_global_click(self, event):
        widget = event.widget

        # ★ Entry自身をクリックした場合は無視
        if widget == self.color_entry:
            return

        # ★ Entry配下（内部クリック）も無視したいならこれ
        if str(widget).startswith(str(self.color_entry)):
            return

        # ★ フォーカス外す
        self.color_entry.master.focus_set()

    # ==========================
    # 通常カラー
    # ==========================
    def create_color_preview(self, rgb):
        size = self.SIZE * self.SCALE
        radius = self.RADIUS * self.SCALE

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = self.SCALE

        draw.rounded_rectangle(
            (margin, margin, size - margin - 1, size - margin - 1),
            radius=radius - margin,
            fill=rgb + (255,),
            outline=(70, 130, 182, 180),
            width=self.SCALE,
        )

        # 縮小してアンチエイリアス
        img = img.resize((self.SIZE, self.SIZE), Image.Resampling.LANCZOS)

        return img

    # ==========================
    # 透明表示
    # ==========================
    def create_transparent_preview(self):
        size = self.SIZE * self.SCALE
        radius = self.RADIUS * self.SCALE
        margin = self.SCALE

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        checker = 8 * self.SCALE

        for y in range(0, size, checker):
            for x in range(0, size, checker):
                c = (
                    (200, 200, 200, 255)
                    if (x // checker + y // checker) % 2 == 0
                    else (235, 235, 235, 255)
                )
                draw.rectangle((x, y, x + checker, y + checker), fill=c)

        draw.rounded_rectangle(
            (margin, margin, size - margin - 1, size - margin - 1),
            radius=radius - margin,
            outline=(70, 130, 182, 180),
            width=self.SCALE,
        )

        img = img.resize((self.SIZE, self.SIZE), Image.Resampling.LANCZOS)

        return img
