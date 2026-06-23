import json
import socket
import urllib.error
import urllib.request

from auth.device_id import get_device_hash
from auth.device_id import get_device_name


def request_license_auth(
        auth_url,
        license_key,
        app_version
):
    license_key = str(
        license_key
    ).strip()

    if not license_key:
        return {
            "res": "N",
            "msg": "라이선스 키를 입력해주세요."
        }

    payload = {
        "license_key": license_key,
        "device_hash": get_device_hash(),
        "device_name": get_device_name(),
        "app_version": app_version
    }

    try:
        request_data = json.dumps(
            payload
        ).encode("utf-8")

        request = urllib.request.Request(
            auth_url,
            data=request_data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
                request,
                timeout=8
        ) as response:
            response_text = response.read().decode(
                "utf-8"
            )

        data = json.loads(
            response_text
        )

        if not isinstance(data, dict):
            return {
                "res": "N",
                "msg": "인증 서버 응답 형식이 올바르지 않습니다."
            }

        if data.get("res") == "Y":
            return data

        return {
            "res": "N",
            "msg": data.get(
                "msg",
                "라이선스 인증에 실패했습니다."
            )
        }


    except urllib.error.HTTPError as e:
        try:
            error_text = e.read().decode(
                "utf-8"
            )

            data = json.loads(
                error_text
            )

            msg = (
                    data.get("msg") or
                    data.get("message") or
                    data.get("error") or
                    "인증 서버 요청이 거부되었습니다."
            )

            return {
                "res": "N",
                "msg": msg
            }

        except Exception:
            return {
                "res": "N",
                "msg": f"인증 서버 요청이 거부되었습니다. HTTP {e.code}"
            }

    except urllib.error.URLError:
        return {
            "res": "N",
            "msg": "서버 인증에 실패했습니다. 인터넷 연결을 확인해주세요."
        }

    except socket.timeout:
        return {
            "res": "N",
            "msg": "서버 인증 시간이 초과되었습니다."
        }

    except json.JSONDecodeError:
        return {
            "res": "N",
            "msg": "인증 서버 응답을 해석할 수 없습니다."
        }

    except Exception:
        return {
            "res": "N",
            "msg": "라이선스 인증 중 오류가 발생했습니다."
        }