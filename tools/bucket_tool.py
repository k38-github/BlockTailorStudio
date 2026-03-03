from tools.base_tool import BaseTool


class BucketTool(BaseTool):
    def __init__(self):
        self.changes = []
        self.visited = set()

        self.mode = "area"  # "area" or "flood"

    def on_press(self, event, controller, canvas):
        self.changes = []
        self.visited = set()
        self._bucket(event, controller, canvas)

    def on_drag(self, event, controller, canvas):
        pass

    def on_release(self, event, controller, canvas):
        pass

    def _bucket(self, event, controller, canvas):
        x, y = canvas.to_skin_coords(event.x, event.y)

        if x is None:
            return

        if self.mode == "area":
            self._fill_area(controller, x, y)
        elif self.mode == "flood":
            self._flood_fill(controller, x, y)
        elif self.mode == "area_flood":
            self._flood_fill_in_area(controller, x, y)

    def _fill_area(self, controller, start_x, start_y):
        model = controller.model
        layer = "overlay" if model.edit_second_layer_only else "base"

        # ここで編集可能か確認
        if not model.can_edit_pixel(start_x, start_y):
            return

        bounds = self.get_clicked_area(model, start_x, start_y)
        if bounds is None:
            return

        x1, y1, x2, y2 = bounds
        new_color = controller.get_color()

        changes = []

        for x in range(x1, x2):
            for y in range(y1, y2):
                old = model.get_editing_color(x, y)
                if old == new_color:
                    continue

                model.draw_pixel_to_layer(layer, x, y, new_color)
                changes.append((layer, x, y, old, new_color))

        if changes:
            controller.execute({"changes": changes})

    def _flood_fill(self, controller, start_x, start_y):
        model = controller.model
        layer = "overlay" if model.edit_second_layer_only else "base"

        # ここで編集可能か確認
        if not model.can_edit_pixel(start_x, start_y):
            return

        target_color = model.get_editing_color(start_x, start_y)
        new_color = controller.get_color()

        # 同じ色なら何もしない
        if target_color == new_color:
            return

        stack = [(start_x, start_y)]
        visited = set()
        changes = []

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            # 範囲外チェック
            if not model.is_valid_position(x, y):
                continue

            if not model.can_edit_pixel(x, y):
                continue

            # 元の色と違うならスキップ
            if model.get_editing_color(x, y) != target_color:
                continue

            old = target_color

            # 直接レイヤー指定で描画
            model.draw_pixel_to_layer(layer, x, y, new_color)

            changes.append((layer, x, y, old, new_color))

            # 上下左右を追加
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

        if changes:
            controller.execute({"changes": changes})

    def _flood_fill_in_area(self, controller, start_x, start_y):
        model = controller.model
        layer = "overlay" if model.edit_second_layer_only else "base"

        # ここで編集可能か確認
        if not model.can_edit_pixel(start_x, start_y):
            return

        bounds = self.get_clicked_area(model, start_x, start_y)
        if bounds is None:
            return

        x1, y1, x2, y2 = bounds

        target_color = model.get_editing_color(start_x, start_y)
        new_color = controller.get_color()

        if target_color == new_color:
            return

        stack = [(start_x, start_y)]
        visited = set()
        changes = []

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            if not (x1 <= x < x2 and y1 <= y < y2):
                continue

            if model.get_editing_color(x, y) != target_color:
                continue

            old = target_color

            # 直接レイヤー指定で描画
            model.draw_pixel_to_layer(layer, x, y, new_color)

            changes.append((layer, x, y, old, new_color))

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

        if changes:
            controller.execute({"changes": changes})

    def get_clicked_area(self, model, grid_x, grid_y):
        if not model.edit_second_layer_only:
            areas = model.first_layer_areas
        else:
            areas = model.second_layer_areas

        for name, (x1, y1, x2, y2) in areas.items():
            if x1 <= grid_x < x2 and y1 <= grid_y < y2:
                return x1, y1, x2, y2

        return None

    def set_mode(self, mode):
        self.mode = mode
