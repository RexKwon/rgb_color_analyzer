import os
from PySide6.QtCore import Qt
from service.color_extractor import extract_colors
from service.color_compare import compare_colors
from PySide6.QtGui import QColor, QBrush

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
    QSplitter
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_list = []
        self.common_colors = set()
        self.color_map = {}
        self.diff_colors = {}
        self.setWindowTitle("RGB Color Analyzer")
        self.resize(1000, 700)

        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.btn_file = QPushButton("파일 선택")
        self.btn_folder = QPushButton("폴더 선택")
        self.btn_analyze = QPushButton("분석 시작")
        self.btn_copy = QPushButton("RGB 전체 복사")

        self.btn_file.clicked.connect(self.select_files)
        self.btn_folder.clicked.connect(self.select_folder)
        self.btn_analyze.clicked.connect(self.analyze_files)
        self.btn_copy.clicked.connect(self.copy_colors)

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

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.label_file)
        main_layout.addWidget(self.list_file)
        main_layout.addWidget(self.label_result)
        splitter = QSplitter()
        splitter.addWidget(self.list_result)
        splitter.addWidget(self.text_result)
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.label_color)
        main_layout.addWidget(self.list_color)
        main_layout.addWidget(self.label_status)

        center_widget.setLayout(main_layout)

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

        if not self.file_list:
            return

        self.btn_analyze.setEnabled(False)
        self.label_status.setText("분석 중입니다...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        color_map = {}

        for file_path in self.file_list:
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
        self.label_status.setText("분석 완료")
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