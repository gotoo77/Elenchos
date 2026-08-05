from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .exp001 import (
    ArithmeticInstance,
    ElenchosObservation,
    RepetitionObservation,
    build_views,
    elenchos_score,
    evaluate_primary,
    parse_integer,
    repetition_score,
    syndrome,
)
from .provider import ModelProvider, addition_prompt


def _ask(provider: ModelProvider, pair: tuple[int, int]):
    generation = provider.generate(addition_prompt(*pair))
    return generation, parse_integer(generation.text)


def run_instance(provider: ModelProvider, instance: ArithmeticInstance) -> dict:
    views = build_views(instance)

    primary_generation, primary = _ask(provider, views.primary)

    repetition_generations = []
    repetitions = []
    for _ in range(3):
        generation, value = _ask(provider, views.primary)
        repetition_generations.append(generation)
        repetitions.append(value)

    transformed_generations = []
    transformed = []
    for pair in (views.commutative, views.offset, views.scaled):
        generation, value = _ask(provider, pair)
        transformed_generations.append(generation)
        transformed.append(value)

    repetition = RepetitionObservation(primary, tuple(repetitions))
    elenchos = ElenchosObservation(
        primary=primary,
        commutative=transformed[0],
        offset=transformed[1],
        scaled=transformed[2],
        multiplier=instance.m,
    )

    def generation_data(generation):
        return asdict(generation)

    return {
        "instance": asdict(instance),
        "primary": primary,
        "correct": evaluate_primary(instance, primary),
        "repetition": {
            "values": repetitions,
            "score": repetition_score(repetition),
        },
        "elenchos": {
            "values": {
                "commutative": transformed[0],
                "offset": transformed[1],
                "scaled": transformed[2],
            },
            "syndrome": list(syndrome(elenchos).as_tuple()),
            "score": elenchos_score(elenchos),
        },
        "generations": {
            "primary": generation_data(primary_generation),
            "repetitions": [generation_data(g) for g in repetition_generations],
            "views": [generation_data(g) for g in transformed_generations],
        },
    }


def write_jsonl(path: str | Path, rows) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
