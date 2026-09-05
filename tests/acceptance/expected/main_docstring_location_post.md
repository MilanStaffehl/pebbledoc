# stellarium_lite documentation

This document lists the full public API of the `stellarium_lite` package.

#### Table of contents
- [`stellarium_lite`](#stellarium_lite)
  - [`stellarium_lite.DEFAULT_CATALOG_NAME`](#stellarium_litedefault_catalog_name)
  - [`stellarium_lite.load_catalog`](#stellarium_liteload_catalog)
  - [`stellarium_lite.CelestialObject`](#stellarium_litecelestialobject)
  - [`stellarium_lite.Star`](#stellarium_litestar)
- [`stellarium_lite.observation`](#stellarium_liteobservation)
  - [`stellarium_lite.observation.MAX_MAGNITUDE`](#stellarium_liteobservationmax_magnitude)
  - [`stellarium_lite.observation.plan_session`](#stellarium_liteobservationplan_session)
  - [`stellarium_lite.observation.ObservableMixin`](#stellarium_liteobservationobservablemixin)
  - [`stellarium_lite.observation.VariableStar`](#stellarium_liteobservationvariablestar)
  - [`stellarium_lite.observation.HybridObject`](#stellarium_liteobservationhybridobject)
  - [`stellarium_lite.observation.Observation`](#stellarium_liteobservationobservation)


A tiny mock astronomy package used to exercise an RST-to-Markdown docstring renderer.

There is one sub-package, the [`observation`](#stellarium_liteobservation) package.
It holds utilities to handle observational data and plan observations.

This package is not a real astronomy library -- every function is a stub and
every constant is arbitrary. It exists purely as a fixture. If you have any
questions, *don't* send an email to <user@example.com>!

## `stellarium_lite`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="default_catalog_name"></a>
### `stellarium_lite.DEFAULT_CATALOG_NAME`

```Python
DEFAULT_CATALOG_NAME: str = 'Messier'
```

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="load_catalog"></a>
### `stellarium_lite.load_catalog`

```Python
load_catalog(name: str = 'Messier') -> dict
```

Load a named catalog of celestial objects.

Supported catalogs, in rough order of popularity:

1. Messier
2. NGC
3. IC

Within each catalog, objects are grouped as:

- Galaxies
  - Spiral
  - Elliptical
- Nebulae
- Star clusters

Catalog metadata for the default catalog:

- **Author:** Charles Messier
- **Year:** 1774
- **Publisher:** Academie royale des sciences

A *very* small excerpt of the raw format looks like this:

```
M31,Andromeda Galaxy,10.68,41.27
M42,Orion Nebula,83.82,-5.39
```

> [!TIP]
>
> Catalog files are cached on first load; see `_normalize_name`
> for how lookup keys are derived.

> :heavy_plus_sign: **Added in version 0.2.0**

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
### `stellarium_lite.CelestialObject`

```Python
CelestialObject(object)
```

Base class for anything you can point a telescope at.

A [`CelestialObject`](#celestialobject) tracks basic **positional** information --
right ascension and declination -- along with an optional *kind* label.
Positions are expressed in degrees, following the convention
$0^\circ \le \alpha < 360^\circ$ for right ascension.

> **Attention:**
>
> Coordinates are assumed to use the J2000 epoch. Mixing epochs will
> silently produce wrong results.

> **Danger:**
>
> Do not pass declinations outside $[-90^\circ, 90^\circ]$ --
> downstream trigonometry will raise or, worse, return nonsense.

> [!CAUTION]
>
> Instances are **not** thread-safe; see [`kind`](#kind) mutation in
> `_recompute`.

> :recycle: **Changed in version 0.3.0:** `ra` and `dec` are now stored in degrees instead of radians.

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobjectkind"></a>
<a name="kind"></a>
#### `stellarium_lite.CelestialObject.kind`

```Python
CelestialObject.kind: ClassVar[str] = 'unknown'
```

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobjectis_visible"></a>
<a name="is_visible"></a>
#### `stellarium_lite.CelestialObject.is_visible`

```Python
@property
CelestialObject.is_visible: bool
```

`bool`: Whether the object is currently above the horizon.

This is a naive placeholder -- see [`ObservableMixin`](#observationobservablemixin)
for the real visibility logic used elsewhere in this package.

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobjectdescribe"></a>
<a name="describe"></a>
#### `stellarium_lite.CelestialObject.describe`

```Python
CelestialObject.describe(self, *, verbose: bool = False) -> str
```

Return a short human-readable description.

Uses the object's right ascension (in h \ <sup>m</sup> \ <sup>s</sup>
notation) and declination (in degrees, with <sub>J2000</sub> epoch
implied) to build a one-line summary.

<details open>
<summary><b>Parameters:</b></summary>

- `verbose`: If `True`, include catalog metadata as well.

</details>

<details open>
<summary><b>Returns:</b></summary>

A description such as `"M31 (unknown)"`.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobjectfrom_dict"></a>
<a name="from_dict"></a>
#### `stellarium_lite.CelestialObject.from_dict`

```Python
@classmethod
CelestialObject.from_dict(cls, record: dict) -> CelestialObject
```

Build a [`CelestialObject`](#celestialobject) from a raw catalog record.

<details open>
<summary><b>Parameters:</b></summary>

- `record`: A mapping with at least `name`, `ra`, `dec` keys.

</details>

<details open>
<summary><b>Returns:</b></summary>

A new instance of `cls`.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="celestialobjectangular_separation"></a>
<a name="angular_separation"></a>
#### `stellarium_lite.CelestialObject.angular_separation`

```Python
@staticmethod
CelestialObject.angular_separation(a: CelestialObject, b: CelestialObject) -> float
```

Compute the angular separation between two objects, in degrees.

Uses the standard great-circle formula

```math
\cos(d) = \sin(\delta_1)\sin(\delta_2)
+ \cos(\delta_1)\cos(\delta_2)\cos(\alpha_1 - \alpha_2)
```

<details open>
<summary><b>Parameters:</b></summary>

- `a`: The first object.
- `b`: The second object.

</details>

<details open>
<summary><b>Returns:</b></summary>

Separation `d` in degrees.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="star"></a>
### `stellarium_lite.Star`

```Python
Star(CelestialObject)
```

A single star, extending `CelestialObject` with a magnitude.

See also `catalog` for how instances are typically constructed via
[`load_catalog`](#load_catalog).

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observation"></a>
## `stellarium_lite.observation`

The observation module contains utilities for orchestrating surveys.

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationmax_magnitude"></a>
<a name="max_magnitude"></a>
### `stellarium_lite.observation.MAX_MAGNITUDE`

```Python
MAX_MAGNITUDE: float = 30.0
```

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationplan_session"></a>
<a name="plan_session"></a>
### `stellarium_lite.observation.plan_session`

```Python
plan_session(objects: list, *, start_at: int = 3) -> list
```

Build an ordered observation plan for a night.

Objects are grouped by priority tier:

1. Must-see targets
2. Nice-to-have targets
   1. Bright nice-to-haves
   2. Faint nice-to-haves
3. Filler targets

Numbering can also resume mid-sequence when appending to an existing
plan, e.g. a plan continued from item 3:

3. Re-check M42
4. Re-check M31

See [NASA](https://www.nasa.gov/) for some real-world astronomy.

<details open>
<summary><b>Parameters:</b></summary>

- `objects`: Candidate [`CelestialObject`](#celestialobject) instances.
- `start_at`: Priority tier to begin scheduling from.

</details>

<details open>
<summary><b>Returns:</b></summary>

A list of objects in observation order.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationobservablemixin"></a>
<a name="observablemixin"></a>
### `stellarium_lite.observation.ObservableMixin`

```Python
ObservableMixin(ABC)
```

Abstract interface for anything that can report its own visibility.

> [!IMPORTANT]
>
> Subclasses **must** implement [`observe`](#observe); the base class raises
> `NotImplementedError` otherwise via the `abstractmethod` machinery.

> :heavy_plus_sign: **Added in version 0.1.0**

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationobservablemixinobserve"></a>
<a name="observablemixinobserve"></a>
<a name="observe"></a>
#### `stellarium_lite.observation.ObservableMixin.observe`

```Python
@abstractmethod
ObservableMixin.observe(self) -> Observation
```

Perform an observation and return the resulting record.

<details open>
<summary><b>Returns:</b></summary>

A new [`Observation`](#observation).

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationvariablestar"></a>
<a name="variablestar"></a>
### `stellarium_lite.observation.VariableStar`

```Python
VariableStar(Star)
```

A star whose brightness changes over time.

Extends [`Star`](#star), which in turn extends [`CelestialObject`](#celestialobject).

```text
night 1: mag 3.2
night 2: mag 3.6
night 3: mag 3.1
```

Compare with the equivalent, more explicit directive:

```python
history = [3.2, 3.6, 3.1]
amplitude = max(history) - min(history)
```

<details open>
<summary><b>Parameters:</b></summary>

- `period_days`: Approximate variability period, in days.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationhybridobject"></a>
<a name="hybridobject"></a>
### `stellarium_lite.observation.HybridObject`

```Python
HybridObject(CelestialObject, ObservableMixin)
```

An object that is both a [`CelestialObject`](#celestialobject) and
[`ObservableMixin`](#observablemixin).

> **Hint:**
>
> This class mostly exists to exercise multiple inheritance; prefer
> [`Star`](#star) or [`VariableStar`](#variablestar) for real use.

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationhybridobjectobserve"></a>
<a name="hybridobjectobserve"></a>
<a name="observe"></a>
#### `stellarium_lite.observation.HybridObject.observe`

```Python
HybridObject.observe(self) -> Observation
```

Perform an observation of this hybrid object.

<details open>
<summary><b>Returns:</b></summary>

A new [`Observation`](#observation) record.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationobservation"></a>
<a name="observation"></a>
### `stellarium_lite.observation.Observation`

```Python
@dataclass
Observation(object)
```

A single recorded observation.

<details open>
<summary><b>Parameters:</b></summary>

- `object_name`: Name of the object observed, e.g. `"M31"`.
- `magnitude`: Estimated visual magnitude at time of observation.
- `tags`: Free-form labels attached to this observation.

</details>

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationobservationschema_version"></a>
<a name="observationschema_version"></a>
<a name="schema_version"></a>
#### `stellarium_lite.observation.Observation.schema_version`

```Python
Observation.schema_version: ClassVar[int] = 1
```

<sup>[Back to top](#stellarium_lite-documentation)</sup>
