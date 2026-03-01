from tools.bucket_tool import BucketTool
from tools.eraser_tool import EraserTool
from tools.eyedropper_tool import EyedropperTool
from tools.pen_tool import PenTool


class ToolManager:
    def __init__(self):
        self.current_tool = None
        self.tools = {
            "pen": PenTool(),
            "eyedropper": EyedropperTool(),
            "eraser": EraserTool(),
            "bucket": BucketTool(),
        }

    def set_tool(self, name):
        self.current_tool = self.tools[name]

    def handle_press(self, event, model, canvas):
        if self.current_tool:
            self.current_tool.on_press(event, model, canvas)

    def handle_drag(self, event, model, canvas):
        if self.current_tool:
            self.current_tool.on_drag(event, model, canvas)

    def handle_release(self, event, model, canvas):
        if self.current_tool:
            self.current_tool.on_release(event, model, canvas)
