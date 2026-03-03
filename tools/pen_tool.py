from tools.base_tool import BaseTool


class PenTool(BaseTool):
    def __init__(self):
        self.changes = []
        self.visited = set()  # 同じピクセル重複防止

    def on_press(self, event, controller, canvas):
        self.changes = []
        self.visited = set()
        self._draw(event, controller, canvas)

    def on_drag(self, event, controller, canvas):
        self._draw(event, controller, canvas)

    def on_release(self, event, controller, canvas):
        if self.changes:
            command = {"changes": self.changes}
            controller.execute(command)

    def _draw(self, event, controller, canvas):
        model = controller.model
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        if not model.can_edit_pixel(x, y):
            return

        if (x, y) in self.visited:
            return

        color = canvas.controller.get_color()
        old = model.get_editing_color(x, y)

        changed = model.draw_pixel(x, y, color)

        if not changed:
            return

        canvas.draw_pixels(x, y)

        layer = "overlay" if model.edit_second_layer_only else "base"
        self.changes.append((layer, x, y, old, color))
        self.visited.add((x, y))
