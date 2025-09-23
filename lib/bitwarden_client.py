import os
import time
import subprocess
from urllib.parse import urlparse
from subprocess import PIPE, Popen
from typing import Optional

import requests
from requests.exceptions import RequestException


class BitwardenError(RuntimeError):
    pass


class BitwardenClient:
    """
    Minimal client for Bitwarden Vault Management API via `bw serve`.
    Starts a persistent bw serve when missing, using BW_SESSION if available.
    """

    def __init__(self,
                 serve_url: Optional[str] = None,
                 session: Optional[str] = None,
                 keep_running: bool = True) -> None:
        self.serve_url = serve_url or os.getenv("BW_SERVE_URL", "http://127.0.0.1:8087")
        self.session = session or os.getenv("BW_SESSION")
        self.keep_running = keep_running
        self._proc: Optional[subprocess.Popen] = None

    @staticmethod
    def _is_ready(base_url: str) -> bool:
        try:
            resp = requests.get(f"{base_url}/status", timeout=1.5)
            return resp.status_code == 200
        except RequestException:
            return False

    @staticmethod
    def _parse_url(url: str) -> tuple[str, int]:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8087
        return host, port

    def _start_bw_serve(self) -> None:
        host, port = self._parse_url(self.serve_url)
        base_url = f"http://{host}:{port}"
        print(f"starting persistent Bitwarden Vault Management API at {base_url}")
        cmd = [
            "bw",
            "serve",
            "--hostname",
            host,
            "--port",
            str(port),
        ]
        if self.session:
            cmd += ["--session", self.session]

        env = os.environ.copy()
        if self.session:
            env["BW_SESSION"] = self.session

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env)

        deadline = time.time() + 8.0
        while time.time() < deadline:
            if self._is_ready(base_url):
                self._proc = proc
                return
            if proc.poll() is not None:
                break
            time.sleep(0.2)

        raise BitwardenError("Failed to start bw serve API; ensure CLI installed and vault unlocked.")

    def ensure_running(self) -> None:
        if not self._is_ready(self.serve_url):
            self._start_bw_serve()

    @staticmethod
    def _extract_value(field: str, resp: requests.Response) -> str:
        text = resp.text.strip()
        ctype = (resp.headers.get("Content-Type") or "").lower()
        data = None
        if "application/json" in ctype or text.startswith("{") or text.startswith("["):
            try:
                data = resp.json()
            except ValueError:
                data = None
        if isinstance(data, dict):
            candidates = []
            if field == "password":
                candidates = ["data", "password", "value"]
            elif field == "totp":
                candidates = ["data", "code", "totp", "value"]
            else:
                candidates = ["data", field, "value"]

            for key in candidates:
                val = data.get(key) if isinstance(data, dict) else None
                if isinstance(val, str) and val:
                    return val
                if isinstance(val, dict):
                    for inner_key in candidates:
                        inner_val = val.get(inner_key)
                        if isinstance(inner_val, str) and inner_val:
                            return inner_val
                    inner_val = val.get("data")
                    if isinstance(inner_val, str) and inner_val:
                        return inner_val

            if field == "password":
                login = data.get("login")
                if isinstance(login, dict):
                    val = login.get("password")
                    if isinstance(val, str) and val:
                        return val
        if text:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    return line
        return ""

    def _get_field(self, field: str, item_id: str) -> str:
        url = f"{self.serve_url}/object/{field}/{item_id}"
        resp = requests.get(url, timeout=3.0)
        if resp.status_code != 200:
            raise BitwardenError(f"Bitwarden API error {resp.status_code} for {field} (is your vault unlocked?)")
        val = self._extract_value(field, resp)
        if val:
            return val
        if field == "password":
            item_url = f"{self.serve_url}/object/item/{item_id}"
            item_resp = requests.get(item_url, timeout=3.0)
            if item_resp.status_code == 200:
                val2 = self._extract_value("password", item_resp)
                if val2:
                    return val2
        return ""

    def get_password(self, item_id: str) -> str:
        self.ensure_running()
        return self._get_field("password", item_id)

    def get_totp(self, item_id: str) -> str:
        self.ensure_running()
        return self._get_field("totp", item_id)

    def probe(self, item_id: str) -> None:
        self.ensure_running()
        # Check status
        r = requests.get(f"{self.serve_url}/status", timeout=2.5)
        r.raise_for_status()
        # Try fields
        _ = self.get_password(item_id)
        _ = self.get_totp(item_id)
