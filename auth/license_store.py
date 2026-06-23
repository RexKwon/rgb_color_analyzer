import json
import os


STORE_DIR_NAME = "GrisimRGBAnalyzer"
STORE_FILE_NAME = "license.json"


def get_store_dir():
    if os.name == "nt":
        base_dir = os.environ.get(
            "APPDATA"
        )

        if base_dir:
            return os.path.join(
                base_dir,
                STORE_DIR_NAME
            )

    return os.path.join(
        os.path.expanduser("~"),
        ".grisim_rgb_analyzer"
    )


def get_store_file_path():
    return os.path.join(
        get_store_dir(),
        STORE_FILE_NAME
    )


def load_license_key():
    file_path = get_store_file_path()

    if not os.path.exists(file_path):
        return ""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        license_key = data.get(
            "license_key",
            ""
        )

        return str(
            license_key
        ).strip()

    except Exception:
        return ""


def save_license_key(license_key):
    license_key = str(
        license_key
    ).strip()

    if not license_key:
        return False

    store_dir = get_store_dir()

    try:
        os.makedirs(
            store_dir,
            exist_ok=True
        )

        file_path = get_store_file_path()

        data = {
            "license_key": license_key
        }

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception:
        return False