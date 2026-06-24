from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtGui import QColor, QBrush


class ColorListModel(QAbstractListModel):

    def __init__(self):
        super().__init__()

        self.colors = []

    def set_colors(
            self,
            colors
    ):
        self.beginResetModel()
        self.colors = list(
            colors
        )
        self.endResetModel()

    def rowCount(
            self,
            parent=QModelIndex()
    ):
        return len(
            self.colors
        )

    def data(
            self,
            index,
            role=Qt.DisplayRole
    ):
        if not index.isValid():
            return None

        color = self.colors[
            index.row()
        ]

        if role == Qt.DisplayRole:
            return self.format_color_text(
                color
            )

        if role == Qt.UserRole:
            return color

        if role == Qt.BackgroundRole:
            visible_rgb = self.get_visible_rgb(
                color
            )

            return QBrush(
                QColor(
                    visible_rgb[0],
                    visible_rgb[1],
                    visible_rgb[2]
                )
            )

        if role == Qt.ForegroundRole:
            visible_rgb = self.get_visible_rgb(
                color
            )
            brightness = self.get_rgb_brightness(
                visible_rgb
            )

            if brightness < 128:
                return QBrush(
                    QColor(255, 255, 255)
                )

            return QBrush(
                QColor(0, 0, 0)
            )

        return None

    def format_color_text(
            self,
            color
    ):
        if len(color) >= 4 and color[3] < 255:
            return f"RGBA{color}"
        return f"RGB({color[0]}, {color[1]}, {color[2]})"

    def get_visible_rgb(
            self,
            color
    ):
        if len(color) < 4:
            return (
                color[0],
                color[1],
                color[2]
            )
        alpha = color[3] / 255
        visible_rgb = (
            int(color[0] * alpha + 255 * (1 - alpha)),
            int(color[1] * alpha + 255 * (1 - alpha)),
            int(color[2] * alpha + 255 * (1 - alpha))
        )
        return visible_rgb

    def get_rgb_brightness(
            self,
            color
    ):
        brightness = (
            color[0] * 299 +
            color[1] * 587 +
            color[2] * 114
        ) / 1000

        return brightness