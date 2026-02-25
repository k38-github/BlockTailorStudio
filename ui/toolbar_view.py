import tkinter as tk


class ToolbarView:
    def __init__(self, parent, model, canvas):
        self.model = model
        self.canvas = canvas

        layer_section = tk.LabelFrame(parent, text="⚙ レイヤー", padx=5, pady=5)
        layer_section.pack(fill="x", pady=5)

        self.edit_second_layer_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            layer_section,
            text="第二レイヤー編集",
            variable=self.edit_second_layer_var,
            command=self.toggle_edit_second_layer,
        ).pack(anchor="w")

    def toggle_edit_second_layer(self):
        value = self.edit_second_layer_var.get()
        self.model.set_edit_layer(value)
        self.canvas.redraw()
