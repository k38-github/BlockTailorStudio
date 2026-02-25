from tools.base_tool import BaseTool


class EraserTool(BaseTool):
    def on_press(self, event, model, canvas):
        self._erase(event, model, canvas)

    def on_drag(self, event, model, canvas):
        self._erase(event, model, canvas)

    def on_release(self, event, model, canvas):
        pass

    def _erase(self, event, model, canvas):
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        if not model.can_edit_pixel(x, y):
            return

        changed = model.erase_pixel(x, y)

        if changed:
            canvas.draw_pixels(x, y)
