# Demonstration data

The full 48-zone synthetic city is generated deterministically rather than
committed as a large static artifact.

```bash
PYTHONPATH=ml python scripts/generate_demo_data.py
```

The command writes `data/samples/delhi_demo.json`. The generated file is ignored
by default because it can always be reproduced from seed `2026`.
