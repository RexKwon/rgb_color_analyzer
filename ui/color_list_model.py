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

        rgb = self.colors[
            index.row()
        ]

        if role == Qt.DisplayRole:
            return self.format_rgb_text(
                rgb
            )

        if role == Qt.UserRole:
            return rgb

        if role == Qt.BackgroundRole:
            return QBrush(
                QColor(
                    rgb[0],
                    rgb[1],
                    rgb[2]
                )
            )

        if role == Qt.ForegroundRole:
            brightness = self.get_rgb_brightness(
                rgb
            )

            if brightness < 128:
                return QBrush(
                    QColor(255, 255, 255)
                )

            return QBrush(
                QColor(0, 0, 0)
            )

        return None

    def format_rgb_text(
            self,
            rgb
    ):
        return f"RGB{rgb}"

    def get_rgb_brightness(
            self,
            rgb
    ):
        brightness = (
            rgb[0] * 299 +
            rgb[1] * 587 +
            rgb[2] * 114
        ) / 1000

        return brightness