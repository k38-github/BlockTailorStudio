import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, width=350):
        super().__init__()

        self.container = tk.Frame(parent, width=width)
        self.container.grid(row=0, column=1, sticky="ns")
        self.container.grid_propagate(False)  # 幅固定

        # スクロール用Canvas
        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # スクロールバー
        self.scrollbar = tk.Scrollbar(
            self.container, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 伸縮設定
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 中身のFrame
        self.inner = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(width=300)

        self.inner.bind("<Configure>", self.update_scrollregion)

        self._enable_parent_scroll()

    @property
    def content(self):
        return self.inner

    # サイズ変更時にスクロール範囲更新
    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _enable_parent_scroll(self):

        def _on_mousewheel(event):
            if hasattr(event, "delta") and event.delta:
                delta = int(-1 * (event.delta / 120))
            else:
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
                else:
                    delta = 0

            self.canvas.yview_scroll(delta, "units")
            return "break"

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)
