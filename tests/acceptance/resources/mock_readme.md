# stellarium_lite

[![PyPI](https://img.shields.io/badge/pypi-not_published-lightgrey)](https://pypi.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](#license)

A **tiny mock astronomy package** used as a test fixture for an
RST-to-Markdown docstring renderer. It is *not* a real astronomy library —
every function is a stub (`pass`) and every constant is arbitrary.

> Somewhere, something incredible is waiting to be known.
> — Carl Sagan (quoted for flavor, not because this package does anything)

## Contents

- `catalog` — object modelling and catalog lookups
- `observation` — session planning and observation records

## Installation

This package is not published anywhere. To use it locally:

```bash
git clone https://github.com/example/stellarium_lite.git
cd stellarium_lite
pip install -e .
```

## Quick example

```python
from stellarium_lite.catalog import CelestialObject, Star
from stellarium_lite.observation import plan_session, Observation

star = Star(name="M31", ra=10.68, dec=41.27, magnitude=3.4)
plan = plan_session([star])

obs = Observation(object_name="M31", magnitude=3.4, tags=["galaxy", "autumn"])
```

## Module overview

| Module        | Highlights                                                       |
|---------------|------------------------------------------------------------------|
| `catalog`     | `CelestialObject`, `Star`, `load_catalog()`                      |
| `observation` | `ObservableMixin`, `VariableStar`, `HybridObject`, `Observation` |

## Package Documentation

<!-- This is where the documentation will go. -->

## Development

Run the test suite with:

```bash
pytest
```

## Caveats

- [ ] No real astronomical data
- [ ] No real math — formulas are illustrative only
- [x] Exists purely to exercise a docstring parser

See [`catalog.py`](./stellarium_lite/catalog.py) and
[`observation.py`](./stellarium_lite/observation.py) for the actual API
surface and their heavily-annotated docstrings.

## License

MIT; see `LICENSE` for details.
