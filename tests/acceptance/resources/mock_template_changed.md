# `stellarium_lite` starting guide

This documents guides you through the most important features of the package.
It also serves as a documentation for the most important members of `stelarium_lite`.
Note that this package does not actually work!

::: stellarium_lite
    options:
        include_members: false
        heading_level: 2

## Getting started

Most often, you will want to load a catalog from one of the well established
galaxy catalogs or surveys. For this purpose, `stellarium_lite` provides the
versatile function [`load_catalog`](#load_catalog). This and the [`CelestialObject`](#celestialbody)
class are documented below:

::: stellarium_lite.load_catalog
    options:
        heading_level: 3

::: stellarium_lite.CelestialObject
    options:
        heading_level: 3
        include_members: true

## Utilities for planning observations

To facilitate the planning and execution of surveys and observations, `stellarium_lite`
also provides a package `observation` that provides useful utilities for this
purpose:

::: stellarium_lite.observation
    options:
        include_members: true
        heading_level: 3

## Further resources

This guide is a small introduction into the most important members of `stellarium_lite`.
