class HistoryManager:
    def __init__(self, model, max_history=50, on_change=None):
        self.model = model
        self.on_change = on_change
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history

    def execute(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()

        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        if self.on_change:
            self.on_change()

    def undo(self):
        if not self.undo_stack:
            return

        command = self.undo_stack.pop()

        for layer, x, y, old, new in command["changes"]:
            self.model.draw_pixel_to_layer(layer, x, y, old)

        self.redo_stack.append(command)

        if self.on_change:
            self.on_change()

    def redo(self):
        if not self.redo_stack:
            return

        command = self.redo_stack.pop()

        for layer, x, y, old, new in command["changes"]:
            self.model.draw_pixel_to_layer(layer, x, y, new)

        self.undo_stack.append(command)

        if self.on_change:
            self.on_change()
