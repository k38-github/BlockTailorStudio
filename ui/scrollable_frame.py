import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, width=None):
        super().__init__(parent)

        # Canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # inner frame
        self.inner = tk.Frame(self.canvas)

        self.window = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw",
        )

        if width:
            self.canvas.configure(width=width)

        # スクロール範囲更新
        self.inner.bind("<Configure>", self._update_scrollregion)

        # Canvas幅に合わせる
        self.canvas.bind("<Configure>", self._fit_width)

        # マウスホイール
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    @property
    def content(self):
        return self.inner

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.window, width=canvas_width)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):

        if event.delta:  # Windows / Mac
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")

        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
