import hashlib
import platform


def get_device_name():
    device_name = platform.node()

    if not device_name:
        return "UNKNOWN_DEVICE"

    return device_name


def get_windows_machine_guid():
    if platform.system().lower() != "windows":
        return ""

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        )

        value, _ = winreg.QueryValueEx(
            key,
            "MachineGuid"
        )

        winreg.CloseKey(
            key
        )

        return str(
            value
        )

    except Exception:
        return ""


def get_device_hash():
    machine_guid = get_windows_machine_guid()

    if machine_guid:
        source_text = "|".join(
            [
                "grisim-rgb-analyzer",
                platform.system(),
                platform.machine(),
                machine_guid
            ]
        )
    else:
        source_text = "|".join(
            [
                "grisim-rgb-analyzer",
                platform.system(),
                platform.machine(),
                get_device_name()
            ]
        )

    return hashlib.sha256(
        source_text.encode("utf-8")
    ).hexdigest()