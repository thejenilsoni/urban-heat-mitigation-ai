from __future__ import annotations

from pathlib import Path

from urban_heat.training import train


def main() -> None:
    report = train(Path("artifacts/training_report.json"))
    print(report)


if __name__ == "__main__":
    main()
