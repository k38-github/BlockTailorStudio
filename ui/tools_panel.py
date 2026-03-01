import tkinter as tk


class ToolsPanel(tk.LabelFrame):
    def __init__(self, parent, tool_manager):
        super().__init__(parent, text="🖌 ツール", padx=5, pady=5)
        self.tool_manager = tool_manager
        self._build()

    def _build(self):
        # 1段目フレーム
        top_row = tk.Frame(self)
        top_row.pack(fill="x")

        tk.Button(
            top_row,
            text="ペン",
            command=lambda: self.tool_manager.set_tool("pen"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        tk.Button(
            top_row,
            text="スポイト",
            command=lambda: self.tool_manager.set_tool("eyedropper"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        tk.Button(
            top_row,
            text="消しゴム",
            command=lambda: self.tool_manager.set_tool("eraser"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        # 2段目フレーム
        bottom_row = tk.Frame(self)
        bottom_row.pack(fill="x")

        tk.Button(
            bottom_row,
            text="🪣エリア",
            command=lambda: self._select_bucket("area_flood"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        tk.Button(
            bottom_row,
            text="🪣フラッド",
            command=lambda: self._select_bucket("flood"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

    def _select_bucket(self, mode):
        self.tool_manager.set_tool("bucket")
        bucket = self.tool_manager.tools["bucket"]
        bucket.set_mode(mode)
