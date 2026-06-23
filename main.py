import sys

from PySide6.QtWidgets import QApplication

from auth.license_client import request_license_auth
from auth.license_store import load_license_key
from ui.license_window import LicenseWindow
from ui.main_window import MainWindow


APP_VERSION = "1.0.0"

LICENSE_AUTH_URL = "https://wkaajkzznoskbcsuefat.supabase.co/functions/v1/license-auth"


class AppController:

    def __init__(self):
        self.main_window = None
        self.license_window = None

    def start(self):
        license_key = load_license_key()

        if license_key:
            result = request_license_auth(
                LICENSE_AUTH_URL,
                license_key,
                APP_VERSION
            )

            if result.get("res") == "Y":
                self.show_main_window()
                return

        self.show_license_window()

    def show_license_window(self):
        self.license_window = LicenseWindow(
            LICENSE_AUTH_URL,
            APP_VERSION
        )

        self.license_window.authenticated.connect(
            self.handle_authenticated
        )

        self.license_window.show()

    def handle_authenticated(
            self,
            result
    ):
        if self.license_window is not None:
            self.license_window.close()
            self.license_window = None

        self.show_main_window()

    def show_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication(
        sys.argv
    )

    controller = AppController()
    controller.start()

    sys.exit(
        app.exec()
    )