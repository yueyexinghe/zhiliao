import requests

from Environment import log, GlobalVar, MessageBox


SERVER_URL = "https://main.xyldomain.top:23818/api"
_session = requests.session()


def _sendRequest(endpoint: str, payload: dict | None = None) -> dict | None:
    GlobalVar.mainWindow.setStatus(f"Requesting: {endpoint}")

    if payload is None:
        resp = _session.get(SERVER_URL + endpoint)
    else:
        payload["client"] = "Config"
        resp = _session.post(SERVER_URL + endpoint, json=payload)
    body = resp.json()

    log.debug("Request: %s, Status code: %d", endpoint, resp.status_code)
    GlobalVar.mainWindow.setStatus("Idle")

    if "msg" in body and body["msg"]:
        MessageBox.info(body["msg"])
    if resp.status_code == 403:
        # GlobalVar.mainWindow.toggleLeftMenu(menuEnabled=False)
        GlobalVar.mainWindow.gotoPage("login")
    if resp.status_code != 200:
        return None

    if "data" not in body or body["data"] is None:
        body["data"] = {}
    return body["data"]


def get(endpoint: str):
    return _sendRequest(endpoint)


def post(endpoint: str, payload: dict | None = None):
    if payload is None:
        payload = {}
    return _sendRequest(endpoint, payload)
