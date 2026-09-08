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

### `stellarium_lite`

A tiny mock astronomy package used to exercise an RST-to-Markdown docstring renderer.

There is one sub-package, the [`observation`](#stellarium_liteobservation) package.
It holds utilities to handle observational data and plan observations.

This is a previous version of the mock docs, which should be overwritten
by the next update.

<a name="load_catalog"></a>
#### `stellarium_lite.load_catalog`

```Python
load_catalog(name: str = 'Messier') -> dict
```

Load a named catalog of celestial objects.

Supported catalogs, in rough order of popularity:

1. Messier
2. NGC

Within each catalog, objects are grouped as:

- Galaxies
  - Spiral
  - Elliptical

<details open>
<summary><b>Parameters:</b></summary>

- `name`: The catalog identifier, e.g. `"Messier"`.

</details>

<details open>
<summary><b>Returns:</b></summary>

A `dict` mapping object names to raw records.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobject"></a>
#### `stellarium_lite.CelestialObject`

```Python
CelestialObject(object)
```

Base class for anything you can point a telescope at.

A [`CelestialObject`](#celestialobject) tracks basic **positional** information --
right ascension and declination -- along with an optional *kind* label.
Positions are expressed in degrees, following the convention
$0^\circ \le \alpha < 360^\circ$ for right ascension.

> :recycle: **Changed in version 0.3.0:** `ra` and `dec` are now stored in degrees instead of radians.

<sup>[Back to top](#stellarium_lite-documentation)</sup>


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

MIT — see `LICENSE` for details.
