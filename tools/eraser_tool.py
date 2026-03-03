from tools.base_tool import BaseTool


class EraserTool(BaseTool):
    def __init__(self):
        self.changes = []
        self.visited = set()

    def on_press(self, event, controller, canvas):
        self.changes = []
        self.visited = set()
        self._erase(event, controller, canvas)

    def on_drag(self, event, controller, canvas):
        self._erase(event, controller, canvas)

    def on_release(self, event, controller, canvas):
        if self.changes:
            command = {"changes": self.changes}
            controller.execute(command)

    def _erase(self, event, controller, canvas):
        model = controller.model
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        if not model.can_edit_pixel(x, y):
            return

        if (x, y) in self.visited:
            return

        # 現在レイヤー取得
        layer = "overlay" if model.edit_second_layer_only else "base"

        old = model.get_editing_color(x, y)
        new = model.TRANSPARENT

        if old == new:
            return

        # 直接レイヤー指定で消す
        model.draw_pixel_to_layer(layer, x, y, new)
        canvas.draw_pixels(x, y)

        self.changes.append((layer, x, y, old, new))
        self.visited.add((x, y))
