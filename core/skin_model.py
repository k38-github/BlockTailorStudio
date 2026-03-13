from typing import Optional
from PIL import Image

from core.skin_areas import (
    FIRST_LAYER_AREAS,
    SECOND_LAYER_AREAS,
    FIRST_LAYER_AREAS_SLIM,
    SECOND_LAYER_AREAS_SLIM,
)
from core.skin_types import CLASSIC


class SkinModel:
    SKIN_SIZE = 64
    TRANSPARENT = (0, 0, 0, 0)

    def __init__(self, skin_type=CLASSIC):
        self.skin_type = skin_type

        if skin_type == CLASSIC:
            self.first_layer_areas = FIRST_LAYER_AREAS
            self.second_layer_areas = SECOND_LAYER_AREAS
        else:
            self.first_layer_areas = FIRST_LAYER_AREAS_SLIM
            self.second_layer_areas = SECOND_LAYER_AREAS_SLIM

        self.edit_second_layer_only = False

        # 第一スキンレイヤーデータ
        self.base_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]

        # 第二スキンレイヤーデータ
        self.overlay_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]

        # ピクセル用idマップ
        self.pixel_items: list[list[Optional[int]]] = [
            [None for _ in range(self.SKIN_SIZE)] for _ in range(self.SKIN_SIZE)
        ]

    def is_first_layer(self, x, y):
        for x1, y1, x2, y2 in self.first_layer_areas.values():
            if x1 <= x < x2 and y1 <= y < y2:
                return True
        return False

    def is_second_layer(self, x, y):
        for x1, y1, x2, y2 in self.second_layer_areas.values():
            if x1 <= x < x2 and y1 <= y < y2:
                return True
        return False

    def can_edit_pixel(self, x, y):
        # 第二レイヤーのみ編集モード
        if not self.edit_second_layer_only:
            return self.is_first_layer(x, y)
        else:
            return self.is_second_layer(x, y)

    def draw_pixel(self, x, y, color):
        if not self.can_edit_pixel(x, y):
            return False

        if self.is_first_layer(x, y):
            self.base_pixels[y][x] = color
        elif self.is_second_layer(x, y):
            self.overlay_pixels[y][x] = color

        return True

    def draw_pixel_to_layer(self, layer, x, y, color):
        if layer == "base":
            self.base_pixels[y][x] = color
        elif layer == "overlay":
            self.overlay_pixels[y][x] = color

    def get_display_color(self, x, y):
        op = self.overlay_pixels[y][x]
        if op[3] > 0:
            return op

        bp = self.base_pixels[y][x]
        if bp[3] > 0:
            return bp

        return self.TRANSPARENT

    def is_valid_position(self, x, y):
        return 0 <= x < self.SKIN_SIZE and 0 <= y < self.SKIN_SIZE

    def set_edit_layer(self, second_only: bool):
        self.edit_second_layer_only = second_only

    def erase_pixel(self, x, y):
        if not self.can_edit_pixel(x, y):
            return False

        if self.is_first_layer(x, y):
            if self.base_pixels[y][x] == self.TRANSPARENT:
                return False
            self.base_pixels[y][x] = self.TRANSPARENT

        elif self.is_second_layer(x, y):
            if self.overlay_pixels[y][x] == self.TRANSPARENT:
                return False
            self.overlay_pixels[y][x] = self.TRANSPARENT

        return True

    def get_editing_color(self, x, y):
        if self.edit_second_layer_only:
            return self.overlay_pixels[y][x]
        return self.base_pixels[y][x]

    def export_image(self):
        img = Image.new("RGBA", (self.SKIN_SIZE, self.SKIN_SIZE))
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                bp = self.base_pixels[y][x]
                op = self.overlay_pixels[y][x]
                img.putpixel((x, y), op if op[3] > 0 else bp)
        return img

    def import_image(self, img):
        for y in range(self.SKIN_SIZE):
            for x in range(self.SKIN_SIZE):
                pixel = img.getpixel((x, y))
                if self.is_second_layer(x, y):
                    self.overlay_pixels[y][x] = pixel
                else:
                    self.base_pixels[y][x] = pixel

    def reset(self, skin_type=CLASSIC):

        self.skin_type = skin_type

        if skin_type == CLASSIC:
            self.first_layer_areas = FIRST_LAYER_AREAS
            self.second_layer_areas = SECOND_LAYER_AREAS
        else:
            self.first_layer_areas = FIRST_LAYER_AREAS_SLIM
            self.second_layer_areas = SECOND_LAYER_AREAS_SLIM

        # 第一レイヤーをクリア
        self.base_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]

        # 第二レイヤーをクリア
        self.overlay_pixels = [
            [self.TRANSPARENT for _ in range(self.SKIN_SIZE)]
            for _ in range(self.SKIN_SIZE)
        ]
