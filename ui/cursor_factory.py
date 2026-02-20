from PIL import Image, ImageDraw, ImageTk


def create_cursor_image(
    diameter=14,
    scale=3,
    outer_color=(70, 130, 182, 180),
    inner_color=(255, 255, 255, 255),
):
    size = diameter * scale
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    outer_width = 3 * scale
    inner_width = 1 * scale

    # 外黒リング
    draw.ellipse(
        (
            outer_width // 2,
            outer_width // 2,
            size - outer_width // 2 - 1,
            size - outer_width // 2 - 1,
        ),
        outline=outer_color,
        width=outer_width,
    )

    # 内白リング
    draw.ellipse(
        (
            outer_width,
            outer_width,
            size - outer_width - 1,
            size - outer_width - 1,
        ),
        outline=inner_color,
        width=inner_width,
    )

    img = img.resize((diameter, diameter), Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(img)
