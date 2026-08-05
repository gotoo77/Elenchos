from elenchos.dataset import DatasetConfig, generate_dataset
from elenchos.exp001 import (
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


def test_parse_integer_is_strict() -> None:
    assert parse_integer("  -42  ") == -42
    assert parse_integer("42\n") == 42
    assert parse_integer("42.0") is None
    assert parse_integer("The answer is 42") is None


def test_views_preserve_expected_relations() -> None:
    instance = ArithmeticInstance(a=37, b=58, k=11, m=2)
    views = build_views(instance)

    assert sum(views.primary) == sum(views.commutative)
    assert sum(views.primary) == sum(views.offset)
    assert sum(views.scaled) == instance.m * sum(views.primary)


def test_zero_syndrome_when_relations_hold() -> None:
    observation = ElenchosObservation(
        primary=95,
        commutative=95,
        offset=95,
        scaled=190,
        multiplier=2,
    )

    assert syndrome(observation).as_tuple() == (0, 0, 0)
    assert elenchos_score(observation) == 0.0


def test_syndrome_records_relation_violations() -> None:
    observation = ElenchosObservation(
        primary=95,
        commutative=94,
        offset=95,
        scaled=189,
        multiplier=2,
    )

    assert syndrome(observation).as_tuple() == (1, 0, 1)
    assert elenchos_score(observation) == 2 / 3


def test_invalid_secondary_output_is_a_violation() -> None:
    observation = ElenchosObservation(
        primary=95,
        commutative=None,
        offset=95,
        scaled=190,
        multiplier=2,
    )
    assert syndrome(observation).as_tuple() == (1, 0, 0)


def test_repetition_score_uses_same_three_comparisons() -> None:
    observation = RepetitionObservation(primary=95, repetitions=(95, 94, 95))
    assert repetition_score(observation) == 1 / 3


def test_evaluation_oracle_is_separate_from_detection() -> None:
    instance = ArithmeticInstance(a=37, b=58, k=3, m=2)
    assert evaluate_primary(instance, 95)
    assert not evaluate_primary(instance, 94)
    assert not evaluate_primary(instance, None)


def test_dataset_generation_is_deterministic_and_unique() -> None:
    config = DatasetConfig(seed=1234, size=50)
    first = generate_dataset(config)
    second = generate_dataset(config)

    assert first == second
    assert len({(item.a, item.b) for item in first}) == 50
    assert all(item.k != 0 for item in first)
    assert all(item.m not in {-1, 0, 1} for item in first)
