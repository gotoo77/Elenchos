from __future__ import annotations

import argparse

from elenchos.dataset import DatasetConfig, generate_dataset
from elenchos.ollama import OllamaProvider
from elenchos.runner import run_instance, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EXP-001 Ollama smoke test.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1001)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--output", default="results/exp001-smoke.jsonl")
    args = parser.parse_args()

    provider = OllamaProvider(
        model=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
    )
    dataset = generate_dataset(DatasetConfig(seed=args.seed, size=args.size))

    rows = []
    for index, instance in enumerate(dataset, start=1):
        row = run_instance(provider, instance)
        rows.append(row)
        status = "correct" if row["correct"] else "ERROR"
        print(
            f"[{index:03d}/{len(dataset):03d}] {status} "
            f"R={row['repetition']['score']:.3f} "
            f"E={row['elenchos']['score']:.3f} "
            f"S={row['elenchos']['syndrome']}"
        )

    write_jsonl(args.output, rows)
    errors = sum(not row["correct"] for row in rows)
    print(f"\nWrote {len(rows)} rows to {args.output}")
    print(f"Primary errors: {errors}/{len(rows)} ({errors / len(rows):.1%})")


if __name__ == "__main__":
    main()
