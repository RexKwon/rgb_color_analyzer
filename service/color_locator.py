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

        self.image = Image.open(file_path).convert("RGB")

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
            target_rgb
    ):
        if self.image_array is None:
            return None

        target = np.array(
            target_rgb,
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
        base_array = (
                image_array.astype(np.float32) * (1 - WHITE_BLEND_RATE)
                + 255 * WHITE_BLEND_RATE
        )

        return base_array.astype(
            np.uint8
        )