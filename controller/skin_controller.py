from controller.history_manager import HistoryManager
from core.skin_types import CLASSIC


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

    def new_skin(self, skin_type=CLASSIC):

        # モデル初期化
        self.model.reset(skin_type)

        # Undo履歴リセット
        self.history.undo_stack.clear()
        self.history.redo_stack.clear()

        # UI更新
        if self.history.on_change:
            self.history.on_change()
