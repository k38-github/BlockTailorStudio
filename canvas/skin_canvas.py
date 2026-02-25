import tkinter as tk


class SkinCanvas:
    def __init__(self, parent, model, controller, tool_manager):
        self.model = model
        self.controller = controller
        self.tool_manager = tool_manager
        self.SKIN_SIZE = self.model.SKIN_SIZE

        self.PIXEL_SIZE = 10
        self.MARGIN = 20
        self.CANVAS_SIZE = self.SKIN_SIZE * self.PIXEL_SIZE + self.MARGIN * 2

        self.last_drawn = None
        # self.tool_mode = None
        self.edit_second_layer_var = None

        self.canvas_frame = tk.Frame(parent)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.CANVAS_SIZE + self.MARGIN * 2,
            height=self.CANVAS_SIZE + self.MARGIN * 2,
            bg="#FFFFFF",
        )
        self.canvas.pack(expand=True)

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.pick_color)

        self.draw_checkerboard()
        self.draw_frameline()
        self.draw_layer_invalid_mask()

    def draw_checkerboard(self):
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                if (x + y) % 2 == 0:
                    color = "#b0b0b0"
                else:
                    color = "#d0d0d0"
                self.canvas.create_rectangle(
                    self.MARGIN + x * self.PIXEL_SIZE,
                    self.MARGIN + y * self.PIXEL_SIZE,
                    self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                    self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                    fill=color,
                    outline="",
                )

    def draw_frameline(self):
        if not self.model.edit_second_layer_only:
            for name, (x1, y1, x2, y2) in self.model.first_layer_areas.items():
                self.canvas.create_rectangle(
                    self.MARGIN + x1 * self.PIXEL_SIZE,
                    self.MARGIN + y1 * self.PIXEL_SIZE,
                    self.MARGIN + x2 * self.PIXEL_SIZE,
                    self.MARGIN + y2 * self.PIXEL_SIZE,
                    outline="#191970",
                    width=1,
                )
                self.canvas.create_text(
                    self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                    self.MARGIN + y1 * self.PIXEL_SIZE - 8,
                    text=name,
                    fill="#191970",
                    font=("Arial", 7),
                )

        else:
            for name, (x1, y1, x2, y2) in self.model.second_layer_areas.items():
                self.canvas.create_rectangle(
                    self.MARGIN + x1 * self.PIXEL_SIZE,
                    self.MARGIN + y1 * self.PIXEL_SIZE,
                    self.MARGIN + x2 * self.PIXEL_SIZE,
                    self.MARGIN + y2 * self.PIXEL_SIZE,
                    outline="#191970",
                    width=1,
                )
                self.canvas.create_text(
                    self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                    self.MARGIN + y1 * self.PIXEL_SIZE - 8,
                    text=name,
                    fill="#191970",
                    font=("Arial", 7),
                )
        # if current_part == "全体":
        # elif FIRST_LAYER_AREAS[current_part]:
        #    x1, y1, x2, y2 = FIRST_LAYER_AREAS[current_part]
        #    canvas.create_rectangle(
        #        MARGIN + x1 * PIXEL_SIZE,
        #        MARGIN + y1 * PIXEL_SIZE,
        #        MARGIN + x2 * PIXEL_SIZE,
        #        MARGIN + y2 * PIXEL_SIZE,
        #        outline="yellow",
        #        width=3,
        #    )

    def draw_layer_invalid_mask(self):
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                if not self.model.edit_second_layer_only:
                    if not self.model.is_first_layer(x, y):
                        self.canvas.create_rectangle(
                            self.MARGIN + x * self.PIXEL_SIZE,
                            self.MARGIN + y * self.PIXEL_SIZE,
                            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                            fill="#000000",
                            stipple="gray50",
                            outline="",
                        )
                else:
                    if not self.model.is_second_layer(x, y):
                        self.canvas.create_rectangle(
                            self.MARGIN + x * self.PIXEL_SIZE,
                            self.MARGIN + y * self.PIXEL_SIZE,
                            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                            fill="#000000",
                            stipple="gray50",
                            outline="",
                        )

    def draw_pixels(self, x, y):
        if not self.model.edit_second_layer_only:
            r, g, b, a = self.model.base_pixels[y][x]
        else:
            r, g, b, a = self.model.overlay_pixels[y][x]

        # すでに描画済みなら削除
        if self.model.pixel_items[y][x] is not None:
            self.canvas.delete(self.model.pixel_items[y][x])
            self.model.pixel_items[y][x] = None

        # 透明なら何も描かない（＝消しゴム）
        if a == 0:
            return

        self.model.pixel_items[y][x] = self.canvas.create_rectangle(
            self.MARGIN + x * self.PIXEL_SIZE,
            self.MARGIN + y * self.PIXEL_SIZE,
            self.MARGIN + (x + 1) * self.PIXEL_SIZE,
            self.MARGIN + (y + 1) * self.PIXEL_SIZE,
            fill=f"#{r:02x}{g:02x}{b:02x}",
            outline="",
        )

    def redraw(self):
        self.canvas.delete("all")
        self.draw_checkerboard()
        self.draw_frameline()
        self.draw_layer_invalid_mask()

        # pixel_items をリセット
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                self.model.pixel_items[y][x] = None
                self.draw_pixels(x, y)

    def draw_face_frames(self, face_dict, color="#800000"):
        for name, (x1, y1, x2, y2) in face_dict.items():
            self.canvas.create_rectangle(
                self.MARGIN + x1 * self.PIXEL_SIZE,
                self.MARGIN + y1 * self.PIXEL_SIZE,
                self.MARGIN + x2 * self.PIXEL_SIZE,
                self.MARGIN + y2 * self.PIXEL_SIZE,
                outline=color,
                width=1,
            )
            self.canvas.create_text(
                self.MARGIN + (x1 + x2) * self.PIXEL_SIZE // 2,
                self.MARGIN + y1 * self.PIXEL_SIZE - 6,
                text=name,
                fill=color,
                font=("Arial", 7),
            )

    def to_skin_coords(self, px, py):
        x = (px - self.MARGIN) // self.PIXEL_SIZE
        y = (py - self.MARGIN) // self.PIXEL_SIZE
        return x, y

    def pick_color(self, event):
        x, y = self.to_skin_coords(event.x, event.y)

        if not self.model.is_valid_position(x, y):
            return

        color = self.model.get_display_color(x, y)
        self.controller.set_color(color)

    def on_press(self, event):
        self.tool_manager.handle_press(event, self.model, self)

    def on_drag(self, event):
        self.tool_manager.handle_drag(event, self.model, self)

    def on_release(self, event):
        self.tool_manager.handle_release(event, self.model, self)
