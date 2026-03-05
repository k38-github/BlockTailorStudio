import tkinter as tk

from ui.tooltip import ToolTip


class ToolsPanel(tk.LabelFrame):
    def __init__(self, parent, tool_manager):
        super().__init__(parent, text="🖌 ツール", padx=5, pady=5)
        self.tool_manager = tool_manager
        self.buttons = {}

        self.icons = {
            "pen": tk.PhotoImage(file="assets/icons/pen32.png"),
            "eyedropper": tk.PhotoImage(file="assets/icons/dropper32.png"),
            "eraser": tk.PhotoImage(file="assets/icons/eraser32.png"),
            "bucket_area": tk.PhotoImage(file="assets/icons/bucket32.png"),
            "bucket_flood": tk.PhotoImage(file="assets/icons/bucket32.png"),
        }

        self._build()

    def _build(self):
        row = tk.Frame(self)
        row.pack()

        self._add_icon_button(row, "pen")
        self._add_icon_button(row, "eyedropper")
        self._add_icon_button(row, "eraser")
        self._add_icon_button(row, "bucket_area")
        self._add_icon_button(row, "bucket_flood")

    def _add_icon_button(self, parent, name):

        if name == "bucket_area":
            command = lambda: self._select_bucket("area_flood")
        elif name == "bucket_flood":
            command = lambda: self._select_bucket("flood")
        else:
            command = lambda: self._select_tool(name)

        btn = tk.Button(
            parent,
            image=self.icons[name],
            command=command,
            width=32,
            height=32,
            relief="raised",
            bd=2,
            highlightthickness=2,
        )

        self._add_hover_effect(btn, name)

        btn.pack(side="left", padx=4, pady=4)

        btn.default_bg = btn.cget("bg")
        btn.default_fg = btn.cget("fg")

        btn.default_highlight = btn.cget("bg")

        btn.config(
            highlightbackground=btn.default_highlight,
            highlightcolor=btn.default_highlight,
        )

        self.buttons[name] = btn

        tooltips = {
            "pen": "ペン",
            "eyedropper": "スポイト",
            "eraser": "消しゴム",
            "bucket_area": "塗りつぶし（領域）",
            "bucket_flood": "塗りつぶし（全体）",
        }

        ToolTip(btn, tooltips[name])

    def _add_button(self, parent, text, tool_name, command=None):
        if command is None:
            command = lambda: self._select_tool(tool_name)

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            relief="raised",
            bd=2,
            highlightthickness=0,
        )

        btn.default_bg = btn.cget("bg")
        btn.default_fg = btn.cget("fg")

        btn.pack(side="left", expand=True, fill="x", padx=5, pady=5)

        self.buttons[tool_name] = btn

    def _select_tool(self, name):
        self.tool_manager.set_tool(name)
        self._update_button_styles()

    def _select_bucket(self, mode):
        self.tool_manager.set_tool("bucket")
        bucket = self.tool_manager.tools["bucket"]
        bucket.set_mode(mode)
        self._update_button_styles()

    def _update_button_styles(self):
        current = self.tool_manager.current_tool

        bucket = self.tool_manager.tools["bucket"]

        for name, btn in self.buttons.items():

            is_selected = False

            if name == "pen" and current == self.tool_manager.tools["pen"]:
                is_selected = True

            elif (
                name == "eyedropper"
                and current == self.tool_manager.tools["eyedropper"]
            ):
                is_selected = True

            elif name == "eraser" and current == self.tool_manager.tools["eraser"]:
                is_selected = True

            elif name == "bucket_area":
                if current == bucket and bucket.mode == "area_flood":
                    is_selected = True

            elif name == "bucket_flood":
                if current == bucket and bucket.mode == "flood":
                    is_selected = True

            if is_selected:
                btn.config(
                    relief="flat",
                    highlightthickness=2,
                    highlightbackground="#2E7D32",  # 枠色
                    highlightcolor="#4CAF50",
                )
            else:
                btn.config(
                    relief="raised",
                    highlightbackground=btn.default_highlight,
                )

    def _add_hover_effect(self, btn, name):

        def on_enter(e):
            if not self._is_selected(name):
                btn.config(highlightbackground="#aaaaaa")

        def on_leave(e):
            if not self._is_selected(name):
                btn.config(highlightbackground=btn.default_highlight)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _is_selected(self, name):
        current = self.tool_manager.current_tool
        tools = self.tool_manager.tools

        if name in ("pen", "eyedropper", "eraser"):
            return current == tools[name]

        if name == "bucket_area":
            return current == tools["bucket"] and tools["bucket"].mode == "area_flood"

        if name == "bucket_flood":
            return current == tools["bucket"] and tools["bucket"].mode == "flood"

        return False
