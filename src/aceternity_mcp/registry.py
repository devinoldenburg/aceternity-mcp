"""Registry loader and manager.

Reads the local ``registry/`` directory tree and provides fast in-memory
access to all components and categories.  The registry is loaded once at
server startup and kept in memory for the lifetime of the process.
"""

from __future__ import annotations

import logging
from pathlib import Path

from .models import AceternityComponent, Category

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Locate the registry directory
# ---------------------------------------------------------------------------


def _find_registry_dir() -> Path:
    """Walk upward from this file to find the ``registry/`` directory.

    Search order:
      1. Sibling of the package directory (source checkout)
      2. ``$PWD/registry``
      3. Installed shared-data location (hatch installs to share/)
      4. pipx shared-data location
    """
    # Source checkout: repo_root/registry
    pkg_dir = Path(__file__).resolve().parent  # src/aceternity_mcp/
    repo_root = pkg_dir.parent.parent  # repo root
    candidate = repo_root / "registry"
    if candidate.is_dir():
        return candidate

    # CWD fallback
    cwd_candidate = Path.cwd() / "registry"
    if cwd_candidate.is_dir():
        return cwd_candidate

    # pipx shared-data location: <venv>/share/aceternity-mcp/registry
    venv_dir = pkg_dir.parent.parent.parent  # pipx venv root
    pipx_candidate = venv_dir / "share" / "aceternity-mcp" / "registry"
    if pipx_candidate.is_dir():
        return pipx_candidate

    raise FileNotFoundError(
        "Cannot locate the registry/ directory.  "
        "Make sure you run the server from the repository root or that "
        "the registry directory is accessible."
    )


# ---------------------------------------------------------------------------
# Registry class
# ---------------------------------------------------------------------------


class Registry:
    """In-memory component and category store."""

    def __init__(self) -> None:
        self._components: dict[str, AceternityComponent] = {}
        self._categories: dict[str, Category] = {}
        self._loaded = False

    # -- loading --------------------------------------------------------------

    def load(self, registry_dir: Path | None = None) -> None:
        """Load all JSON files from the registry directory tree."""
        if registry_dir is None:
            registry_dir = _find_registry_dir()

        logger.info("Loading registry from %s", registry_dir)

        # Load components
        components_dir = registry_dir / "components"
        if components_dir.is_dir():
            for path in sorted(components_dir.glob("*.json")):
                try:
                    comp = AceternityComponent.from_json_file(path)
                    self._components[comp.slug] = comp
                except Exception:
                    logger.warning("Failed to load component %s", path, exc_info=True)

        # Load categories
        categories_dir = registry_dir / "categories"
        if categories_dir.is_dir():
            for path in sorted(categories_dir.glob("*.json")):
                try:
                    cat = Category.from_json_file(path)
                    self._categories[cat.slug] = cat
                except Exception:
                    logger.warning("Failed to load category %s", path, exc_info=True)

        self._loaded = True
        logger.info(
            "Registry loaded: %d components, %d categories",
            len(self._components),
            len(self._categories),
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # -- accessors ------------------------------------------------------------

    @property
    def component_count(self) -> int:
        return len(self._components)

    @property
    def category_count(self) -> int:
        return len(self._categories)

    def all_components(self) -> list[AceternityComponent]:
        """Return all components sorted by name."""
        return sorted(self._components.values(), key=lambda c: c.name)

    def all_categories(self) -> list[Category]:
        """Return all categories sorted by name."""
        return sorted(self._categories.values(), key=lambda c: c.name)

    def get_component(self, slug: str) -> AceternityComponent | None:
        """Look up a component by slug."""
        return self._components.get(slug)

    def get_category(self, slug: str) -> Category | None:
        """Look up a category by slug."""
        return self._categories.get(slug)

    def components_in_category(self, category_slug: str) -> list[AceternityComponent]:
        """Return all components belonging to a category."""
        return [c for c in self._components.values() if category_slug in c.category]

    def component_slugs(self) -> list[str]:
        """All known component slugs."""
        return sorted(self._components.keys())

    def category_slugs(self) -> list[str]:
        """All known category slugs."""
        return sorted(self._categories.keys())
