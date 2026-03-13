import tkinter as tk


class BaseDialog(tk.Toplevel):

    def __init__(self, parent, title="Dialog"):
        super().__init__(parent)

        self.parent = parent
        self.result = None

        self.title(title)
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        # ===== body =====
        self.body = tk.Frame(self)
        self.body.pack(padx=10, pady=10)

        self.build_body(self.body)

        # ===== buttons =====
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(0, 10))

        tk.Button(btn_frame, text="OK", width=8, command=self.ok).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Cancel", width=8, command=self.cancel).pack(
            side="left", padx=5
        )

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.wait_window(self)

    def build_body(self, master):
        """サブクラスでUIを作る"""
        pass

    def ok(self):
        self.result = self.get_result()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def get_result(self):
        """サブクラスで結果を返す"""
        return None
