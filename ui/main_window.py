import os
from service.color_extractor import extract_colors

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QListWidget,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_list = []
        self.setWindowTitle("RGB Color Analyzer")
        self.resize(1000, 700)

        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.btn_file = QPushButton("파일 선택")
        self.btn_folder = QPushButton("폴더 선택")
        self.btn_analyze = QPushButton("분석 시작")

        self.btn_file.clicked.connect(self.select_files)
        self.btn_folder.clicked.connect(self.select_folder)
        self.btn_analyze.clicked.connect(self.analyze_files)

        button_layout.addWidget(self.btn_file)
        button_layout.addWidget(self.btn_folder)
        button_layout.addWidget(self.btn_analyze)

        self.label_file = QLabel("선택된 파일")

        self.list_file = QListWidget()

        self.label_result = QLabel("분석 결과")

        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.label_file)
        main_layout.addWidget(self.list_file)
        main_layout.addWidget(self.label_result)
        main_layout.addWidget(self.text_result)

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

        file_path = self.file_list[0]

        colors = extract_colors(file_path)

        self.text_result.clear()

        self.text_result.append(
            f"총 색상 수 : {len(colors)}개\n"
        )

        for rgb in colors:
            self.text_result.append(
                f"RGB{rgb}"
            )