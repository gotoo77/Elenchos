from elenchos.exp001 import ArithmeticInstance
from elenchos.provider import Generation
from elenchos.runner import run_instance


class SequenceProvider:
    def __init__(self, values: list[str]) -> None:
        self._values = iter(values)

    def generate(self, prompt: str) -> Generation:
        return Generation(text=next(self._values), input_tokens=5, output_tokens=1, latency_ms=1.0)


def test_runner_keeps_oracle_out_of_detection_scores() -> None:
    instance = ArithmeticInstance(a=37, b=58, k=11, m=2)
    provider = SequenceProvider([
        "94",  # primary: deliberately wrong
        "94", "94", "94",  # repetitions agree with the wrong answer
        "94",  # commutative preserves the wrong answer
        "95",  # offset breaks agreement with primary
        "190",  # scale breaks relation with 2 * primary
    ])

    row = run_instance(provider, instance)

    assert row["correct"] is False
    assert row["repetition"]["score"] == 0.0
    assert row["elenchos"]["syndrome"] == [0, 1, 1]
    assert row["elenchos"]["score"] == 2 / 3
