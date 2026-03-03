from controller.history_manager import HistoryManager


class SkinController:
    def __init__(self, model, color_controller):
        self.model = model
        self.color_controller = color_controller
        self.history = None

    def set_color(self, color):
        self.color_controller.set_color(color)

    def get_color(self):
        return self.color_controller.get_color()

    def execute(self, command):
        self.history.execute(command)

    def undo(self):
        self.history.undo()

    def redo(self):
        self.history.redo()

    def set_on_change(self, callback):
        self.history = HistoryManager(self.model, on_change=callback)
