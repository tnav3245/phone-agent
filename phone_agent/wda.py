"""Small client for WebDriverAgent (WDA), the program on the iPhone that taps.

WDA runs an HTTP server on the phone (port 8100). On Windows we forward that
port to http://localhost:8100 with pymobiledevice3 (see scripts/start_phone.ps1).

All coordinates here are in iOS "points" (e.g. 393 x 852 on an iPhone 15),
not screenshot pixels. Screenshots are resized to points before the model sees
them, so the x/y the model picks can be sent straight to WDA.
"""

import base64
import io

import requests
from PIL import Image


class WDAError(RuntimeError):
    pass


class WDA:
    def __init__(self, url="http://localhost:8100", timeout=60):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.session_id = None
        self._size = None

    # --- low-level HTTP -------------------------------------------------
    def _request(self, method, path, json=None):
        try:
            r = requests.request(method, self.url + path, json=json, timeout=self.timeout)
        except requests.ConnectionError as e:
            raise WDAError(
                f"Can't reach WebDriverAgent at {self.url}. Is start_phone.ps1 running "
                "and is the iPhone unlocked?"
            ) from e
        try:
            body = r.json()
        except ValueError:
            body = {}
        if r.status_code >= 400:
            raise WDAError(f"{method} {path} failed ({r.status_code}): {body or r.text[:300]}")
        return body.get("value", body)

    def _s(self, path):
        """Path inside the current session, creating one if needed."""
        if not self.session_id:
            self.start_session()
        return f"/session/{self.session_id}{path}"

    # --- session / info -------------------------------------------------
    def status(self):
        return self._request("GET", "/status")

    def start_session(self):
        value = self._request("POST", "/session", json={"capabilities": {"alwaysMatch": {}}})
        self.session_id = value.get("sessionId") if isinstance(value, dict) else None
        if not self.session_id:
            raise WDAError(f"WDA did not return a session id: {value}")
        return self.session_id

    def window_size(self):
        if not self._size:
            v = self._request("GET", self._s("/window/size"))
            self._size = (int(v["width"]), int(v["height"]))
        return self._size

    # --- seeing ---------------------------------------------------------
    def screenshot_png(self):
        """Screenshot resized to point coordinates, returned as PNG bytes."""
        b64 = self._request("GET", "/screenshot")
        img = Image.open(io.BytesIO(base64.b64decode(b64)))
        w, h = self.window_size()
        if img.size[0] < img.size[1] and w > h or img.size[0] > img.size[1] and w < h:
            w, h = h, w  # rotated screen
        img = img.convert("RGB").resize((w, h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # --- acting ---------------------------------------------------------
    def tap(self, x, y):
        self._request("POST", self._s("/wda/tap"), json={"x": x, "y": y})

    def type_text(self, text):
        self._request("POST", self._s("/wda/keys"), json={"value": list(text)})

    def swipe(self, from_x, from_y, to_x, to_y, duration=0.3):
        self._request(
            "POST",
            self._s("/wda/dragfromtoforduration"),
            json={"fromX": from_x, "fromY": from_y, "toX": to_x, "toY": to_y,
                  "duration": duration},
        )

    def home(self):
        self._request("POST", "/wda/homescreen")

    def launch_app(self, bundle_id):
        self._request("POST", self._s("/wda/apps/launch"), json={"bundleId": bundle_id})
