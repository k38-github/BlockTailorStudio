class SkinMaker:

    def __init__(self, template_manager, composer):
        self.ORDER = ["face", "hair", "clothes", "accessory"]

        self.template_manager = template_manager
        self.composer = composer

        self.selected = {}

    def select(self, category, template):

        self.selected[category] = template

    def build(self):

        templates = []

        for category in self.ORDER:

            template = self.selected.get(category)

            if template:
                templates.append(template)

        self.composer.apply_templates(templates)
