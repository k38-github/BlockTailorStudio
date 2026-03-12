from core.skin_areas import FIRST_LAYER_AREAS, SECOND_LAYER_AREAS
from core.template_areas import TEMPLATE_AREAS

ALL_AREAS = {**FIRST_LAYER_AREAS, **SECOND_LAYER_AREAS}


class SkinComposer:

    def __init__(self, skin_model):
        self.skin_model = skin_model

    def apply_template(self, template):

        img = template["image"]
        pixels = img.load()

        for group in template["areas"]:

            parts = TEMPLATE_AREAS[group]

            for part in parts:

                x1, y1, x2, y2 = ALL_AREAS[part]

                for y in range(y1, y2):
                    for x in range(x1, x2):

                        r, g, b, a = pixels[x, y]

                        if a == 0:
                            continue

                        if self.skin_model.is_first_layer(x, y):
                            self.skin_model.draw_pixel_to_layer(
                                "base", x, y, (r, g, b, a)
                            )

                        elif self.skin_model.is_second_layer(x, y):
                            self.skin_model.draw_pixel_to_layer(
                                "overlay", x, y, (r, g, b, a)
                            )

    def apply_templates(self, templates):

        for template in templates:
            self.apply_template(template)
