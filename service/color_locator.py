from PIL import Image
import numpy as np

HIGHLIGHT_RGB = (
    255,
    0,
    0
)

WHITE_BLEND_RATE = 0.5


class ColorLocatorEngine:

    def __init__(self):
        self.image = None
        self.image_array = None
        self.base_array = None

    def load_image(
            self,
            file_path
    ):
        self.clear()

        self.image = Image.open(file_path).convert("RGBA")

        self.image_array = np.asarray(
            self.image,
            dtype=np.uint8
        )

        self.base_array = self.create_base_array(
            self.image_array
        )

    def clear(self):
        self.image = None
        self.image_array = None
        self.base_array = None

    def has_image(self):
        return self.image_array is not None

    def create_mask_image(
            self,
            target_color
    ):
        if self.image_array is None:
            return None

        if len(target_color) == 3:
            target_color = (
                target_color[0],
                target_color[1],
                target_color[2],
                255
            )
        if len(target_color) != 4:
            return None

        target = np.array(
            target_color,
            dtype=np.uint8
        )

        result_array = self.base_array.copy()

        mask = np.all(
            self.image_array == target,
            axis=2
        )

        result_array[mask] = HIGHLIGHT_RGB

        return Image.fromarray(
            result_array,
            "RGB"
        )

    def create_base_array(
            self,
            image_array
    ):
        rgb_array = image_array[:, :, :3].astype(
            np.float32
        )
        alpha_array = image_array[:, :, 3:4].astype(
            np.float32
        ) / 255.0
        visible_array = (
                rgb_array * alpha_array
                + 255 * (1 - alpha_array)
        )

        base_array = (
                visible_array * (1 - WHITE_BLEND_RATE)
                + 255 * WHITE_BLEND_RATE
        )

        return base_array.astype(
            np.uint8
        )