"""Asynchroner WebMI-Client mit einer dauerhaften Session."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import secrets
import urllib.parse

import aiohttp

from .const import WEBMI_PASSWORD, WEBMI_USER

_LOGGER = logging.getLogger(__name__)


class WebMIError(Exception):
    """Fehler bei der Kommunikation mit dem Controller."""


def _md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def _rsa_hex(plain: str, mod_hex: str, exp_hex: str) -> str:
    """RSA PKCS#1 v1.5 (Typ 2), Ausgabe als Hex."""
    n, e = int(mod_hex, 16), int(exp_hex, 16)
    k = (n.bit_length() + 7) // 8
    msg = plain.encode()
    if len(msg) > k - 11:
        raise WebMIError("Nachricht zu lang fuer RSA-Schluessel")
    ps = bytes(secrets.choice(range(1, 256)) for _ in range(k - len(msg) - 3))
    em = b"\x00\x02" + ps + b"\x00" + msg
    return format(pow(int.from_bytes(em, "big"), e, n), "x").zfill(k * 2)


class WebMIClient:
    def __init__(self, session: aiohttp.ClientSession, host: str,
                 user: str = WEBMI_USER, password: str = WEBMI_PASSWORD) -> None:
        self._http = session
        self._base = f"http://{host}/webMI/"
        self._user = user
        self._password = password
        self._lock = asyncio.Lock()
        self._sid: str | None = None
        self._w = ""
        self._cnonce = 0
        self._info: dict = {}
        self.logged_in = False

    async def _post(self, fn: str, body: str = "", auth: bool = True) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if auth and self._sid:
            self._cnonce += 1
            digest = _md5(f"{self._sid}:{self._w}:{self._cnonce}")
            headers["X-WebMI"] = (
                f'sessionid="{self._sid}", cnonce="{self._cnonce}", digest="{digest}"'
            )
        try:
            async with self._http.post(
                self._base + "?" + fn, data=body, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                txt = await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise WebMIError(f"{fn}: {err}") from err
        try:
            data = json.loads(txt) if txt.strip() else {}
        except ValueError as err:
            raise WebMIError(f"{fn}: keine JSON-Antwort: {txt[:120]!r}") from err
        if isinstance(data, dict) and data.get("error"):
            raise WebMIError(f"{fn}: {data.get('errorstring', data['error'])}")
        if not isinstance(data, dict):
            raise WebMIError(f"{fn}: Unerwartete Antwort: {str(data)[:120]}")
        return data

    async def connect(self) -> None:
        """Neue Session aufbauen und einloggen."""
        async with self._lock:
            await self._connect_locked()

    async def _connect_locked(self, require_login: bool = False) -> None:
        self._sid, self._cnonce, self.logged_in = None, 0, False
        self._w = secrets.token_hex(16)
        self._info = await self._post("info", auth=False)
        try:
            mod = self._info["encryptionmodulus"]
            exp = self._info["encryptionexponent"]
            res = await self._post("createsession",
                                   "cipher=" + urllib.parse.quote(_rsa_hex(self._w, mod, exp)),
                                   auth=False)
            self._sid = res["sessionid"]
        except (KeyError, ValueError) as err:
            raise WebMIError(f"Session konnte nicht aufgebaut werden: {err}") from err
        body = urllib.parse.urlencode({
            "username": self._user,
            "passwordcipher": _rsa_hex(self._password, mod, exp),
            "passworddigest": _md5(f"{self._sid}:{self._w}:{self._password}"),
        })
        try:
            await self._post("login", body)
        except WebMIError as err:
            # Lesen funktioniert auch ohne Login, daher nur beim Schreiben fatal
            if require_login:
                raise
            _LOGGER.warning("Login fehlgeschlagen, nur Lesezugriff: %s", err)
        else:
            self.logged_in = True

    async def read(self, addrs: list[str]) -> list:
        body = "&".join("address[]=" + urllib.parse.quote(a, safe="") for a in addrs)
        async with self._lock:
            if not self._sid:
                await self._connect_locked()
            try:
                res = await self._post("read", body)
            except WebMIError:
                await self._connect_locked()  # einmal neu verbinden
                res = await self._post("read", body)
        results = res.get("result")
        if (not isinstance(results, list) or len(results) != len(addrs)
                or not all(isinstance(r, dict) for r in results)):
            raise WebMIError(f"Unerwartete Antwort: {str(res)[:120]}")
        return [r.get("value") for r in results]

    async def write(self, addr: str, value) -> None:
        if isinstance(value, bool):
            value = int(value)
        body = (f"address[]={urllib.parse.quote(addr, safe='')}"
                f"&value[]={urllib.parse.quote(str(value))}")
        async with self._lock:
            if not self._sid or not self.logged_in:
                await self._connect_locked(require_login=True)
            try:
                res = await self._post("write", body)
            except WebMIError:
                await self._connect_locked(require_login=True)  # Session abgelaufen
                res = await self._post("write", body)
        results = res.get("result", [])
        if results and isinstance(results[0], dict) and results[0].get("error"):
            raise WebMIError(f"write fehlgeschlagen: {results[0]}")
