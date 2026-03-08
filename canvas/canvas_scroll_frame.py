import tkinter as tk


class CanvasScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        self.vbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.hbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            yscrollcommand=self.vbar.set,
            xscrollcommand=self.hbar.set,
        )

        # expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # inner frame
        self.inner = tk.Frame(self.canvas)

        self.window = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw",
        )

        # scrollregion更新
        self.inner.bind("<Configure>", self._update_scrollregion)

        # mousewheel
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    @property
    def content(self):
        return self.inner

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # -----------------------------
    # mousewheel control
    # -----------------------------

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):

        # Windows / Mac
        if event.delta:
            if event.state & 0x1:  # Shift押下 → 横スクロール
                self.canvas.xview_scroll(int(-event.delta / 120), "units")
            else:  # 通常 → 縦スクロール
                self.canvas.yview_scroll(int(-event.delta / 120), "units")

        # Linux
        elif event.num == 4:
            if event.state & 0x1:
                self.canvas.xview_scroll(-1, "units")
            else:
                self.canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            if event.state & 0x1:
                self.canvas.xview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(1, "units")

        return "break"
