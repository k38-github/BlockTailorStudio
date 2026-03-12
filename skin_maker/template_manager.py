import os
import json
from PIL import Image


class TemplateManager:

    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        self.templates = {}

        self.load_templates()

    def load_templates(self):

        for category in os.listdir(self.template_dir):

            cat_path = os.path.join(self.template_dir, category)

            if not os.path.isdir(cat_path):
                continue

            self.templates[category] = []

            for file in os.listdir(cat_path):

                if not file.endswith(".json"):
                    continue

                json_path = os.path.join(cat_path, file)

                with open(json_path) as f:
                    data = json.load(f)

                img_path = json_path.replace(".json", ".png")

                template = {
                    "name": data["name"],
                    "areas": data["areas"],
                    "image": Image.open(img_path).convert("RGBA"),
                }

                self.templates[category].append(template)
