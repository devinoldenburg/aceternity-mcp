#!/usr/bin/env python3
"""Validate local Aceternity registry quality.

Checks:
- Required fields exist for every component
- detailedDescription has at least 60 words
- install command uses @aceternity namespace or registry URL
- referenced categories exist
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
COMPONENTS = REGISTRY / "components"
CATEGORIES = REGISTRY / "categories"


REQUIRED_FIELDS = {
    "slug",
    "name",
    "category",
    "tags",
    "summary",
    "detailedDescription",
    "purpose",
    "behavior",
    "visualCharacteristics",
    "dependencies",
    "installCommand",
    "registryUrl",
    "docsUrl",
    "previewAvailable",
    "compatibility",
    "scores",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    category_slugs = {p.stem for p in CATEGORIES.glob("*.json")}
    if not category_slugs:
        errors.append("No category files found in registry/categories")

    component_files = sorted(COMPONENTS.glob("*.json"))
    if not component_files:
        errors.append("No component files found in registry/components")

    seen_slugs: set[str] = set()

    for path in component_files:
        data = _load(path)
        slug = data.get("slug", path.stem)

        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            errors.append(f"{slug}: missing required fields: {sorted(missing)}")

        if slug in seen_slugs:
            errors.append(f"Duplicate slug found: {slug}")
        seen_slugs.add(slug)

        desc_words = len(str(data.get("detailedDescription", "")).split())
        if desc_words < 60:
            errors.append(f"{slug}: detailedDescription has {desc_words} words (< 60)")

        install = str(data.get("installCommand", ""))
        if (
            "@aceternity/" not in install
            and "ui.aceternity.com/registry/" not in install
        ):
            errors.append(
                f"{slug}: installCommand is not namespaced or registry URL based"
            )

        cats = data.get("category", [])
        if not isinstance(cats, list) or not cats:
            errors.append(f"{slug}: category must be a non-empty list")
        else:
            for cat in cats:
                if cat not in category_slugs:
                    errors.append(f"{slug}: category '{cat}' has no category file")

    if errors:
        print("Registry validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(
        f"Registry validation passed: {len(component_files)} components, "
        f"{len(category_slugs)} categories"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
