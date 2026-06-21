import os
from dataclasses import dataclass, field


@dataclass
class ImageColorInfo:
    file_path: str
    colors: set
    diff_colors: set
    sorted_diff_colors: list = field(init=False)

    def __post_init__(self):
        self.sorted_diff_colors = sorted(
            self.diff_colors
        )

    @property
    def file_name(self):
        return os.path.basename(
            self.file_path
        )

    @property
    def color_count(self):
        return len(
            self.colors
        )

    @property
    def diff_count(self):
        return len(
            self.diff_colors
        )


@dataclass
class AnalysisResult:
    image_list: list
    common_colors: set
    elapsed_time: float = 0
    sorted_common_colors: list = field(init=False)
    image_map: dict = field(init=False)

    def __post_init__(self):
        self.sorted_common_colors = sorted(
            self.common_colors
        )

        self.image_map = {}

        for image_info in self.image_list:
            self.image_map[image_info.file_path] = image_info

    @classmethod
    def empty(cls):
        return cls(
            [],
            set(),
            0
        )

    @classmethod
    def from_maps(
            cls,
            color_map,
            common_colors,
            diff_colors,
            elapsed_time
    ):
        image_list = []

        for file_path, colors in color_map.items():
            image_info = ImageColorInfo(
                file_path,
                colors,
                diff_colors.get(
                    file_path,
                    set()
                )
            )

            image_list.append(
                image_info
            )

        return cls(
            image_list,
            common_colors,
            elapsed_time
        )

    def get_image_info(
            self,
            file_path
    ):
        return self.image_map.get(
            file_path
        )

    def has_common_colors(self):
        return len(
            self.common_colors
        ) > 0

    @property
    def total_file_count(self):
        return len(
            self.image_list
        )