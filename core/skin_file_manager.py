from PIL import Image


class SkinFileManager:
    def __init__(self, model):
        self.model = model

    def save(self, path):
        img = self.model.export_image()
        img.save(path)

    def load(self, path):
        img = Image.open(path).convert("RGBA")

        if img.size != (self.model.SKIN_SIZE, self.model.SKIN_SIZE):
            return False

        self.model.import_image(img)
        return True
