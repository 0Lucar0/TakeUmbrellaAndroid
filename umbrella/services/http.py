from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: str

    def json(self) -> Any:
        return json.loads(self.body)


def get_json(url: str, params: dict[str, Any] | None = None, timeout_s: float = 10.0) -> Any:
    if params:
        url = f"{url}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "take-umbrella/1.0"})
    with urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)

