from PIL import Image

HIGHLIGHT_RGB = (
    255,
    0,
    255
)

def create_color_mask(
    image,
    target_rgb
):

    width, height = image.size

    pixels = image.getdata()

    result_pixels = []

    for rgb in pixels:

        if rgb == target_rgb:
            result_pixels.append(
                HIGHLIGHT_RGB
            )
        else:
            result_pixels.append(
                (0, 0, 0)
            )

    result = Image.new(
        "RGB",
        (width, height)
    )

    result.putdata(
        result_pixels
    )

    return result