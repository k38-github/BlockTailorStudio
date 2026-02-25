from tools.base_tool import BaseTool


class PenTool(BaseTool):
    def on_press(self, event, model, canvas):
        self._draw(event, model, canvas)

    def on_drag(self, event, model, canvas):
        self._draw(event, model, canvas)

    def on_release(self, event, model, canvas):
        pass  # 今は何もしない

    def _draw(self, event, model, canvas):
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        if not model.can_edit_pixel(x, y):
            return

        color = canvas.controller.get_color()
        changed = model.draw_pixel(x, y, color)

        if changed:
            canvas.draw_pixels(x, y)
