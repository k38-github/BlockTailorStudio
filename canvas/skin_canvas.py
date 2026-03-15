import tkinter as tk


class SkinCanvas(tk.Frame):
    def __init__(self, parent, model, controller, tool_manager, app):
        super().__init__(parent)

        self.model = model
        self.controller = controller
        self.tool_manager = tool_manager
        self.app = app
        self.SKIN_SIZE = self.model.SKIN_SIZE

        self.PIXEL_SIZE = 10
        self.MARGIN = 20
        self.CANVAS_SIZE = self.SKIN_SIZE * self.PIXEL_SIZE + self.MARGIN * 2

        self.LAYER_CHECKER = "checker"
        self.LAYER_PIXEL = "pixel"
        self.LAYER_MASK = "mask"
        self.LAYER_GRID = "grid"
        self.LAYER_FRAME = "frame"
        self.LAYER_CURSOR = "cursor"
        self.LAYER_HOVER = "hover"

        self.last_drawn = None
        self.edit_second_layer_var = None
        self.hover_part = None

        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_SIZE,
            height=self.CANVAS_SIZE,
            bg="#FFFFFF",
        )
        self.canvas.pack(fill="both", expand=True)

        self.cursor_rect = self.canvas.create_rectangle(
            0,
            0,
            0,
            0,
            outline="#2E7D32",
            width=1,
            tags=self.LAYER_CURSOR,
        )

        self.hover_rect = self.canvas.create_rectangle(
            0,
            0,
            0,
            0,
            outline="#2E7D32",
            width=2,
            tags=self.LAYER_HOVER,
        )

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.pick_color)
        self.canvas.bind("<Motion>", self.on_move)
        self.canvas.bind("<Motion>", self._on_mouse_move, add="+")
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        self.draw_checkerboard()
        self.create_pixel_cells()
        self.draw_pixel_grid_lines()
        self.draw_layer_invalid_mask()
        self.draw_frameline()

        self.canvas.tag_raise(self.LAYER_PIXEL)
        self.canvas.tag_raise(self.LAYER_GRID)
        self.canvas.tag_raise(self.LAYER_MASK)
        self.canvas.tag_raise(self.LAYER_FRAME)
        self.canvas.tag_raise(self.LAYER_HOVER)
        self.canvas.tag_raise(self.LAYER_CURSOR)

    def on_press(self, event):
        self.tool_manager.handle_press(event, self.controller, self)

    def on_drag(self, event):
        self.on_move(event)
        self._on_mouse_move(event)
        self.tool_manager.handle_drag(event, self.controller, self)

    def on_release(self, event):
        self.tool_manager.handle_release(event, self.controller, self)

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
                    tags=self.LAYER_CHECKER,
                )

    def draw_frameline(self):
        if not self.model.edit_second_layer_only:
            areas = self.model.first_layer_areas
        else:
            areas = self.model.second_layer_areas

        for name, (x1, y1, x2, y2) in areas.items():

            x1p = self.MARGIN + x1 * self.PIXEL_SIZE
            y1p = self.MARGIN + y1 * self.PIXEL_SIZE
            x2p = self.MARGIN + x2 * self.PIXEL_SIZE
            y2p = self.MARGIN + y2 * self.PIXEL_SIZE

            # 外側（白）
            self.canvas.create_rectangle(
                x1p, y1p, x2p, y2p, outline="#ffffff", width=2, tags=self.LAYER_FRAME
            )

            # 内側（濃色）
            self.canvas.create_rectangle(
                x1p, y1p, x2p, y2p, outline="#191970", width=1, tags=self.LAYER_FRAME
            )

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
                            tags=self.LAYER_MASK,
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
                            tags=self.LAYER_MASK,
                        )

    def draw_pixels(self, x, y):

        if not self.model.edit_second_layer_only:
            r, g, b, a = self.model.base_pixels[y][x]
        else:
            r, g, b, a = self.model.overlay_pixels[y][x]

        rect = self.model.pixel_items[y][x]

        if a == 0:
            self.canvas.itemconfig(rect, fill="")
        else:
            self.canvas.itemconfig(rect, fill=f"#{r:02x}{g:02x}{b:02x}")

    def redraw(self):
        self.canvas.delete(self.LAYER_MASK)
        self.canvas.delete(self.LAYER_FRAME)
        self.canvas.delete(self.LAYER_GRID)

        self.draw_pixel_grid_lines()
        self.draw_layer_invalid_mask()

        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                self.draw_pixels(x, y)

        self.draw_frameline()

        self.canvas.tag_raise(self.LAYER_CURSOR)
        self.update_preview()

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

    def _get_part_at(self, px, py):

        areas = (
            self.model.second_layer_areas
            if self.model.edit_second_layer_only
            else self.model.first_layer_areas
        )

        for name, (x1, y1, x2, y2) in areas.items():
            if x1 <= px < x2 and y1 <= py < y2:
                return name

        return "-"

    def _get_part_rect(self, part):

        areas = (
            self.model.second_layer_areas
            if self.model.edit_second_layer_only
            else self.model.first_layer_areas
        )

        if part not in areas:
            return None

        x1, y1, x2, y2 = areas[part]

        return (
            self.MARGIN + x1 * self.PIXEL_SIZE,
            self.MARGIN + y1 * self.PIXEL_SIZE,
            self.MARGIN + x2 * self.PIXEL_SIZE,
            self.MARGIN + y2 * self.PIXEL_SIZE,
        )

    def pick_color(self, event):
        x, y = self.to_skin_coords(event.x, event.y)

        if not self.model.is_valid_position(x, y):
            return

        color = self.model.get_display_color(x, y)
        self.controller.set_color(color)

    def redraw_all(self):
        self.redraw()

    def on_move(self, event):
        x, y = self.to_skin_coords(event.x, event.y)

        if not self.model.is_valid_position(x, y):
            self.canvas.coords(self.cursor_rect, 0, 0, 0, 0)
            return

        tool = self.tool_manager.current_tool

        size = 1
        if tool == self.tool_manager.tools["eraser"]:
            size = tool.size

        x1 = self.MARGIN + x * self.PIXEL_SIZE
        y1 = self.MARGIN + y * self.PIXEL_SIZE
        x2 = self.MARGIN + (x + size) * self.PIXEL_SIZE
        y2 = self.MARGIN + (y + size) * self.PIXEL_SIZE

        self.canvas.coords(self.cursor_rect, x1, y1, x2, y2)

    def create_pixel_cells(self):
        self.model.pixel_items = [
            [None for _ in range(self.SKIN_SIZE)] for _ in range(self.SKIN_SIZE)
        ]

        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):

                rect = self.canvas.create_rectangle(
                    self.MARGIN + x * self.PIXEL_SIZE,
                    self.MARGIN + y * self.PIXEL_SIZE,
                    self.MARGIN + (x + 1) * self.PIXEL_SIZE,
                    self.MARGIN + (y + 1) * self.PIXEL_SIZE,
                    fill="",
                    outline="",
                    tags=self.LAYER_PIXEL,
                )

                self.model.pixel_items[y][x] = rect

    def draw_pixel_grid_lines(self):

        for x in range(self.SKIN_SIZE + 1):
            px = self.MARGIN + x * self.PIXEL_SIZE
            self.canvas.create_line(
                px,
                self.MARGIN,
                px,
                self.MARGIN + self.SKIN_SIZE * self.PIXEL_SIZE,
                fill="#d3d3d3",
                width=1,
                tags=self.LAYER_GRID,
            )

        for y in range(self.SKIN_SIZE + 1):
            py = self.MARGIN + y * self.PIXEL_SIZE
            self.canvas.create_line(
                self.MARGIN,
                py,
                self.MARGIN + self.SKIN_SIZE * self.PIXEL_SIZE,
                py,
                fill="#d3d3d3",
                width=1,
                tags=self.LAYER_GRID,
            )

    def _on_mouse_move(self, event):

        px, py = self.to_skin_coords(event.x, event.y)

        if px < 0 or py < 0 or px >= self.SKIN_SIZE or py >= self.SKIN_SIZE:
            part = "-"
        else:
            part = self._get_part_at(px, py)

        if part == self.hover_part:
            return

        self.hover_part = part
        self.app.set_part(part)

        rect = self._get_part_rect(part)

        if rect:
            x1, y1, x2, y2 = rect
            self.canvas.coords(self.hover_rect, x1, y1, x2, y2)
        else:
            self.canvas.coords(self.hover_rect, 0, 0, 0, 0)

    def _on_mouse_leave(self, event):

        self.hover_part = None
        self.app.set_part("-")

        self.canvas.coords(self.hover_rect, 0, 0, 0, 0)

    def update_preview(self):

        if hasattr(self.app, "preview_dialog") and self.app.preview_dialog:
            img = self.model.export_image()
            self.app.preview_dialog.update_skin(img)
