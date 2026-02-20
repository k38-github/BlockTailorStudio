class ColorController:
    def __init__(self):
        self.current_rgba = (255, 0, 0, 255)
        self.observers = []

    def set_color(self, rgba):
        if rgba == self.current_rgba:
            return

        self.current_rgba = rgba
        self.notify()

    def get_color(self):
        return self.current_rgba

    def add_observer(self, callback):
        self.observers.append(callback)

    def notify(self):
        for callback in self.observers:
            callback(self.current_rgba)
