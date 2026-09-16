..
   SPDX-FileCopyrightText: Copyright DB InfraGO AG
   SPDX-License-Identifier: Apache-2.0

Migrating from |project| v0.7.x to v0.8.x
=========================================

This page lists the most important differences that users should be aware of
when upgrading to v0.8.x from earlier versions of |project|.

Deprecated diagram rendering properties
---------------------------------------

- The ``as_<format>`` properties (e.g., ``as_svg``, ``as_png``) on ``Diagram``
  objects have been **deprecated** in favor of the more flexible ``render()``
  method.

  **Before (deprecated):**

  .. code-block:: python

     diagram = model.diagrams.by_name("My Diagram")
     svg_data = diagram.as_svg
     png_data = diagram.as_png

  **After (recommended):**

  .. code-block:: python

     diagram = model.diagrams.by_name("My Diagram")
     svg_data = diagram.render("svg")
     png_data = diagram.render("png")

  Note that this does not change any of the semantics behind diagram rendering.
  Specifically, `render()` calls are cached across consecutive calls with the
  same render parameters. The following code still renders the diagram only
  once and converts this rendered diagram into the different formats:

  .. code-block:: python

     diagram = model.diagrams.by_name("My Diagram")
     raw_svg = diagram.render("svg")
     datauri = diagram.render("datauri_svg")
     png = diagram.render("png")
