from tools.base_tool import BaseTool


class BucketTool(BaseTool):
    def __init__(self):
        self.mode = "area"  # "area" or "flood"

    def on_press(self, event, model, canvas):
        self._bucket(event, model, canvas)

    def on_drag(self, event, model, canvas):
        pass

    def on_release(self, event, model, canvas):
        pass

    def _bucket(self, event, model, canvas):
        x, y = canvas.to_skin_coords(event.x, event.y)

        if x is None:
            return

        if self.mode == "area":
            self._fill_area(model, canvas, x, y)
        elif self.mode == "flood":
            self._flood_fill(model, canvas, x, y)
        elif self.mode == "area_flood":
            self._flood_fill_in_area(model, canvas, x, y)

    def _fill_area(self, model, canvas, start_x, start_y):

        bounds = self.get_clicked_area(model, start_x, start_y)
        if bounds is None:
            return

        x1, y1, x2, y2 = bounds
        color = canvas.controller.get_color()

        updated = False
        for x in range(x1, x2):
            for y in range(y1, y2):
                changed = model.draw_pixel(x, y, color)

                if changed:
                    updated = True

        if updated:
            canvas.redraw()

    def _flood_fill(self, model, canvas, start_x, start_y):
        target_color = model.get_editing_color(start_x, start_y)
        new_color = canvas.controller.get_color()

        # 同じ色なら何もしない
        if target_color == new_color:
            return

        stack = [(start_x, start_y)]
        visited = set()
        updated = False

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            # 範囲外チェック
            if not model.is_valid_position(x, y):
                continue

            # 元の色と違うならスキップ
            if model.get_editing_color(x, y) != target_color:
                continue

            changed = model.draw_pixel(x, y, new_color)
            if changed:
                updated = True

            # 上下左右を追加
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

        if updated:
            canvas.redraw()

    def _flood_fill_in_area(self, model, canvas, start_x, start_y):
        bounds = self.get_clicked_area(model, start_x, start_y)
        if bounds is None:
            return

        x1, y1, x2, y2 = bounds

        target_color = model.get_editing_color(start_x, start_y)
        new_color = canvas.controller.get_color()

        if target_color == new_color:
            return

        stack = [(start_x, start_y)]
        visited = set()
        updated = False

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            if not (x1 <= x < x2 and y1 <= y < y2):
                continue

            if model.get_editing_color(x, y) != target_color:
                continue

            changed = model.draw_pixel(x, y, new_color)
            if changed:
                updated = True

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

        if updated:
            canvas.redraw()

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
