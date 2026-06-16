import os
import time
from PySide6.QtCore import Qt
from service.color_extractor import extract_colors
from service.color_compare import compare_colors
from service.color_locator import create_color_mask
from PySide6.QtGui import QColor, QBrush, QPixmap
from PIL.ImageQt import ImageQt
from PIL import Image

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QSplitter,
    QTabWidget,
    QLineEdit,
    QGraphicsView,
    QGraphicsScene
)

class ImageZoomView(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.setInteractive(
            False
        )

        self.drag_enabled = False
        self.dragging = False
        self.drag_pos = None

    def enable_drag(self):

        self.drag_enabled = True

        if not self.dragging:
            self.setCursor(
                Qt.OpenHandCursor
            )

    def disable_drag(self):

        self.drag_enabled = False
        self.dragging = False
        self.drag_pos = None

        self.setCursor(
            Qt.ArrowCursor
        )

    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:
            self.scale(
                1.25,
                1.25
            )
        else:
            self.scale(
                0.8,
                0.8
            )

    def mousePressEvent(self, event):
        if (
                self.drag_enabled and
                event.button() == Qt.LeftButton
        ):
            self.dragging = True
            self.drag_pos = event.pos()
            self.setCursor(
                Qt.ClosedHandCursor
            )

            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = (
                    event.pos() -
                    self.drag_pos
            )
            self.drag_pos = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - delta.y()
            )

            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            if self.drag_enabled:
                self.setCursor(
                    Qt.OpenHandCursor
                )

            return

        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_list = []
        self.common_colors = set()
        self.color_map = {}
        self.diff_colors = {}
        self.locator_file = None

        self.locator_colors_all = []
        self.locator_pixmap = None
        self.locator_image = None
        self.setWindowTitle("RGB Color Analyzer")
        self.resize(1000, 700)

        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tab_compare = QWidget()
        self.tab_locator = QWidget()
        self.btn_locator_file = QPushButton(
            "이미지 선택"
        )
        self.list_locator_color = QListWidget()

        self.input_locator_search = QLineEdit()
        self.input_locator_search.setPlaceholderText(
            "RGB 검색"
        )

        self.scene_locator_image = QGraphicsScene()
        self.view_locator_image = ImageZoomView()
        self.view_locator_image.setScene(
            self.scene_locator_image
        )
        self.view_locator_image.setMinimumHeight(
            300
        )

        self.view_locator_image.setFocusPolicy(
            Qt.StrongFocus
        )

        self.tabs.addTab(
            self.tab_compare,
            "RGB 비교 분석"
        )
        self.tabs.addTab(
            self.tab_locator,
            "색상 위치 확인"
        )
        compare_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.btn_file = QPushButton("파일 선택")
        self.btn_folder = QPushButton("폴더 선택")
        self.btn_analyze = QPushButton("분석 시작")
        self.btn_copy = QPushButton("RGB 전체 복사")

        self.btn_file.clicked.connect(self.select_files)
        self.btn_folder.clicked.connect(self.select_folder)
        self.btn_analyze.clicked.connect(self.analyze_files)
        self.btn_copy.clicked.connect(self.copy_colors)
        self.btn_locator_file.clicked.connect(
            self.select_locator_image
        )
        self.list_locator_color.itemClicked.connect(
            self.show_locator_color
        )
        self.input_locator_search.textChanged.connect(
            self.filter_locator_colors
        )

        button_layout.addWidget(self.btn_file)
        button_layout.addWidget(self.btn_folder)
        button_layout.addWidget(self.btn_analyze)
        button_layout.addWidget(self.btn_copy)

        self.label_file = QLabel("선택된 파일")
        self.list_file = QListWidget()
        self.label_result = QLabel("분석 결과")
        self.list_result = QListWidget()
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.label_color = QLabel("색상 미리보기")
        self.list_color = QListWidget()
        self.label_status = QLabel("대기 중")
        self.list_result.itemClicked.connect(
            self.show_file_detail
        )

        compare_layout.addLayout(button_layout)
        compare_layout.addWidget(self.label_file)
        compare_layout.addWidget(self.list_file)
        compare_layout.addWidget(self.label_result)
        splitter = QSplitter()
        splitter.addWidget(self.list_result)
        splitter.addWidget(self.text_result)
        splitter.setSizes([300, 700])
        compare_layout.addWidget(splitter)
        compare_layout.addWidget(self.label_color)
        compare_layout.addWidget(self.list_color)
        compare_layout.addWidget(self.label_status)

        self.tab_compare.setLayout(
            compare_layout
        )
        main_layout.addWidget(
            self.tabs
        )

        locator_layout = QVBoxLayout()
        locator_layout.addWidget(
            self.btn_locator_file
        )
        locator_layout.addWidget(
            QLabel("RGB 목록")
        )
        locator_layout.addWidget(
            self.input_locator_search
        )
        locator_layout.addWidget(
            self.list_locator_color
        )
        locator_layout.addWidget(
            self.view_locator_image
        )
        self.tab_locator.setLayout(
            locator_layout
        )

        center_widget.setLayout(main_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.view_locator_image.enable_drag()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.view_locator_image.disable_drag()
        super().keyReleaseEvent(event)

    def select_files(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "이미지 선택",
            "",
            "Image Files (*.png *.tga)"
        )

        if not files:
            return

        self.file_list = files
        self.list_file.clear()

        for file_path in files:
            self.list_file.addItem(file_path)

    def select_folder(self):

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "폴더 선택"
        )

        if not folder_path:
            return

        self.file_list = []
        self.list_file.clear()

        for file_name in os.listdir(folder_path):

            if file_name.lower().endswith((".png", ".tga")):
                file_path = os.path.join(
                    folder_path,
                    file_name
                )

                self.file_list.append(file_path)
                self.list_file.addItem(file_path)

    def analyze_files(self):
        start_time = time.time()
        if not self.file_list:
            return

        self.btn_analyze.setEnabled(False)
        self.label_status.setText("분석 중입니다...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        color_map = {}

        total_count = len(
            self.file_list
        )

        for idx, file_path in enumerate(
                self.file_list,
                start=1
        ):
            self.label_status.setText(
                f"분석 중입니다... ({idx}/{total_count})"
            )

            QApplication.processEvents()

            colors = extract_colors(file_path)

            color_map[file_path] = colors

        common_colors, diff_colors = compare_colors(
            color_map
        )
        self.common_colors = common_colors
        self.color_map = color_map
        self.diff_colors = diff_colors
        self.display_colors(common_colors)

        self.list_result.clear()

        self.list_result.addItem(
            "[전체 결과]"
        )

        for file_path, colors in color_map.items():
            file_name = os.path.basename(
                file_path
            )

            diff_count = len(
                diff_colors[file_path]
            )

            self.list_result.addItem(
                f"{file_name} | {len(colors)}색 | +{diff_count}"
            )

        self.text_result.clear()

        self.text_result.append(
            f"분석 파일 수 : {len(color_map)}개"
        )

        self.text_result.append(
            f"공통 색상 : {len(common_colors)}개"
        )

        self.list_result.setCurrentRow(0)
        elapsed_time = round(
            time.time() - start_time,
            2
        )
        self.label_status.setText(
            f"분석 완료 ({elapsed_time}초)"
        )
        self.btn_analyze.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def display_colors(self, colors):

        self.label_color.setText(
            f"색상 미리보기 ({len(colors)})"
        )

        self.list_color.clear()

        for rgb in sorted(colors):
            item = QListWidgetItem(
                f"RGB{rgb}"
            )

            color = QColor(
                rgb[0],
                rgb[1],
                rgb[2]
            )

            item.setBackground(
                QBrush(color)
            )

            brightness = (
                rgb[0] * 299 +
                rgb[1] * 587 +
                rgb[2] * 114
            ) / 1000

            if brightness < 128:
                item.setForeground(
                    QBrush(QColor(255, 255, 255))
                )
            else:
                item.setForeground(
                    QBrush(QColor(0, 0, 0))
                )

            self.list_color.addItem(item)

    def copy_colors(self):

        if not self.common_colors:
            return

        rgb_text = []

        for rgb in sorted(self.common_colors):
            rgb_text.append(
                f"RGB{rgb}"
            )

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(rgb_text))

    def show_file_detail(self, item):

        row = self.list_result.row(item)

        if row == 0:
            self.text_result.clear()
            self.text_result.append(
                f"분석 파일 수 : {len(self.color_map)}개"
            )
            self.text_result.append(
                f"공통 색상 : {len(self.common_colors)}개"
            )
            return

        file_path = self.file_list[row - 1]

        file_name = os.path.basename(
            file_path
        )

        diff_colors = self.diff_colors.get(
            file_path,
            set()
        )

        self.text_result.clear()

        self.text_result.append(
            f"{file_name}"
        )

        self.text_result.append(
            f"추가 색상 : {len(diff_colors)}개\n"
        )

        for rgb in sorted(diff_colors):

            self.text_result.append(
                f"RGB{rgb}"
            )

    def select_locator_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 선택",
            "",
            "Image Files (*.png *.tga)"
        )
        if not file_path:
            return
        self.locator_file = file_path
        self.locator_image = Image.open(file_path).convert("RGB")
        pixmap = QPixmap(file_path)
        self.locator_pixmap = pixmap
        if not pixmap.isNull():
            self.show_locator_pixmap(
                pixmap
            )
        colors = extract_colors(
            file_path
        )

        self.locator_colors_all = sorted(
            colors
        )

        self.input_locator_search.clear()

        self.load_locator_color_list(
            self.locator_colors_all
        )

    def show_locator_color(self, item):
        if not self.locator_file:
            return

        if item.text() == "[전체 색상]":
            self.show_locator_pixmap(
                self.locator_pixmap
            )
            return

        rgb_text = item.text()
        rgb_text = (
            rgb_text
            .replace("RGB(", "")
            .replace(")", "")
        )
        rgb = tuple(
            map(
                int,
                rgb_text.split(",")
            )
        )
        result_image = create_color_mask(
            self.locator_image,
            rgb
        )
        qt_image = ImageQt(
            result_image
        )
        pixmap = QPixmap.fromImage(
            qt_image
        )
        self.show_locator_pixmap(
            pixmap
        )

    def show_locator_pixmap(
            self,
            pixmap
    ):
        self.view_locator_image.resetTransform()
        self.scene_locator_image.clear()
        self.scene_locator_image.addPixmap(
            pixmap
        )
        self.scene_locator_image.setSceneRect(
            pixmap.rect()
        )
        self.view_locator_image.fitInView(
            self.scene_locator_image.sceneRect(),
            Qt.KeepAspectRatio
        )

    def load_locator_color_list(
            self,
            colors
    ):

        self.list_locator_color.clear()

        self.list_locator_color.addItem(
            "[전체 색상]"
        )

        for rgb in colors:

            item = QListWidgetItem(
                f"RGB{rgb}"
            )

            color = QColor(
                rgb[0],
                rgb[1],
                rgb[2]
            )

            item.setBackground(
                QBrush(color)
            )

            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000

            if brightness < 128:
                item.setForeground(
                    QBrush(QColor(255, 255, 255))
                )
            else:
                item.setForeground(
                    QBrush(QColor(0, 0, 0))
                )

            self.list_locator_color.addItem(
                item
            )

    def filter_locator_colors(self):

        keyword = (
            self.input_locator_search.text()
            .strip()
        )

        filtered_colors = []

        for rgb in self.locator_colors_all:

            rgb_text = (
                f"{rgb[0]},{rgb[1]},{rgb[2]}"
            )

            if keyword:
                if keyword not in rgb_text:
                    continue

            filtered_colors.append(
                rgb
            )

        self.load_locator_color_list(
            filtered_colors
        )