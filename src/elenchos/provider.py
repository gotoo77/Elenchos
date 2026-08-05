from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Generation:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: float | None = None


class ModelProvider(Protocol):
    """Minimal inference boundary for EXP-001.

    Implementations may target a local or remote model. The experimental core
    depends only on this protocol so provider-specific details cannot leak into
    the detection logic.
    """

    def generate(self, prompt: str) -> Generation: ...


def addition_prompt(a: int, b: int) -> str:
    return f"Calculer exactement {a} + {b}. Répondre uniquement par l'entier résultat."
