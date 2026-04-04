"""Search and filter engine for the Aceternity component registry.

Provides text-based search across names, descriptions, tags, and categories
as well as structured filtering by category, tag, and score thresholds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AceternityComponent
    from .registry import Registry

# ---------------------------------------------------------------------------
# Search result wrapper
# ---------------------------------------------------------------------------


@dataclass
class SearchResult:
    """A single search hit with relevance score."""

    component: AceternityComponent
    relevance: float = 0.0


# ---------------------------------------------------------------------------
# Tokenisation helpers
# ---------------------------------------------------------------------------

_SPLIT_RE = re.compile(r"[\s\-_/,;:.!?]+")


def _tokenise(text: str) -> set[str]:
    """Split text into lowercase tokens."""
    return {t for t in _SPLIT_RE.split(text.lower()) if len(t) >= 2}


def _text_relevance(query_tokens: set[str], text: str, weight: float = 1.0) -> float:
    """Score how many query tokens appear in *text*."""
    if not query_tokens or not text:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for t in query_tokens if t in text_lower)
    return (hits / len(query_tokens)) * weight


# ---------------------------------------------------------------------------
# Search engine
# ---------------------------------------------------------------------------


class SearchEngine:
    """Stateless search layer over a :class:`Registry`."""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry

    # -- full-text search -----------------------------------------------------

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        tags: list[str] | None = None,
        max_results: int = 20,
        include_pro: bool = True,
    ) -> list[SearchResult]:
        """Search components by free-text *query* with optional filters.

        Scoring weights:
          - name match:          3.0
          - tag match:           2.5
          - category match:      2.0
          - summary match:       1.5
          - description match:   1.0
          - purpose match:       1.0
          - behaviour match:     0.8
          - visual chars match:  0.8
        """
        tokens = _tokenise(query)
        results: list[SearchResult] = []

        for comp in self._registry.all_components():
            if not include_pro and comp.is_pro:
                continue

            # Apply hard filters first
            if category and category not in comp.category:
                continue
            if tags and not {t.lower() for t in tags}.intersection(
                {t.lower() for t in comp.tags}
            ):
                continue

            score = 0.0
            score += _text_relevance(tokens, comp.name, weight=3.0)
            score += _text_relevance(tokens, comp.slug, weight=2.5)
            score += _text_relevance(tokens, " ".join(comp.tags), weight=2.5)
            score += _text_relevance(tokens, " ".join(comp.category), weight=2.0)
            score += _text_relevance(tokens, comp.summary, weight=1.5)
            score += _text_relevance(tokens, comp.detailed_description, weight=1.0)
            score += _text_relevance(tokens, " ".join(comp.purpose), weight=1.0)
            score += _text_relevance(tokens, " ".join(comp.behavior), weight=0.8)
            score += _text_relevance(
                tokens, " ".join(comp.visual_characteristics), weight=0.8
            )

            if score > 0:
                results.append(SearchResult(component=comp, relevance=round(score, 3)))

        results.sort(key=lambda r: r.relevance, reverse=True)
        return results[:max_results]

    # -- structured filters ---------------------------------------------------

    def filter_by_category(
        self, category_slug: str, *, include_pro: bool = True
    ) -> list[AceternityComponent]:
        """Return all components in a given category."""
        comps = self._registry.components_in_category(category_slug)
        if not include_pro:
            comps = [c for c in comps if not c.is_pro]
        return sorted(comps, key=lambda c: c.name)

    def filter_by_tags(
        self, tags: list[str], *, match_all: bool = False, include_pro: bool = True
    ) -> list[AceternityComponent]:
        """Return components matching the given tags.

        When *match_all* is True every tag must be present; otherwise any
        single tag match is sufficient.
        """
        tag_set = {t.lower() for t in tags}
        out: list[AceternityComponent] = []
        for comp in self._registry.all_components():
            if not include_pro and comp.is_pro:
                continue
            comp_tags = {t.lower() for t in comp.tags}
            if match_all:
                if tag_set.issubset(comp_tags):
                    out.append(comp)
            elif tag_set.intersection(comp_tags):
                out.append(comp)
        return sorted(out, key=lambda c: c.name)

    def filter_by_scores(
        self,
        *,
        min_visual_intensity: int | None = None,
        max_visual_intensity: int | None = None,
        min_animation_intensity: int | None = None,
        max_animation_intensity: int | None = None,
        min_landing_page_fit: int | None = None,
        min_dashboard_fit: int | None = None,
        max_performance_impact: int | None = None,
        min_customization_ease: int | None = None,
        include_pro: bool = True,
    ) -> list[AceternityComponent]:
        """Filter by numeric scoring thresholds."""
        out: list[AceternityComponent] = []
        for comp in self._registry.all_components():
            if not include_pro and comp.is_pro:
                continue
            s = comp.scores
            if (
                min_visual_intensity is not None
                and s.visual_intensity < min_visual_intensity
            ):
                continue
            if (
                max_visual_intensity is not None
                and s.visual_intensity > max_visual_intensity
            ):
                continue
            if (
                min_animation_intensity is not None
                and s.animation_intensity < min_animation_intensity
            ):
                continue
            if (
                max_animation_intensity is not None
                and s.animation_intensity > max_animation_intensity
            ):
                continue
            if (
                min_landing_page_fit is not None
                and s.landing_page_fit < min_landing_page_fit
            ):
                continue
            if min_dashboard_fit is not None and s.dashboard_fit < min_dashboard_fit:
                continue
            if (
                max_performance_impact is not None
                and s.performance_impact > max_performance_impact
            ):
                continue
            if (
                min_customization_ease is not None
                and s.customization_ease < min_customization_ease
            ):
                continue
            out.append(comp)
        return sorted(out, key=lambda c: c.name)
