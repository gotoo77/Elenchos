from __future__ import annotations

from dataclasses import dataclass
import re

_INTEGER_RE = re.compile(r"^-?[0-9]+$")


@dataclass(frozen=True)
class ArithmeticInstance:
    a: int
    b: int
    k: int
    m: int

    def truth(self) -> int:
        """Evaluation-only oracle. Detectors must not call this method."""
        return self.a + self.b


@dataclass(frozen=True)
class Views:
    primary: tuple[int, int]
    commutative: tuple[int, int]
    offset: tuple[int, int]
    scaled: tuple[int, int]


@dataclass(frozen=True)
class Syndrome:
    commutative: int
    offset: int
    scaled: int

    def as_tuple(self) -> tuple[int, int, int]:
        return (self.commutative, self.offset, self.scaled)


@dataclass(frozen=True)
class RepetitionObservation:
    primary: int | None
    repetitions: tuple[int | None, int | None, int | None]


@dataclass(frozen=True)
class ElenchosObservation:
    primary: int | None
    commutative: int | None
    offset: int | None
    scaled: int | None
    multiplier: int


def build_views(instance: ArithmeticInstance) -> Views:
    if instance.k == 0:
        raise ValueError("k must be non-zero")
    if instance.m in {-1, 0, 1}:
        raise ValueError("m must not be -1, 0, or 1")

    a, b, k, m = instance.a, instance.b, instance.k, instance.m
    return Views(
        primary=(a, b),
        commutative=(b, a),
        offset=(a + k, b - k),
        scaled=(m * a, m * b),
    )


def parse_integer(raw: str) -> int | None:
    text = raw.strip()
    if not _INTEGER_RE.fullmatch(text):
        return None
    return int(text)


def _different(candidate: int | None, reference: int | None) -> int:
    if candidate is None or reference is None:
        return 1
    return int(candidate != reference)


def repetition_score(observation: RepetitionObservation) -> float:
    violations = [
        _different(value, observation.primary)
        for value in observation.repetitions
    ]
    return sum(violations) / len(violations)


def syndrome(observation: ElenchosObservation) -> Syndrome:
    primary = observation.primary

    z_comm = _different(observation.commutative, primary)
    z_offset = _different(observation.offset, primary)

    if primary is None or observation.scaled is None:
        z_scale = 1
    else:
        z_scale = int(observation.scaled != observation.multiplier * primary)

    return Syndrome(z_comm, z_offset, z_scale)


def elenchos_score(observation: ElenchosObservation) -> float:
    values = syndrome(observation).as_tuple()
    return sum(values) / len(values)


def evaluate_primary(instance: ArithmeticInstance, primary: int | None) -> bool:
    """Evaluation boundary: the only primitive that compares with ground truth."""
    return primary is not None and primary == instance.truth()
