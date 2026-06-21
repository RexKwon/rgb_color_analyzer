import os

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QListView,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QSplitter,
    QLineEdit,
    QGraphicsView,
    QGraphicsScene
)
from PIL.ImageQt import ImageQt

from model.analysis_result import AnalysisResult
from service.color_locator import ColorLocatorEngine
from ui.color_list_model import ColorListModel
from worker.analysis_worker import AnalysisWorker


SUPPORTED_IMAGE_EXTENSIONS = (
    ".png",
    ".tga"
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
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        self.scale(
            1.25,
            1.25
        )

    def zoom_out(self):
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
        self.analysis_result = AnalysisResult.empty()
        self.locator_file = None

        self.locator_diff_colors = []
        self.locator_common_colors = []
        self.locator_diff_search_items = []
        self.locator_common_search_items = []

        self.locator_engine = ColorLocatorEngine()

        self.analysis_thread = None
        self.analysis_worker = None

        self.setWindowTitle("RGB Color Analyzer")
        self.resize(1000, 700)

        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        main_layout = QVBoxLayout()

        main_splitter = QSplitter(
            Qt.Horizontal
        )

        self.widget_compare = QWidget()
        self.widget_locator = QWidget()

        self.label_color_info = QLabel("색상정보")
        self.label_diff_color = QLabel("추가색상 (0)")
        self.list_diff_color = QListView()
        self.label_common_color = QLabel("공통색상 (0)")
        self.list_common_color = QListView()

        self.model_diff_color = ColorListModel()
        self.model_common_color = ColorListModel()

        self.list_diff_color.setModel(
            self.model_diff_color
        )
        self.list_common_color.setModel(
            self.model_common_color
        )

        self.list_diff_color.setUniformItemSizes(
            True
        )
        self.list_common_color.setUniformItemSizes(
            True
        )

        self.input_locator_search = QLineEdit()
        self.input_locator_search.setPlaceholderText(
            "RGB 검색"
        )

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(
            True
        )
        self.search_timer.setInterval(
            150
        )
        self.search_timer.timeout.connect(
            self.filter_locator_colors
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

        self.list_diff_color.clicked.connect(
            self.show_locator_color
        )
        self.list_common_color.clicked.connect(
            self.show_locator_color
        )
        self.input_locator_search.textChanged.connect(
            self.start_locator_search_timer
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
        self.label_status = QLabel("대기 중")

        self.list_result.currentItemChanged.connect(
            self.change_result_item
        )

        file_widget = QWidget()
        file_layout = QVBoxLayout()
        file_layout.addLayout(button_layout)
        file_layout.addWidget(self.label_file)
        file_layout.addWidget(self.list_file)
        file_widget.setLayout(
            file_layout
        )

        result_widget = QWidget()
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.label_result)

        result_splitter = QSplitter(
            Qt.Horizontal
        )
        result_splitter.addWidget(
            self.list_result
        )
        result_splitter.addWidget(
            self.text_result
        )
        result_splitter.setSizes(
            [300, 700]
        )

        result_layout.addWidget(
            result_splitter
        )
        result_widget.setLayout(
            result_layout
        )

        color_info_widget = QWidget()
        color_info_layout = QVBoxLayout()
        color_info_layout.addWidget(
            self.label_color_info
        )
        color_info_layout.addWidget(
            self.input_locator_search
        )

        diff_color_widget = QWidget()
        diff_color_layout = QVBoxLayout()
        diff_color_layout.addWidget(
            self.label_diff_color
        )
        diff_color_layout.addWidget(
            self.list_diff_color
        )
        diff_color_widget.setLayout(
            diff_color_layout
        )

        common_color_widget = QWidget()
        common_color_layout = QVBoxLayout()
        common_color_layout.addWidget(
            self.label_common_color
        )
        common_color_layout.addWidget(
            self.list_common_color
        )
        common_color_widget.setLayout(
            common_color_layout
        )

        color_splitter = QSplitter(
            Qt.Vertical
        )
        color_splitter.addWidget(
            diff_color_widget
        )
        color_splitter.addWidget(
            common_color_widget
        )
        color_splitter.setSizes(
            [110, 130]
        )

        color_info_layout.addWidget(
            color_splitter
        )
        color_info_widget.setLayout(
            color_info_layout
        )

        compare_splitter = QSplitter(
            Qt.Vertical
        )
        compare_splitter.addWidget(
            file_widget
        )
        compare_splitter.addWidget(
            result_widget
        )
        compare_splitter.addWidget(
            color_info_widget
        )
        compare_splitter.setSizes(
            [130, 330, 240]
        )

        compare_layout.addWidget(
            compare_splitter
        )
        compare_layout.addWidget(
            self.label_status
        )

        self.widget_compare.setLayout(
            compare_layout
        )

        locator_layout = QVBoxLayout()

        image_splitter = QSplitter(
            Qt.Vertical
        )
        image_splitter.addWidget(
            self.view_locator_image
        )
        image_splitter.setSizes(
            [700]
        )

        locator_layout.addWidget(
            image_splitter
        )
        self.widget_locator.setLayout(
            locator_layout
        )

        main_splitter.addWidget(
            self.widget_compare
        )
        main_splitter.addWidget(
            self.widget_locator
        )
        main_splitter.setSizes(
            [550, 450]
        )

        main_layout.addWidget(
            main_splitter
        )

        center_widget.setLayout(main_layout)

    def keyPressEvent(self, event):
        if QApplication.focusWidget() == self.input_locator_search:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Space:
            self.view_locator_image.enable_drag()

        if event.key() == Qt.Key_1:
            self.view_locator_image.zoom_in()

        if event.key() == Qt.Key_2:
            self.view_locator_image.zoom_out()

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

        self.set_file_list(
            files
        )

    def select_folder(self):

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "폴더 선택"
        )

        if not folder_path:
            return

        files = []

        for file_name in sorted(os.listdir(folder_path), key=str.lower):

            if self.is_supported_image_file(file_name):
                file_path = os.path.join(
                    folder_path,
                    file_name
                )

                files.append(
                    file_path
                )

        self.set_file_list(
            files
        )

    def is_supported_image_file(
            self,
            file_name
    ):
        return file_name.lower().endswith(
            SUPPORTED_IMAGE_EXTENSIONS
        )

    def set_file_list(
            self,
            files
    ):
        self.file_list = list(
            files
        )

        self.list_file.clear()

        for file_path in self.file_list:
            self.list_file.addItem(
                file_path
            )

        self.reset_analysis_state()

        if self.file_list:
            self.label_status.setText(
                f"{len(self.file_list)}개 파일 선택됨"
            )
        else:
            self.label_status.setText(
                "선택 가능한 이미지 파일이 없습니다."
            )

    def reset_analysis_state(self):
        self.analysis_result = AnalysisResult.empty()

        self.locator_diff_colors = []
        self.locator_common_colors = []
        self.locator_diff_search_items = []
        self.locator_common_search_items = []

        self.clear_locator_state()
        self.clear_result_view()

        self.label_status.setText(
            "대기 중"
        )

    def clear_locator_state(self):
        self.locator_file = None
        self.locator_engine.clear()

        self.scene_locator_image.clear()
        self.view_locator_image.resetTransform()
        self.view_locator_image.horizontalScrollBar().setValue(
            0
        )
        self.view_locator_image.verticalScrollBar().setValue(
            0
        )

    def clear_result_view(self):
        self.search_timer.stop()

        self.list_result.clear()
        self.set_result_text(
            []
        )

        self.input_locator_search.blockSignals(
            True
        )
        self.input_locator_search.clear()
        self.input_locator_search.blockSignals(
            False
        )

        self.label_diff_color.setText(
            "추가색상 (0)"
        )
        self.label_common_color.setText(
            "공통색상 (0)"
        )

        self.model_diff_color.set_colors(
            []
        )
        self.model_common_color.set_colors(
            []
        )

    def analyze_files(self):

        if not self.file_list:
            self.label_status.setText(
                "분석할 이미지 파일이 없습니다."
            )
            return

        if self.analysis_thread is not None:
            return

        self.reset_analysis_state()
        self.set_analysis_running(
            True
        )

        self.analysis_thread = QThread()
        self.analysis_worker = AnalysisWorker(
            self.file_list
        )

        self.analysis_worker.moveToThread(
            self.analysis_thread
        )

        self.analysis_thread.started.connect(
            self.analysis_worker.run
        )
        self.analysis_worker.progress.connect(
            self.handle_analysis_progress
        )
        self.analysis_worker.finished.connect(
            self.handle_analysis_finished
        )
        self.analysis_worker.error.connect(
            self.handle_analysis_error
        )
        self.analysis_worker.completed.connect(
            self.analysis_thread.quit
        )
        self.analysis_worker.completed.connect(
            self.analysis_worker.deleteLater
        )
        self.analysis_thread.finished.connect(
            self.analysis_thread.deleteLater
        )
        self.analysis_thread.finished.connect(
            self.cleanup_analysis_thread
        )

        self.analysis_thread.start()

    def set_analysis_running(
            self,
            running
    ):
        self.btn_file.setEnabled(
            not running
        )
        self.btn_folder.setEnabled(
            not running
        )
        self.btn_analyze.setEnabled(
            not running
        )
        self.btn_copy.setEnabled(
            not running
        )

        if running:
            self.label_status.setText(
                "분석 중입니다..."
            )
            QApplication.setOverrideCursor(
                Qt.WaitCursor
            )
        else:
            QApplication.restoreOverrideCursor()

    def handle_analysis_progress(
            self,
            idx,
            total_count
    ):
        self.label_status.setText(
            f"분석 중입니다... ({idx}/{total_count})"
        )

    def handle_analysis_finished(
            self,
            analysis_result
    ):
        self.analysis_result = analysis_result

        self.set_locator_color_source(
            [],
            self.analysis_result.sorted_common_colors
        )
        self.load_color_info()

        self.list_result.clear()

        self.list_result.addItem(
            self.create_result_item(
                "[전체 결과]"
            )
        )

        for image_info in self.analysis_result.image_list:
            self.list_result.addItem(
                self.create_result_item(
                    f"{image_info.file_name} | {image_info.color_count}색 | +{image_info.diff_count}",
                    image_info.file_path
                )
            )

        self.show_summary_result_text()

        self.list_result.setCurrentRow(
            0
        )

        self.label_status.setText(
            f"분석 완료 ({self.analysis_result.elapsed_time}초)"
        )

    def handle_analysis_error(
            self,
            error_file_name,
            error_text
    ):
        print(
            error_text
        )

        if error_file_name:
            self.label_status.setText(
                f"분석 오류 : {error_file_name}"
            )
        else:
            self.label_status.setText(
                "분석 오류가 발생했습니다."
            )

    def cleanup_analysis_thread(self):
        self.analysis_thread = None
        self.analysis_worker = None

        self.set_analysis_running(
            False
        )

    def copy_colors(self):

        if not self.analysis_result.has_common_colors():
            self.label_status.setText(
                "복사할 공통 색상이 없습니다."
            )
            return

        rgb_text = []

        for rgb in self.analysis_result.sorted_common_colors:
            rgb_text.append(
                self.format_rgb_text(rgb)
            )

        clipboard = QApplication.clipboard()
        clipboard.setText(
            "\n".join(rgb_text)
        )

        self.label_status.setText(
            f"공통 색상 {len(rgb_text)}개 복사 완료"
        )

    def change_result_item(
            self,
            current,
            previous
    ):
        if current is None:
            return

        self.show_file_detail(
            current
        )

    def create_result_item(
            self,
            text,
            file_path=None
    ):
        item = QListWidgetItem(
            text
        )
        item.setData(
            Qt.UserRole,
            file_path
        )

        return item

    def show_file_detail(self, item):

        file_path = item.data(
            Qt.UserRole
        )

        if file_path is None:
            self.show_summary_result_text()

            self.set_locator_color_source(
                [],
                self.analysis_result.sorted_common_colors
            )
            self.load_color_info()

            return

        image_info = self.analysis_result.get_image_info(
            file_path
        )

        if image_info is None:
            return

        self.set_locator_image(
            image_info.file_path
        )

        self.set_locator_color_source(
            image_info.sorted_diff_colors,
            self.analysis_result.sorted_common_colors
        )
        self.load_color_info()

        self.show_file_result_text(
            image_info.file_name,
            image_info.sorted_diff_colors
        )

    def show_summary_result_text(self):
        lines = [
            f"분석 파일 수 : {self.analysis_result.total_file_count}개",
            f"공통 색상 : {len(self.analysis_result.common_colors)}개"
        ]

        self.set_result_text(
            lines
        )

    def show_file_result_text(
            self,
            file_name,
            sorted_diff_colors
    ):
        lines = [
            file_name,
            f"추가 색상 : {len(sorted_diff_colors)}개",
            ""
        ]

        for rgb in sorted_diff_colors:
            lines.append(
                self.format_rgb_text(rgb)
            )

        self.set_result_text(
            lines
        )

    def set_result_text(
            self,
            lines
    ):
        self.text_result.setPlainText(
            "\n".join(lines)
        )

    def set_locator_image(self, file_path):
        self.locator_file = file_path
        self.locator_engine.load_image(
            file_path
        )

        pixmap = QPixmap(
            file_path
        )

        if not pixmap.isNull():
            self.show_locator_pixmap(
                pixmap
            )

    def show_locator_color(self, item):
        if not self.locator_file:
            return

        if not self.locator_engine.has_image():
            return

        rgb = item.data(
            Qt.UserRole
        )

        if rgb is None:
            return

        result_image = self.locator_engine.create_mask_image(
            rgb
        )

        if result_image is None:
            return

        qt_image = ImageQt(
            result_image
        )
        pixmap = QPixmap.fromImage(
            qt_image
        )

        self.show_locator_pixmap(
            pixmap,
            False
        )

    def show_locator_pixmap(
            self,
            pixmap,
            reset_view=True
    ):
        h_value = self.view_locator_image.horizontalScrollBar().value()
        v_value = self.view_locator_image.verticalScrollBar().value()

        if reset_view:
            self.view_locator_image.resetTransform()

        self.scene_locator_image.clear()
        self.scene_locator_image.addPixmap(
            pixmap
        )
        self.scene_locator_image.setSceneRect(
            pixmap.rect()
        )

        if reset_view:
            self.view_locator_image.fitInView(
                self.scene_locator_image.sceneRect(),
                Qt.KeepAspectRatio
            )
        else:
            self.view_locator_image.horizontalScrollBar().setValue(
                h_value
            )
            self.view_locator_image.verticalScrollBar().setValue(
                v_value
            )

    def set_locator_color_source(
            self,
            diff_colors,
            common_colors
    ):
        self.locator_diff_colors = diff_colors
        self.locator_common_colors = common_colors

        self.locator_diff_search_items = self.create_color_search_items(
            diff_colors
        )
        self.locator_common_search_items = self.create_color_search_items(
            common_colors
        )

    def create_color_search_items(
            self,
            colors
    ):
        search_items = []

        for rgb in colors:
            search_items.append(
                (
                    rgb,
                    f"{rgb[0]},{rgb[1]},{rgb[2]}"
                )
            )

        return search_items

    def load_color_info(self):

        keyword = (
            self.input_locator_search.text()
            .strip()
        )

        diff_colors = self.filter_color_list(
            self.locator_diff_search_items,
            keyword
        )
        common_colors = self.filter_color_list(
            self.locator_common_search_items,
            keyword
        )

        self.label_diff_color.setText(
            f"추가색상 ({len(diff_colors)})"
        )
        self.label_common_color.setText(
            f"공통색상 ({len(common_colors)})"
        )

        self.model_diff_color.set_colors(
            diff_colors
        )
        self.model_common_color.set_colors(
            common_colors
        )

    def format_rgb_text(
            self,
            rgb
    ):
        return f"RGB{rgb}"

    def filter_color_list(
            self,
            search_items,
            keyword
    ):
        filtered_colors = []

        for rgb, rgb_text in search_items:

            if keyword:
                if keyword not in rgb_text:
                    continue

            filtered_colors.append(
                rgb
            )

        return filtered_colors

    def start_locator_search_timer(self):
        self.search_timer.start()

    def filter_locator_colors(self):
        self.load_color_info()