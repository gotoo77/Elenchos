from __future__ import annotations

import json
import time
from urllib import request

from .provider import Generation


class OllamaProvider:
    """Minimal Ollama /api/generate provider for EXP-001."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def generate(self, prompt: str) -> Generation:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": self.temperature},
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        with request.urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        latency_ms = (time.perf_counter() - started) * 1000

        return Generation(
            text=str(data.get("response", "")),
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
            latency_ms=latency_ms,
        )
