from tools.base_tool import BaseTool


class EyedropperTool(BaseTool):
    def on_press(self, event, model, canvas):
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        color = model.get_display_color(x, y)
        canvas.controller.set_color(color)

    def on_drag(self, event, model, canvas):
        pass

    def on_release(self, event, model, canvas):
        pass
