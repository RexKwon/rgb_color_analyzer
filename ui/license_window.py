from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QApplication
)

from auth.license_client import request_license_auth
from auth.license_store import load_license_key
from auth.license_store import save_license_key


class LicenseWindow(QWidget):

    authenticated = Signal(dict)

    def __init__(
            self,
            auth_url,
            app_version
    ):
        super().__init__()

        self.auth_url = auth_url
        self.app_version = app_version

        self.setWindowTitle(
            "라이선스 인증"
        )
        self.resize(
            420,
            160
        )

        self.label_title = QLabel(
            "프로그램을 사용하려면 라이선스 인증이 필요합니다."
        )

        self.input_license_key = QLineEdit()
        self.input_license_key.setPlaceholderText(
            "라이선스 키를 입력하세요."
        )
        self.input_license_key.setText(
            load_license_key()
        )
        self.input_license_key.returnPressed.connect(
            self.authenticate
        )

        self.label_message = QLabel("")
        self.label_message.setWordWrap(
            True
        )

        self.btn_auth = QPushButton(
            "인증하기"
        )
        self.btn_auth.clicked.connect(
            self.authenticate
        )

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(
            self.btn_auth
        )

        layout = QVBoxLayout()
        layout.addWidget(
            self.label_title
        )
        layout.addWidget(
            self.input_license_key
        )
        layout.addWidget(
            self.label_message
        )
        layout.addLayout(
            button_layout
        )

        self.setLayout(
            layout
        )

    def authenticate(self):
        license_key = (
            self.input_license_key.text()
            .strip()
        )

        if not license_key:
            self.label_message.setText(
                "라이선스 키를 입력해주세요."
            )
            self.input_license_key.setFocus()
            return

        self.btn_auth.setEnabled(
            False
        )
        self.label_message.setText(
            "인증 중입니다..."
        )

        QApplication.processEvents()

        result = request_license_auth(
            self.auth_url,
            license_key,
            self.app_version
        )

        if result.get("res") == "Y":
            save_license_key(
                license_key
            )

            self.label_message.setText(
                result.get(
                    "msg",
                    "인증되었습니다."
                )
            )

            self.authenticated.emit(
                result
            )

            return

        self.label_message.setText(
            result.get(
                "msg",
                "라이선스 인증에 실패했습니다."
            )
        )

        self.btn_auth.setEnabled(
            True
        )