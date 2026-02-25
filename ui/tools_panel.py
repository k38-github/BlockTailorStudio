import tkinter as tk


class ToolsPanel(tk.LabelFrame):
    def __init__(self, parent, tool_manager):
        super().__init__(parent, text="🖌 ツール", padx=5, pady=5)
        self.tool_manager = tool_manager
        self._build()

    def _build(self):
        tk.Button(
            self,
            text="ペン",
            command=lambda: self.tool_manager.set_tool("pen"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        tk.Button(
            self,
            text="スポイト",
            command=lambda: self.tool_manager.set_tool("eyedropper"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        tk.Button(
            self,
            text="消しゴム",
            command=lambda: self.tool_manager.set_tool("eraser"),
        ).pack(side="left", expand=True, fill="x", padx=5, pady=5)
