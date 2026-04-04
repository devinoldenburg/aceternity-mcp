"""Recommendation engine for Aceternity UI components.

Uses scoring metadata and keyword analysis to recommend components
for specific project types, page sections, and design goals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .search import _text_relevance, _tokenise

if TYPE_CHECKING:
    from .models import AceternityComponent
    from .registry import Registry

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
# Page layout result
# ---------------------------------------------------------------------------


@dataclass
class LayoutSection:
    """A single section in a generated page layout."""

    name: str
    role: str
    description: str
    components: list[Recommendation] = field(default_factory=list)
    priority: int = 1  # 1 = must-have, 2 = recommended, 3 = optional


@dataclass
class PageLayout:
    """A complete page layout with ordered sections and metadata."""

    page_type: str
    description: str
    sections: list[LayoutSection] = field(default_factory=list)
    all_dependencies: list[str] = field(default_factory=list)
    install_commands: list[str] = field(default_factory=list)
    total_components: int = 0
    estimated_performance: str = "medium"


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
    "ecommerce": {
        "description": "E-commerce or product store",
        "preferred_categories": [
            "cards",
            "navigation",
            "hero-sections",
            "layout",
            "forms",
            "feature-sections",
        ],
        "preferred_tags": [
            "grid",
            "card",
            "product",
            "gallery",
            "image",
            "responsive",
            "layout",
            "carousel",
        ],
        "score_weights": {
            "layout_importance": 2.5,
            "customization_ease": 2.0,
            "dashboard_fit": 1.0,
            "performance_impact": -1.5,
        },
    },
    "documentation": {
        "description": "Documentation or knowledge base site",
        "preferred_categories": [
            "navigation",
            "layout",
            "text-effects",
            "sidebars",
        ],
        "preferred_tags": [
            "sidebar",
            "navbar",
            "text",
            "layout",
            "minimal",
            "responsive",
            "content",
        ],
        "score_weights": {
            "layout_importance": 3.0,
            "customization_ease": 2.0,
            "performance_impact": -2.0,
            "visual_intensity": -1.0,
        },
    },
    "startup": {
        "description": "Startup or product launch page",
        "preferred_categories": [
            "hero-sections",
            "backgrounds",
            "text-effects",
            "testimonials",
            "call-to-action",
            "feature-sections",
            "pricing",
        ],
        "preferred_tags": [
            "hero",
            "animated",
            "gradient",
            "premium",
            "cta",
            "landing",
            "modern",
            "startup",
        ],
        "score_weights": {
            "landing_page_fit": 3.0,
            "visual_intensity": 2.0,
            "animation_intensity": 1.5,
        },
    },
    "blog": {
        "description": "Blog or content publication",
        "preferred_categories": [
            "layout",
            "cards",
            "text-effects",
            "navigation",
        ],
        "preferred_tags": [
            "text",
            "card",
            "layout",
            "minimal",
            "content",
            "clean",
            "responsive",
        ],
        "score_weights": {
            "customization_ease": 2.5,
            "layout_importance": 2.0,
            "performance_impact": -1.5,
            "visual_intensity": -0.5,
        },
    },
}

# ---------------------------------------------------------------------------
# Page layout templates
# ---------------------------------------------------------------------------

# Each template defines ordered sections with queries and priorities.
# priority: 1 = essential, 2 = recommended, 3 = optional enhancement

_PAGE_TEMPLATES: dict[str, dict[str, Any]] = {
    "landing": {
        "description": "Conversion-focused landing page",
        "sections": [
            {
                "name": "Navigation",
                "role": "navigation",
                "query": "navbar navigation header",
                "description": "Top navigation bar with logo and links",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero section animated headline",
                "description": "Primary hero section with headline and CTA",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background effect ambient",
                "description": "Ambient background effect for visual depth",
                "priority": 2,
            },
            {
                "name": "Features",
                "role": "features",
                "query": "feature section bento grid display",
                "description": "Feature showcase with structured layout",
                "priority": 1,
            },
            {
                "name": "Social Proof",
                "role": "social-proof",
                "query": "testimonial review marquee",
                "description": "Testimonials or client logos for credibility",
                "priority": 2,
            },
            {
                "name": "Content Cards",
                "role": "cards",
                "query": "card hover effect showcase",
                "description": "Interactive cards for content or services",
                "priority": 2,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation typewriter gradient",
                "description": "Animated text for emphasis and engagement",
                "priority": 3,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button section",
                "description": "Closing CTA section driving conversions",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with links and secondary navigation",
                "priority": 1,
            },
        ],
    },
    "dashboard": {
        "description": "Data-rich admin dashboard",
        "sections": [
            {
                "name": "Sidebar",
                "role": "sidebar",
                "query": "sidebar navigation menu",
                "description": "Collapsible sidebar for primary navigation",
                "priority": 1,
            },
            {
                "name": "Top Bar",
                "role": "navigation",
                "query": "navbar header toolbar",
                "description": "Top bar with search, notifications, profile",
                "priority": 1,
            },
            {
                "name": "Content Grid",
                "role": "layout",
                "query": "bento grid layout cards",
                "description": "Main content area with grid layout",
                "priority": 1,
            },
            {
                "name": "Data Cards",
                "role": "cards",
                "query": "card stats metric hover",
                "description": "Metric cards for KPIs and data display",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background subtle gradient",
                "description": "Subtle background for visual hierarchy",
                "priority": 3,
            },
            {
                "name": "Loading States",
                "role": "loaders",
                "query": "loader skeleton spinner",
                "description": "Loading indicators for async content",
                "priority": 2,
            },
        ],
    },
    "portfolio": {
        "description": "Creative portfolio or showcase site",
        "sections": [
            {
                "name": "Navigation",
                "role": "navigation",
                "query": "navbar floating minimal",
                "description": "Minimal floating navigation",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero parallax 3d spotlight",
                "description": "Immersive hero with 3D or parallax effects",
                "priority": 1,
            },
            {
                "name": "Background Effect",
                "role": "background",
                "query": "background aurora beam particles",
                "description": "Atmospheric background effect",
                "priority": 1,
            },
            {
                "name": "Project Showcase",
                "role": "showcase",
                "query": "card hover parallax image gallery",
                "description": "Interactive project cards with hover effects",
                "priority": 1,
            },
            {
                "name": "Scroll Effects",
                "role": "scroll",
                "query": "scroll animation reveal timeline",
                "description": "Scroll-driven content reveals",
                "priority": 2,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation typewriter gradient",
                "description": "Animated headings for visual impact",
                "priority": 2,
            },
            {
                "name": "Contact Section",
                "role": "cta",
                "query": "call to action contact form",
                "description": "Contact or hire-me section",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer links social",
                "description": "Footer with social links",
                "priority": 2,
            },
        ],
    },
    "saas": {
        "description": "SaaS product marketing page",
        "sections": [
            {
                "name": "Navigation",
                "role": "navigation",
                "query": "navbar sticky header premium",
                "description": "Sticky header with product navigation",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero spotlight animated premium",
                "description": "Product hero with animated showcase",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background gradient grid beam",
                "description": "Dynamic background for modern SaaS feel",
                "priority": 2,
            },
            {
                "name": "Feature Grid",
                "role": "features",
                "query": "bento grid feature card hover",
                "description": "Feature breakdown in bento grid layout",
                "priority": 1,
            },
            {
                "name": "Product Demo",
                "role": "showcase",
                "query": "card 3d parallax image container scroll",
                "description": "Product screenshots or demo section",
                "priority": 2,
            },
            {
                "name": "Testimonials",
                "role": "social-proof",
                "query": "testimonial marquee animated review",
                "description": "Customer testimonials for trust",
                "priority": 2,
            },
            {
                "name": "Pricing",
                "role": "pricing",
                "query": "pricing card table plan",
                "description": "Pricing tiers with comparison",
                "priority": 1,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button spotlight",
                "description": "Final conversion CTA",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Comprehensive footer with links",
                "priority": 1,
            },
        ],
    },
    "ecommerce": {
        "description": "E-commerce product store",
        "sections": [
            {
                "name": "Navigation",
                "role": "navigation",
                "query": "navbar header navigation responsive",
                "description": "Product navigation with categories",
                "priority": 1,
            },
            {
                "name": "Hero Banner",
                "role": "hero",
                "query": "hero carousel image animated",
                "description": "Promotional hero banner",
                "priority": 1,
            },
            {
                "name": "Product Grid",
                "role": "products",
                "query": "card grid hover image product",
                "description": "Product listing cards with hover effects",
                "priority": 1,
            },
            {
                "name": "Feature Highlights",
                "role": "features",
                "query": "feature section bento layout",
                "description": "Product feature highlights",
                "priority": 2,
            },
            {
                "name": "Reviews",
                "role": "social-proof",
                "query": "testimonial review marquee",
                "description": "Customer reviews section",
                "priority": 2,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button section",
                "description": "Promotional CTA for offers",
                "priority": 2,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with store info and links",
                "priority": 1,
            },
        ],
    },
    "blog": {
        "description": "Blog or content publication site",
        "sections": [
            {
                "name": "Navigation",
                "role": "navigation",
                "query": "navbar minimal header clean",
                "description": "Clean navigation header",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero text minimal clean",
                "description": "Content-focused hero with title",
                "priority": 2,
            },
            {
                "name": "Article Cards",
                "role": "cards",
                "query": "card hover image layout grid",
                "description": "Article preview cards in grid layout",
                "priority": 1,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation subtle gradient",
                "description": "Subtle heading effects",
                "priority": 3,
            },
            {
                "name": "Sidebar",
                "role": "sidebar",
                "query": "sidebar navigation categories",
                "description": "Category sidebar for content browsing",
                "priority": 2,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with archives and links",
                "priority": 1,
            },
        ],
    },
    "documentation": {
        "description": "Documentation or knowledge base",
        "sections": [
            {
                "name": "Top Bar",
                "role": "navigation",
                "query": "navbar header toolbar search",
                "description": "Top bar with search functionality",
                "priority": 1,
            },
            {
                "name": "Sidebar Navigation",
                "role": "sidebar",
                "query": "sidebar navigation tree menu",
                "description": "Docs sidebar with section navigation",
                "priority": 1,
            },
            {
                "name": "Content Area",
                "role": "layout",
                "query": "layout content container",
                "description": "Main content area for documentation",
                "priority": 1,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text highlight gradient code",
                "description": "Text emphasis for code and headings",
                "priority": 3,
            },
        ],
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
            tag_overlap = preferred_tags.intersection({t.lower() for t in comp.tags})
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
        _max_results: int = 8,
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

    def generate_page_layout(
        self,
        page_description: str,
        *,
        page_type: str | None = None,
        include_pro: bool = True,
        components_per_section: int = 2,
    ) -> PageLayout:
        """Generate a complete page layout with component recommendations.

        Analyses the description to detect the page type, selects the
        appropriate template, and fills each section with the best-fit
        components. De-duplicates across sections and computes aggregate
        install commands and dependencies.

        Args:
            page_description: Free-text description of the page to build.
            page_type: Explicit page type override. One of: landing,
                dashboard, portfolio, saas, ecommerce, blog, documentation.
                If omitted, detected automatically from the description.
            include_pro: Include pro components in recommendations.
            components_per_section: Components to recommend per section
                (default 2).

        Returns:
            A :class:`PageLayout` with ordered sections, install commands,
            and dependency summary.
        """
        # Resolve template
        if page_type and page_type in _PAGE_TEMPLATES:
            template_key = page_type
        else:
            template_key = self._detect_page_type(page_description)
        template = _PAGE_TEMPLATES[template_key]

        used_slugs: set[str] = set()
        sections: list[LayoutSection] = []

        for sec_def in template["sections"]:
            query = f"{sec_def['query']} for {page_description}"
            recs = self.recommend_for_use_case(
                query,
                max_results=components_per_section + 5,
                include_pro=include_pro,
            )

            # De-duplicate: skip components already assigned
            unique_recs: list[Recommendation] = []
            for r in recs:
                if r.component.slug not in used_slugs:
                    unique_recs.append(r)
                    if len(unique_recs) >= components_per_section:
                        break

            for r in unique_recs:
                used_slugs.add(r.component.slug)

            sections.append(
                LayoutSection(
                    name=sec_def["name"],
                    role=sec_def["role"],
                    description=sec_def["description"],
                    components=unique_recs,
                    priority=sec_def["priority"],
                )
            )

        # Aggregate dependencies and install commands
        all_deps: set[str] = set()
        install_cmds: list[str] = []
        total = 0
        perf_sum = 0

        for sec in sections:
            for rec in sec.components:
                comp = rec.component
                all_deps.update(comp.dependencies)
                if comp.install_command:
                    install_cmds.append(comp.install_command)
                total += 1
                perf_sum += comp.scores.performance_impact

        avg_perf = perf_sum / total if total > 0 else 5
        if avg_perf <= 3:
            perf_label = "lightweight"
        elif avg_perf <= 5:
            perf_label = "moderate"
        elif avg_perf <= 7:
            perf_label = "heavy"
        else:
            perf_label = "very heavy"

        return PageLayout(
            page_type=template_key,
            description=template["description"],
            sections=sections,
            all_dependencies=sorted(all_deps),
            install_commands=install_cmds,
            total_components=total,
            estimated_performance=perf_label,
        )

    @staticmethod
    def available_page_types() -> dict[str, str]:
        """Return mapping of page type slug to description."""
        return {k: v["description"] for k, v in _PAGE_TEMPLATES.items()}

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _detect_page_type(description: str) -> str:
        """Detect the best page template from a free-text description."""
        desc_lower = description.lower()

        type_keywords: dict[str, list[str]] = {
            "landing": [
                "landing",
                "conversion",
                "lead",
                "signup",
                "launch",
            ],
            "saas": [
                "saas",
                "software",
                "platform",
                "app",
                "tool",
                "service",
            ],
            "dashboard": [
                "dashboard",
                "admin",
                "panel",
                "analytics",
                "internal",
                "crm",
                "erp",
                "metrics",
            ],
            "portfolio": [
                "portfolio",
                "personal",
                "creative",
                "showcase",
                "freelance",
                "designer",
                "developer",
            ],
            "ecommerce": [
                "ecommerce",
                "e-commerce",
                "store",
                "shop",
                "product",
                "marketplace",
                "retail",
            ],
            "blog": [
                "blog",
                "article",
                "publication",
                "magazine",
                "news",
                "journal",
            ],
            "documentation": [
                "docs",
                "documentation",
                "knowledge base",
                "wiki",
                "reference",
                "guide",
                "api docs",
            ],
        }

        best_match = ""
        best_count = 0
        for ptype, keywords in type_keywords.items():
            count = sum(1 for kw in keywords if kw in desc_lower)
            if count > best_count:
                best_count = count
                best_match = ptype

        return best_match or "landing"

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
