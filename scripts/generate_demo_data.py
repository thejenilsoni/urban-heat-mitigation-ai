from __future__ import annotations

import json
from pathlib import Path

from urban_heat.data import city_payload


def main() -> None:
    output = Path("data/samples/delhi_demo.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(city_payload(), indent=2), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
