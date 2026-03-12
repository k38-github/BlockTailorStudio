from tools.base_tool import BaseTool


class EraserTool(BaseTool):
    def __init__(self, size=1):
        self.size = size
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

        layer = "overlay" if model.edit_second_layer_only else "base"

        for dx in range(self.size):
            for dy in range(self.size):

                px = x + dx
                py = y + dy

                if not model.is_valid_position(px, py):
                    continue

                if not model.can_edit_pixel(px, py):
                    continue

                if (px, py) in self.visited:
                    continue

                old = model.get_editing_color(px, py)
                new = model.TRANSPARENT

                if old == new:
                    continue

                model.draw_pixel_to_layer(layer, px, py, new)
                canvas.draw_pixels(px, py)

                self.changes.append((layer, px, py, old, new))
                self.visited.add((px, py))
