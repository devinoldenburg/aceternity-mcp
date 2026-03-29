"""Recommendation engine for Aceternity UI components.

Uses scoring metadata and keyword analysis to recommend components
for specific project types, page sections, and design goals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import AceternityComponent
from .registry import Registry
from .search import _text_relevance, _tokenise

# ---------------------------------------------------------------------------
# Recommendation result
# ---------------------------------------------------------------------------


@dataclass
class Recommendation:
    """A component recommendation with a numeric fit score and rationale."""

    component: AceternityComponent
    fit_score: float
    reasons: list[str]


# ---------------------------------------------------------------------------
# Project archetype profiles
# ---------------------------------------------------------------------------

# Each archetype defines which scoring dimensions matter most and which
# categories / tags are preferred.

_ARCHETYPES: dict[str, dict[str, Any]] = {
    "saas-landing": {
        "description": "SaaS or product landing page",
        "preferred_categories": [
            "hero-sections",
            "backgrounds",
            "text-effects",
            "call-to-action",
            "testimonials",
            "pricing",
            "navigation",
            "feature-sections",
            "cards",
        ],
        "preferred_tags": [
            "hero",
            "landing",
            "premium",
            "animated",
            "gradient",
            "cta",
            "testimonial",
            "pricing",
            "saas",
        ],
        "score_weights": {
            "landing_page_fit": 3.0,
            "visual_intensity": 1.5,
            "animation_intensity": 1.0,
            "customization_ease": 1.0,
        },
    },
    "dashboard": {
        "description": "Admin dashboard or internal tool",
        "preferred_categories": [
            "navigation",
            "sidebar",
            "layout",
            "cards",
            "forms",
            "loaders",
            "utilities",
        ],
        "preferred_tags": [
            "sidebar",
            "navbar",
            "grid",
            "layout",
            "form",
            "loader",
            "minimal",
            "responsive",
            "dashboard",
        ],
        "score_weights": {
            "dashboard_fit": 3.0,
            "layout_importance": 2.0,
            "customization_ease": 1.5,
            "performance_impact": -1.0,  # lower is better
        },
    },
    "portfolio": {
        "description": "Personal portfolio or creative showcase",
        "preferred_categories": [
            "hero-sections",
            "cards",
            "text-effects",
            "backgrounds",
            "scroll-effects",
            "3d-effects",
        ],
        "preferred_tags": [
            "3d",
            "parallax",
            "scroll",
            "reveal",
            "creative",
            "portfolio",
            "showcase",
            "animated",
            "premium",
        ],
        "score_weights": {
            "visual_intensity": 2.5,
            "animation_intensity": 2.0,
            "landing_page_fit": 1.5,
        },
    },
    "marketing": {
        "description": "Marketing or agency website",
        "preferred_categories": [
            "hero-sections",
            "testimonials",
            "pricing",
            "call-to-action",
            "feature-sections",
            "navigation",
            "backgrounds",
            "text-effects",
        ],
        "preferred_tags": [
            "hero",
            "cta",
            "testimonial",
            "pricing",
            "premium",
            "animated",
            "gradient",
            "marketing",
        ],
        "score_weights": {
            "landing_page_fit": 2.5,
            "visual_intensity": 2.0,
            "animation_intensity": 1.5,
            "customization_ease": 1.0,
        },
    },
    "minimal": {
        "description": "Clean, minimal, content-focused site",
        "preferred_categories": [
            "layout",
            "text-effects",
            "navigation",
            "forms",
            "cards",
        ],
        "preferred_tags": [
            "minimal",
            "clean",
            "subtle",
            "simple",
            "responsive",
            "text",
            "content",
        ],
        "score_weights": {
            "customization_ease": 2.0,
            "layout_importance": 2.0,
            "visual_intensity": -1.0,  # lower is better for minimal
            "animation_intensity": -1.0,
        },
    },
}


# ---------------------------------------------------------------------------
# Recommender
# ---------------------------------------------------------------------------


class Recommender:
    """Generates component recommendations based on project context."""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry

    # -- public API -----------------------------------------------------------

    def recommend_for_use_case(
        self,
        description: str,
        *,
        max_results: int = 10,
        include_pro: bool = True,
    ) -> list[Recommendation]:
        """Recommend components for a free-text use-case description.

        Combines keyword search relevance with scoring metadata.
        """
        tokens = _tokenise(description)
        recommendations: list[Recommendation] = []

        # Detect archetype
        archetype = self._detect_archetype(description)
        arch_config = _ARCHETYPES.get(archetype, {})
        score_weights = arch_config.get("score_weights", {})
        preferred_cats = set(arch_config.get("preferred_categories", []))
        preferred_tags = set(arch_config.get("preferred_tags", []))

        for comp in self._registry.all_components():
            if not include_pro and comp.is_pro:
                continue

            reasons: list[str] = []
            fit = 0.0

            # Text relevance
            text_score = 0.0
            text_score += _text_relevance(tokens, comp.name, weight=2.0)
            text_score += _text_relevance(tokens, comp.summary, weight=1.5)
            text_score += _text_relevance(tokens, comp.detailed_description, weight=1.0)
            text_score += _text_relevance(tokens, " ".join(comp.purpose), weight=1.5)
            text_score += _text_relevance(tokens, " ".join(comp.tags), weight=1.5)
            text_score += _text_relevance(tokens, " ".join(comp.category), weight=1.0)
            if text_score > 0:
                fit += text_score
                reasons.append("Matches use-case keywords")

            # Category affinity
            cat_overlap = preferred_cats.intersection(set(comp.category))
            if cat_overlap:
                fit += len(cat_overlap) * 1.5
                reasons.append(f"Category match: {', '.join(cat_overlap)}")

            # Tag affinity
            tag_overlap = preferred_tags.intersection(set(t.lower() for t in comp.tags))
            if tag_overlap:
                fit += len(tag_overlap) * 1.0
                reasons.append(f"Tag match: {', '.join(tag_overlap)}")

            # Score-based fit
            s = comp.scores
            for dim, weight in score_weights.items():
                val = getattr(s, dim, 5)
                if weight > 0:
                    fit += (val / 10.0) * weight
                else:
                    # Negative weight = prefer *lower* values
                    fit += ((10 - val) / 10.0) * abs(weight)

            if fit > 0:
                recommendations.append(
                    Recommendation(
                        component=comp,
                        fit_score=round(fit, 3),
                        reasons=reasons,
                    )
                )

        recommendations.sort(key=lambda r: r.fit_score, reverse=True)
        return recommendations[:max_results]

    def recommend_combination(
        self,
        description: str,
        *,
        max_results: int = 8,
        include_pro: bool = True,
    ) -> dict[str, list[Recommendation]]:
        """Recommend a full page combination: navbar, hero, features, etc.

        Returns a dict keyed by section role with recommended components.
        """
        section_queries = {
            "navigation": f"navbar navigation header for {description}",
            "hero": f"hero section header for {description}",
            "features": f"feature section display for {description}",
            "background": f"background effect for {description}",
            "cards": f"card component for {description}",
            "cta": f"call to action section for {description}",
            "footer": f"footer navigation for {description}",
            "text-effect": f"text animation effect for {description}",
        }

        result: dict[str, list[Recommendation]] = {}
        for section, query in section_queries.items():
            recs = self.recommend_for_use_case(
                query, max_results=3, include_pro=include_pro
            )
            if recs:
                result[section] = recs

        return result

    def match_to_project(
        self,
        project_description: str,
        *,
        max_results: int = 15,
        include_pro: bool = True,
    ) -> list[Recommendation]:
        """Match components to a whole project description.

        Similar to :meth:`recommend_for_use_case` but also boosts
        layout-critical components.
        """
        recs = self.recommend_for_use_case(
            project_description,
            max_results=max_results * 2,
            include_pro=include_pro,
        )

        # Boost layout-important components slightly
        for rec in recs:
            if rec.component.scores.layout_importance >= 7:
                rec.fit_score += 0.5
                rec.reasons.append("High layout importance")

        recs.sort(key=lambda r: r.fit_score, reverse=True)
        return recs[:max_results]

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _detect_archetype(description: str) -> str:
        """Simple keyword-based archetype detection."""
        desc_lower = description.lower()

        archetype_keywords: dict[str, list[str]] = {
            "saas-landing": ["saas", "startup", "product", "app landing", "software"],
            "dashboard": ["dashboard", "admin", "panel", "internal", "crm", "erp"],
            "portfolio": ["portfolio", "personal", "creative", "showcase", "freelance"],
            "marketing": ["marketing", "agency", "corporate", "business", "company"],
            "minimal": ["minimal", "clean", "simple", "blog", "content"],
        }

        best_match = ""
        best_count = 0
        for archetype, keywords in archetype_keywords.items():
            count = sum(1 for kw in keywords if kw in desc_lower)
            if count > best_count:
                best_count = count
                best_match = archetype

        return best_match or "saas-landing"  # default

    @staticmethod
    def available_archetypes() -> dict[str, str]:
        """Return mapping of archetype slug to description."""
        return {k: v["description"] for k, v in _ARCHETYPES.items()}
