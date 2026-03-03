from tools.base_tool import BaseTool


class EyedropperTool(BaseTool):
    def on_press(self, event, controller, canvas):
        model = controller.model
        x, y = canvas.to_skin_coords(event.x, event.y)

        if not model.is_valid_position(x, y):
            return

        color = model.get_display_color(x, y)
        controller.set_color(color)

    def on_drag(self, event, controller, canvas):
        self.on_press(event, controller, canvas)

    def on_release(self, event, controller, canvas):
        pass
