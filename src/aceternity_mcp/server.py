"""Aceternity UI MCP Server.

Exposes the enriched component registry through the Model Context Protocol
so that AI agents can search, understand, recommend, and install Aceternity
UI components with full structured knowledge.

Tools exposed:
  - list_components        List all or filtered components
  - list_categories        List all categories
  - search_components      Full-text + filter search
  - get_component          Full detail for one component
  - get_category           Components in a category
  - recommend_components   Use-case-based recommendations
  - recommend_combination  Full page section recommendations
  - match_components_to_project  Project-level matching
  - install_component      Installation command and steps
  - filter_by_scores       Filter by numeric scoring thresholds
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .models import AceternityComponent
from .recommender import Recommender
from .registry import Registry
from .search import SearchEngine

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "aceternity-ui",
    instructions=(
        "Aceternity UI MCP Registry and Integration Server. "
        "Provides structured access to 100+ Aceternity UI components with "
        "rich descriptions, search, recommendations, and install commands. "
        "Use list_components or search_components to discover components, "
        "get_component for full details, recommend_components for use-case "
        "matching, and install_component for installation instructions."
    ),
)

# Global singletons — initialised in main()
_registry = Registry()
_search: SearchEngine | None = None
_recommender: Recommender | None = None


def _ensure_loaded() -> None:
    global _search, _recommender
    if not _registry.is_loaded:
        _registry.load()
        _search = SearchEngine(_registry)
        _recommender = Recommender(_registry)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _component_summary(comp: AceternityComponent) -> dict[str, Any]:
    """Return a compact summary dict for listings."""
    return {
        "slug": comp.slug,
        "name": comp.name,
        "category": comp.category,
        "tags": comp.tags,
        "summary": comp.summary,
        "isPro": comp.is_pro,
    }


def _component_full(comp: AceternityComponent) -> dict[str, Any]:
    """Return the complete component dict."""
    return comp.to_dict()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_components(
    category: str | None = None,
    include_pro: bool = True,
) -> str:
    """List all available Aceternity UI components.

    Optionally filter by category slug.  Returns a compact summary for
    each component (slug, name, category, tags, summary).

    Args:
        category: Optional category slug (e.g. "hero-sections")
        include_pro: Include pro-only components (default: True)
    """
    _ensure_loaded()
    if category:
        comps = _registry.components_in_category(category)
    else:
        comps = _registry.all_components()

    if not include_pro:
        comps = [c for c in comps if not c.is_pro]

    result = {
        "total": len(comps),
        "components": [_component_summary(c) for c in comps],
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def list_categories() -> str:
    """List all component categories with descriptions and component counts."""
    _ensure_loaded()
    cats = _registry.all_categories()
    result = {
        "total": len(cats),
        "categories": [
            {
                **cat.to_dict(),
                "componentCount": len(cat.component_slugs),
            }
            for cat in cats
        ],
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def search_components(
    query: str,
    category: str | None = None,
    tags: str | None = None,
    max_results: int = 15,
    include_pro: bool = True,
) -> str:
    """Search components by text query with optional filters.

    Searches across names, descriptions, tags, categories, purposes,
    behaviors, and visual characteristics.  Results are ranked by
    relevance.

    Args:
        query: Search query (e.g. "animated hero", "dark card")
        category: Optional category slug to narrow results
        tags: Optional comma-separated tags to filter by
        max_results: Max results to return (default 15)
        include_pro: Include pro components (default True)
    """
    _ensure_loaded()
    assert _search is not None

    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    results = _search.search(
        query,
        category=category,
        tags=tag_list,
        max_results=max_results,
        include_pro=include_pro,
    )

    output = {
        "query": query,
        "total": len(results),
        "results": [
            {
                "relevance": r.relevance,
                **_component_summary(r.component),
            }
            for r in results
        ],
    }
    return json.dumps(output, indent=2)


@mcp.tool()
def get_component(slug: str) -> str:
    """Get the full detailed entry for a single component.

    Returns ALL metadata including the 60+ word detailed description,
    purpose, behavior, visual characteristics, dependencies, install
    commands, props, compatibility, and scoring.

    Args:
        slug: Component slug (e.g. "spotlight", "bento-grid", "hero-parallax")
    """
    _ensure_loaded()
    comp = _registry.get_component(slug)
    if comp is None:
        return json.dumps({"error": f"Component '{slug}' not found"})
    return json.dumps(_component_full(comp), indent=2)


@mcp.tool()
def get_category(slug: str) -> str:
    """Get all components in a specific category.

    Returns the category info and full summaries of every component
    that belongs to it.

    Args:
        slug: Category slug (e.g. "hero-sections", "backgrounds", "cards")
    """
    _ensure_loaded()
    cat = _registry.get_category(slug)
    if cat is None:
        return json.dumps({"error": f"Category '{slug}' not found"})

    comps = _registry.components_in_category(slug)
    result = {
        **cat.to_dict(),
        "componentCount": len(comps),
        "componentDetails": [_component_summary(c) for c in comps],
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def recommend_components(
    description: str,
    max_results: int = 10,
    include_pro: bool = True,
) -> str:
    """Recommend components for a specific use case or design goal.

    Analyses the description against component metadata, categories,
    tags, and scoring dimensions to find the best matches.

    Example descriptions:
      - "premium AI SaaS landing page with dark theme"
      - "subtle background effect for a login page"
      - "testimonial section for a marketing site"
      - "animated hero for a startup landing page"

    Args:
        description: Free-text description of what you need
        max_results: Number of recommendations to return (default 10)
        include_pro: Include pro components (default True)
    """
    _ensure_loaded()
    assert _recommender is not None

    recs = _recommender.recommend_for_use_case(
        description,
        max_results=max_results,
        include_pro=include_pro,
    )

    output = {
        "description": description,
        "total": len(recs),
        "recommendations": [
            {
                "fitScore": r.fit_score,
                "reasons": r.reasons,
                **_component_summary(r.component),
            }
            for r in recs
        ],
    }
    return json.dumps(output, indent=2)


@mcp.tool()
def recommend_combination(
    description: str,
    include_pro: bool = True,
) -> str:
    """Recommend a full-page component combination.

    Given a project or page description, returns recommended components
    for each page section: navigation, hero, features, background,
    cards, CTA, footer, and text effects.

    Args:
        description: Description of the page or project (e.g. "AI SaaS landing page")
        include_pro: Include pro components (default True)
    """
    _ensure_loaded()
    assert _recommender is not None

    combo = _recommender.recommend_combination(
        description,
        include_pro=include_pro,
    )

    output: dict[str, Any] = {"description": description, "sections": {}}
    for section, recs in combo.items():
        output["sections"][section] = [
            {
                "fitScore": r.fit_score,
                "reasons": r.reasons,
                **_component_summary(r.component),
            }
            for r in recs
        ]

    return json.dumps(output, indent=2)


@mcp.tool()
def match_components_to_project(
    project_description: str,
    max_results: int = 15,
    include_pro: bool = True,
) -> str:
    """Match components to a whole project description.

    Similar to recommend_components but biased toward layout-critical
    components and returns more results for full project planning.

    Args:
        project_description: Project description (e.g. "dashboard with dark mode")
        max_results: Number of results (default 15)
        include_pro: Include pro components (default True)
    """
    _ensure_loaded()
    assert _recommender is not None

    recs = _recommender.match_to_project(
        project_description,
        max_results=max_results,
        include_pro=include_pro,
    )

    output = {
        "projectDescription": project_description,
        "total": len(recs),
        "matchedComponents": [
            {
                "fitScore": r.fit_score,
                "reasons": r.reasons,
                **_component_summary(r.component),
            }
            for r in recs
        ],
    }
    return json.dumps(output, indent=2)


@mcp.tool()
def install_component(slug: str) -> str:
    """Get full installation instructions for a component.

    Returns the install command, dependencies, registry URL,
    documentation link, and step-by-step setup instructions.

    Args:
        slug: Component slug (e.g. "spotlight", "sidebar", "bento-grid")
    """
    _ensure_loaded()
    comp = _registry.get_component(slug)
    if comp is None:
        return json.dumps({"error": f"Component '{slug}' not found"})

    steps: list[str] = [
        f"1. Run: {comp.install_command}",
        "2. Import the component into your React/Next.js file",
        "3. Ensure Tailwind CSS is configured in your project",
    ]

    if comp.compatibility.framer_motion:
        steps.append(
            "4. Ensure Framer Motion (motion) is installed: npm install motion"
        )
    if comp.dependencies:
        deps_str = " ".join(comp.dependencies)
        steps.append(f"5. Verify dependencies are present: {deps_str}")

    result: dict[str, Any] = {
        "slug": comp.slug,
        "name": comp.name,
        "installCommand": comp.install_command,
        "registryUrl": comp.registry_url,
        "docsUrl": comp.docs_url,
        "dependencies": comp.dependencies,
        "compatibility": comp.compatibility.to_dict(),
        "steps": steps,
    }

    return json.dumps(result, indent=2)


@mcp.tool()
def filter_by_scores(
    min_visual_intensity: int | None = None,
    max_visual_intensity: int | None = None,
    min_animation_intensity: int | None = None,
    max_animation_intensity: int | None = None,
    min_landing_page_fit: int | None = None,
    min_dashboard_fit: int | None = None,
    max_performance_impact: int | None = None,
    min_customization_ease: int | None = None,
    include_pro: bool = True,
) -> str:
    """Filter components by numeric scoring thresholds (1-10 scale).

    All parameters are optional.  Only components passing every
    specified threshold are returned.

    Scoring dimensions:
      - visualIntensity:     How visually dominant (1=subtle, 10=dramatic)
      - animationIntensity:  How much animation/motion (1=static, 10=heavy)
      - layoutImportance:    How critical to page structure (1=decorative, 10=essential)
      - customizationEase:   How easy to customise (1=rigid, 10=very flexible)
      - landingPageFit:      Suitability for landing pages (1=poor, 10=perfect)
      - dashboardFit:        Suitability for dashboards (1=poor, 10=perfect)
      - performanceImpact:   Runtime cost (1=lightweight, 10=heavy)

    Args:
        min_visual_intensity: Minimum visual intensity (1-10)
        max_visual_intensity: Maximum visual intensity (1-10)
        min_animation_intensity: Minimum animation intensity (1-10)
        max_animation_intensity: Maximum animation intensity (1-10)
        min_landing_page_fit: Minimum landing page fit (1-10)
        min_dashboard_fit: Minimum dashboard fit (1-10)
        max_performance_impact: Maximum performance impact (1-10)
        min_customization_ease: Minimum customization ease (1-10)
        include_pro: Include pro components (default True)
    """
    _ensure_loaded()
    assert _search is not None

    comps = _search.filter_by_scores(
        min_visual_intensity=min_visual_intensity,
        max_visual_intensity=max_visual_intensity,
        min_animation_intensity=min_animation_intensity,
        max_animation_intensity=max_animation_intensity,
        min_landing_page_fit=min_landing_page_fit,
        min_dashboard_fit=min_dashboard_fit,
        max_performance_impact=max_performance_impact,
        min_customization_ease=min_customization_ease,
        include_pro=include_pro,
    )

    result = {
        "total": len(comps),
        "components": [_component_summary(c) for c in comps],
    }
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server over stdio."""
    _ensure_loaded()
    logger.info(
        "Aceternity MCP server ready — %d components, %d categories",
        _registry.component_count,
        _registry.category_count,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
