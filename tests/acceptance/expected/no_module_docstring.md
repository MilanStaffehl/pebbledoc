# stellarium_lite documentation

> #### Table of contents
> - [`stellarium_lite`](#stellarium_lite)
>   - [`stellarium_lite.DEFAULT_CATALOG_NAME`](#stellarium_litedefault_catalog_name)
>   - [`stellarium_lite.load_catalog`](#stellarium_liteload_catalog)
>   - [`stellarium_lite.CelestialObject`](#stellarium_litecelestialobject)
>   - [`stellarium_lite.Star`](#stellarium_litestar)
> - [`stellarium_lite.observation`](#stellarium_liteobservation)
>   - [`stellarium_lite.observation.MAX_MAGNITUDE`](#stellarium_liteobservationmax_magnitude)
>   - [`stellarium_lite.observation.plan_session`](#stellarium_liteobservationplan_session)
>   - [`stellarium_lite.observation.ObservableMixin`](#stellarium_liteobservationobservablemixin)
>   - [`stellarium_lite.observation.VariableStar`](#stellarium_liteobservationvariablestar)
>   - [`stellarium_lite.observation.HybridObject`](#stellarium_liteobservationhybridobject)
>   - [`stellarium_lite.observation.Observation`](#stellarium_liteobservationobservation)


## `stellarium_lite`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="default_catalog_name"></a>
### `stellarium_lite.DEFAULT_CATALOG_NAME`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
DEFAULT_CATALOG_NAME: str = 'Messier'
```

<a name="load_catalog"></a>
### `stellarium_lite.load_catalog`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

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

> :heavy_plus_sign: Added in version 0.2.0

**Parameters:**

- `name`: The catalog identifier, e.g. `"Messier"`.

**Returns:**

A `dict` mapping object names to raw records.

<a name="celestialobject"></a>
### `stellarium_lite.CelestialObject`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

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

> :recycle: Changed in version 0.3.0: `ra` and `dec` are now stored in degrees instead of radians.

<a name="celestialobjectkind"></a>
<a name="kind"></a>
#### `stellarium_lite.CelestialObject.kind`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
CelestialObject.kind: ClassVar[str] = 'unknown'
```

<a name="celestialobjectis_visible"></a>
<a name="is_visible"></a>
#### `stellarium_lite.CelestialObject.is_visible`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
@property
CelestialObject.is_visible: bool
```

`bool`: Whether the object is currently above the horizon.

This is a naive placeholder -- see [`ObservableMixin`](#observationobservablemixin)
for the real visibility logic used elsewhere in this package.

<a name="celestialobjectdescribe"></a>
<a name="describe"></a>
#### `stellarium_lite.CelestialObject.describe`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
CelestialObject.describe(self, *, verbose: bool = False) -> str
```

Return a short human-readable description.

Uses the object's right ascension (in h \ <sup>m</sup> \ <sup>s</sup>
notation) and declination (in degrees, with <sub>J2000</sub> epoch
implied) to build a one-line summary.

**Parameters:**

- `verbose`: If `True`, include catalog metadata as well.

**Returns:**

A description such as `"M31 (unknown)"`.

<a name="celestialobjectfrom_dict"></a>
<a name="from_dict"></a>
#### `stellarium_lite.CelestialObject.from_dict`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
@classmethod
CelestialObject.from_dict(cls, record: dict) -> CelestialObject
```

Build a [`CelestialObject`](#celestialobject) from a raw catalog record.

**Parameters:**

- `record`: A mapping with at least `name`, `ra`, `dec` keys.

**Returns:**

A new instance of `cls`.

<a name="celestialobjectangular_separation"></a>
<a name="angular_separation"></a>
#### `stellarium_lite.CelestialObject.angular_separation`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

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

**Parameters:**

- `a`: The first object.
- `b`: The second object.

**Returns:**

Separation `d` in degrees.

<a name="star"></a>
### `stellarium_lite.Star`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
Star(CelestialObject)
```

A single star, extending `CelestialObject` with a magnitude.

See also `catalog` for how instances are typically constructed via
[`load_catalog`](#load_catalog).

<a name="observation"></a>
## `stellarium_lite.observation`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

<a name="observationmax_magnitude"></a>
<a name="max_magnitude"></a>
### `stellarium_lite.observation.MAX_MAGNITUDE`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
MAX_MAGNITUDE: float = 30.0
```

<a name="observationplan_session"></a>
<a name="plan_session"></a>
### `stellarium_lite.observation.plan_session`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

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

**Parameters:**

- `objects`: Candidate [`CelestialObject`](#celestialobject) instances.
- `start_at`: Priority tier to begin scheduling from.

**Returns:**

A list of objects in observation order.

<a name="observationobservablemixin"></a>
<a name="observablemixin"></a>
### `stellarium_lite.observation.ObservableMixin`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
ObservableMixin(ABC)
```

Abstract interface for anything that can report its own visibility.

> [!IMPORTANT]
>
> Subclasses **must** implement [`observe`](#observe); the base class raises
> `NotImplementedError` otherwise via the `abstractmethod` machinery.

> :heavy_plus_sign: Added in version 0.1.0

<a name="observationobservablemixinobserve"></a>
<a name="observablemixinobserve"></a>
<a name="observe"></a>
#### `stellarium_lite.observation.ObservableMixin.observe`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
@abstractmethod
ObservableMixin.observe(self) -> Observation
```

Perform an observation and return the resulting record.

**Returns:**

A new [`Observation`](#observation).

<a name="observationvariablestar"></a>
<a name="variablestar"></a>
### `stellarium_lite.observation.VariableStar`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

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

**Parameters:**

- `period_days`: Approximate variability period, in days.

<a name="observationhybridobject"></a>
<a name="hybridobject"></a>
### `stellarium_lite.observation.HybridObject`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
HybridObject(CelestialObject, ObservableMixin)
```

An object that is both a [`CelestialObject`](#celestialobject) and
[`ObservableMixin`](#observablemixin).

> **Hint:**
>
> This class mostly exists to exercise multiple inheritance; prefer
> [`Star`](#star) or [`VariableStar`](#variablestar) for real use.

<a name="observationhybridobjectobserve"></a>
<a name="hybridobjectobserve"></a>
<a name="observe"></a>
#### `stellarium_lite.observation.HybridObject.observe`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
HybridObject.observe(self) -> Observation
```

Perform an observation of this hybrid object.

**Returns:**

A new [`Observation`](#observation) record.

<a name="observationobservation"></a>
<a name="observation"></a>
### `stellarium_lite.observation.Observation`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
@dataclass
Observation(object)
```

A single recorded observation.

**Parameters:**

- `object_name`: Name of the object observed, e.g. `"M31"`.
- `magnitude`: Estimated visual magnitude at time of observation.
- `tags`: Free-form labels attached to this observation.

<a name="observationobservationschema_version"></a>
<a name="observationschema_version"></a>
<a name="schema_version"></a>
#### `stellarium_lite.observation.Observation.schema_version`

<sup>[Back to top](#stellarium_lite-documentation)</sup>

```Python
Observation.schema_version: ClassVar[int] = 1
```
