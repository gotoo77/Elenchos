from __future__ import annotations

from dataclasses import dataclass
import random

from .exp001 import ArithmeticInstance


@dataclass(frozen=True)
class DatasetConfig:
    seed: int
    size: int
    min_value: int = 10_000
    max_value: int = 999_999
    max_abs_offset: int = 10_000
    multipliers: tuple[int, ...] = (-3, -2, 2, 3)


def generate_dataset(config: DatasetConfig) -> list[ArithmeticInstance]:
    if config.size <= 0:
        raise ValueError("size must be positive")
    if config.min_value > config.max_value:
        raise ValueError("min_value must not exceed max_value")
    if config.max_abs_offset < 1:
        raise ValueError("max_abs_offset must be >= 1")
    if not config.multipliers or any(m in {-1, 0, 1} for m in config.multipliers):
        raise ValueError("multipliers must exclude -1, 0, and 1")

    rng = random.Random(config.seed)
    seen: set[tuple[int, int]] = set()
    result: list[ArithmeticInstance] = []

    while len(result) < config.size:
        a = rng.randint(config.min_value, config.max_value)
        b = rng.randint(config.min_value, config.max_value)
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)

        k = 0
        while k == 0:
            k = rng.randint(-config.max_abs_offset, config.max_abs_offset)

        m = rng.choice(config.multipliers)
        result.append(ArithmeticInstance(a=a, b=b, k=k, m=m))

    return result
