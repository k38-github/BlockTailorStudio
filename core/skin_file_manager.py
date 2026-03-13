from PIL import Image

from core.skin_types import SLIM, CLASSIC


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

        # スキンタイプ判定
        skin_type = self.detect_skin_type(img)

        # モデル初期化
        self.model.reset(skin_type)

        self.model.import_image(img)
        return True

    def detect_skin_type(self, img):

        check_pixels = [
            (54, 20),
            (55, 20),
            (54, 21),
            (55, 21),
        ]

        for x, y in check_pixels:
            r, g, b, a = img.getpixel((x, y))
            if a != 0:
                return CLASSIC

        return SLIM
