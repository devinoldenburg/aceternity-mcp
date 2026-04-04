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
    implementation_note: str = ""
    components: list[Recommendation] = field(default_factory=list)
    priority: int = 1  # 1 = must-have, 2 = recommended, 3 = optional
    build_order: int = 0


@dataclass
class PageLayout:
    """A complete page layout with ordered sections and metadata."""

    page_type: str
    description: str
    detected_theme: str = ""
    design_tones: list[str] = field(default_factory=list)
    sections: list[LayoutSection] = field(default_factory=list)
    all_dependencies: list[str] = field(default_factory=list)
    install_commands: list[str] = field(default_factory=list)
    batch_install: str = ""
    total_components: int = 0
    estimated_performance: str = "moderate"
    shared_dependency_count: int = 0
    unique_dependency_count: int = 0


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
# Design tone detection
# ---------------------------------------------------------------------------

_TONE_KEYWORDS: dict[str, list[str]] = {
    "dark": ["dark", "night", "black", "midnight", "shadow"],
    "premium": ["premium", "luxury", "elegant", "high-end", "exclusive"],
    "modern": ["modern", "contemporary", "sleek", "cutting-edge", "futuristic"],
    "minimal": ["minimal", "clean", "simple", "whitespace", "understated"],
    "playful": ["playful", "fun", "colorful", "vibrant", "energetic"],
    "corporate": ["corporate", "professional", "enterprise", "formal", "business"],
    "creative": ["creative", "artistic", "bold", "experimental", "avant-garde"],
    "tech": ["tech", "developer", "code", "engineering", "ai", "fintech"],
}

# ---------------------------------------------------------------------------
# Section-level scoring profiles
# ---------------------------------------------------------------------------

# Each role maps to preferred categories, preferred tags, and score weights
# used when scoring components specifically for that section role.

_SECTION_PROFILES: dict[str, dict[str, Any]] = {
    "navigation": {
        "categories": ["navigation", "navbars"],
        "tags": ["navbar", "header", "navigation", "menu", "responsive"],
        "weights": {"layout_importance": 3.0, "customization_ease": 1.5},
    },
    "hero": {
        "categories": ["hero-sections"],
        "tags": ["hero", "headline", "landing", "animated", "spotlight"],
        "weights": {
            "visual_intensity": 2.5,
            "landing_page_fit": 2.0,
            "animation_intensity": 1.5,
        },
    },
    "background": {
        "categories": ["backgrounds"],
        "tags": [
            "background",
            "ambient",
            "gradient",
            "aurora",
            "beam",
            "particles",
            "grid",
        ],
        "weights": {"visual_intensity": 2.0, "animation_intensity": 1.5},
    },
    "features": {
        "categories": ["feature-sections", "cards", "layout"],
        "tags": ["feature", "bento", "grid", "display", "showcase"],
        "weights": {"layout_importance": 2.5, "customization_ease": 2.0},
    },
    "cards": {
        "categories": ["cards"],
        "tags": ["card", "hover", "effect", "3d", "image"],
        "weights": {"customization_ease": 2.0, "visual_intensity": 1.5},
    },
    "social-proof": {
        "categories": ["testimonials"],
        "tags": ["testimonial", "review", "marquee", "infinite", "logo"],
        "weights": {"landing_page_fit": 2.0, "customization_ease": 1.5},
    },
    "cta": {
        "categories": ["cta", "call-to-action", "hero-sections"],
        "tags": ["cta", "button", "action", "call"],
        "weights": {"landing_page_fit": 2.5, "visual_intensity": 1.5},
    },
    "text-effect": {
        "categories": ["text-effects"],
        "tags": [
            "text",
            "typewriter",
            "gradient",
            "animation",
            "headline",
            "generate",
        ],
        "weights": {"animation_intensity": 2.0, "visual_intensity": 1.5},
    },
    "sidebar": {
        "categories": ["sidebars", "navigation"],
        "tags": ["sidebar", "navigation", "menu", "tree"],
        "weights": {
            "layout_importance": 3.0,
            "dashboard_fit": 2.0,
            "performance_impact": -1.0,
        },
    },
    "layout": {
        "categories": ["layout"],
        "tags": ["grid", "bento", "layout", "container", "responsive"],
        "weights": {"layout_importance": 3.0, "customization_ease": 2.0},
    },
    "footer": {
        "categories": ["navigation", "layout"],
        "tags": ["footer", "links", "navigation"],
        "weights": {"layout_importance": 2.0, "customization_ease": 1.5},
    },
    "scroll": {
        "categories": ["scroll-effects"],
        "tags": ["scroll", "parallax", "reveal", "timeline", "animation"],
        "weights": {"animation_intensity": 2.5, "visual_intensity": 2.0},
    },
    "loaders": {
        "categories": ["loaders"],
        "tags": ["loader", "skeleton", "spinner", "loading"],
        "weights": {"customization_ease": 2.0, "performance_impact": -1.5},
    },
    "showcase": {
        "categories": ["cards", "3d-effects", "scroll-effects"],
        "tags": ["3d", "parallax", "image", "gallery", "showcase", "hover"],
        "weights": {"visual_intensity": 2.5, "animation_intensity": 2.0},
    },
    "pricing": {
        "categories": ["pricing", "cards"],
        "tags": ["pricing", "plan", "table", "card"],
        "weights": {"customization_ease": 2.5, "layout_importance": 2.0},
    },
    "products": {
        "categories": ["cards", "layout"],
        "tags": ["card", "grid", "product", "image", "hover", "gallery"],
        "weights": {
            "customization_ease": 2.5,
            "layout_importance": 2.0,
            "performance_impact": -1.0,
        },
    },
    "visualization": {
        "categories": ["visualization", "3d-effects"],
        "tags": ["globe", "3d", "chart", "data", "visualization"],
        "weights": {"visual_intensity": 2.5, "animation_intensity": 2.0},
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
                "note": "Build first. Use sticky positioning and ensure mobile responsiveness.",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero section animated headline",
                "description": "Primary hero section with headline and CTA",
                "note": "Place immediately below nav. Include a clear headline, subtext, and primary CTA button.",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background effect ambient",
                "description": "Ambient background effect for visual depth",
                "note": "Layer behind the hero or use as a full-page backdrop with position fixed or absolute.",
                "priority": 2,
            },
            {
                "name": "Features",
                "role": "features",
                "query": "feature section bento grid display",
                "description": "Feature showcase with structured layout",
                "note": "Use a bento grid or card layout. Keep to 3-6 features with icons and short descriptions.",
                "priority": 1,
            },
            {
                "name": "Social Proof",
                "role": "social-proof",
                "query": "testimonial review marquee",
                "description": "Testimonials or client logos for credibility",
                "note": "Place after features. Use an infinite marquee for logos or a card carousel for testimonials.",
                "priority": 2,
            },
            {
                "name": "Content Cards",
                "role": "cards",
                "query": "card hover effect showcase",
                "description": "Interactive cards for content or services",
                "note": "Use hover effects to increase engagement. Limit to 3-4 cards in a responsive grid.",
                "priority": 2,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation typewriter gradient",
                "description": "Animated text for emphasis and engagement",
                "note": "Apply to section headings sparingly. Avoid using on body text to maintain readability.",
                "priority": 3,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button section",
                "description": "Closing CTA section driving conversions",
                "note": "Final conversion point. Use contrasting colors and a clear value proposition.",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with links and secondary navigation",
                "note": "Include sitemap links, social media, and legal pages. Build last.",
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
                "note": "Build first. Implement collapse/expand toggle and active state highlighting.",
                "priority": 1,
            },
            {
                "name": "Top Bar",
                "role": "navigation",
                "query": "navbar header toolbar",
                "description": "Top bar with search, notifications, profile",
                "note": "Sits beside the sidebar. Include breadcrumbs and a global search input.",
                "priority": 1,
            },
            {
                "name": "Content Grid",
                "role": "layout",
                "query": "bento grid layout cards",
                "description": "Main content area with grid layout",
                "note": "Use a responsive bento grid. This is the primary content container for widgets and charts.",
                "priority": 1,
            },
            {
                "name": "Data Cards",
                "role": "cards",
                "query": "card stats metric hover",
                "description": "Metric cards for KPIs and data display",
                "note": "Place in the content grid. Show key metrics with trend indicators and hover details.",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background subtle gradient",
                "description": "Subtle background for visual hierarchy",
                "note": "Keep very subtle. A soft gradient or dot pattern improves depth without distraction.",
                "priority": 3,
            },
            {
                "name": "Loading States",
                "role": "loaders",
                "query": "loader skeleton spinner",
                "description": "Loading indicators for async content",
                "note": "Use skeleton loaders matching card shapes for perceived performance during data fetches.",
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
                "note": "Use a floating or transparent nav that blends with the hero. Keep links minimal.",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero parallax 3d spotlight",
                "description": "Immersive hero with 3D or parallax effects",
                "note": "This is the first impression. Use full-viewport height with bold typography.",
                "priority": 1,
            },
            {
                "name": "Background Effect",
                "role": "background",
                "query": "background aurora beam particles",
                "description": "Atmospheric background effect",
                "note": "Layer behind hero or use across the full page. Keep opacity low to not overpower content.",
                "priority": 1,
            },
            {
                "name": "Project Showcase",
                "role": "showcase",
                "query": "card hover parallax image gallery",
                "description": "Interactive project cards with hover effects",
                "note": "Core section. Use image-heavy cards with hover reveals for project details.",
                "priority": 1,
            },
            {
                "name": "Scroll Effects",
                "role": "scroll",
                "query": "scroll animation reveal timeline",
                "description": "Scroll-driven content reveals",
                "note": "Use for experience timeline or progressive project reveals. Keep animations smooth.",
                "priority": 2,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation typewriter gradient",
                "description": "Animated headings for visual impact",
                "note": "Apply to your name or role title in the hero. Use gradient or typewriter effects.",
                "priority": 2,
            },
            {
                "name": "Contact Section",
                "role": "cta",
                "query": "call to action contact form",
                "description": "Contact or hire-me section",
                "note": "Include email, social links, and optionally a contact form. Use a spotlight or glow effect.",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer links social",
                "description": "Footer with social links",
                "note": "Keep minimal. Social links and copyright are sufficient.",
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
                "note": "Use sticky positioning. Include logo, feature links, pricing link, and a CTA button.",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero spotlight animated premium",
                "description": "Product hero with animated showcase",
                "note": "Lead with your value proposition. Include a product screenshot or animated demo below the headline.",
                "priority": 1,
            },
            {
                "name": "Background",
                "role": "background",
                "query": "background gradient grid beam",
                "description": "Dynamic background for modern SaaS feel",
                "note": "Use a grid or beam pattern. Keep it behind the hero and features sections.",
                "priority": 2,
            },
            {
                "name": "Feature Grid",
                "role": "features",
                "query": "bento grid feature card hover",
                "description": "Feature breakdown in bento grid layout",
                "note": "Use a bento grid with 4-6 features. Each cell should have an icon, title, and one-line description.",
                "priority": 1,
            },
            {
                "name": "Product Demo",
                "role": "showcase",
                "query": "card 3d parallax image container scroll",
                "description": "Product screenshots or demo section",
                "note": "Show your product in context. Use scroll-triggered animations or 3D card effects for screenshots.",
                "priority": 2,
            },
            {
                "name": "Testimonials",
                "role": "social-proof",
                "query": "testimonial marquee animated review",
                "description": "Customer testimonials for trust",
                "note": "Use an infinite marquee or card grid. Include company logos, names, and short quotes.",
                "priority": 2,
            },
            {
                "name": "Pricing",
                "role": "pricing",
                "query": "pricing card table plan",
                "description": "Pricing tiers with comparison",
                "note": "Show 2-3 tiers. Highlight the recommended plan. Include feature comparison and CTA per tier.",
                "priority": 1,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button spotlight",
                "description": "Final conversion CTA",
                "note": "Place before the footer. Repeat the primary value proposition with a strong CTA button.",
                "priority": 1,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Comprehensive footer with links",
                "note": "Include product links, company info, legal pages, and social media.",
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
                "note": "Include category dropdowns, search bar, and cart icon. Ensure mobile hamburger menu.",
                "priority": 1,
            },
            {
                "name": "Hero Banner",
                "role": "hero",
                "query": "hero carousel image animated",
                "description": "Promotional hero banner",
                "note": "Use for seasonal promotions or featured products. Include a shop-now CTA.",
                "priority": 1,
            },
            {
                "name": "Product Grid",
                "role": "products",
                "query": "card grid hover image product",
                "description": "Product listing cards with hover effects",
                "note": "Core section. Use uniform card sizes with image, title, price. Add hover for quick-view.",
                "priority": 1,
            },
            {
                "name": "Feature Highlights",
                "role": "features",
                "query": "feature section bento layout",
                "description": "Product feature highlights",
                "note": "Highlight shipping, returns, and quality guarantees. Use icons with short text.",
                "priority": 2,
            },
            {
                "name": "Reviews",
                "role": "social-proof",
                "query": "testimonial review marquee",
                "description": "Customer reviews section",
                "note": "Show star ratings and customer photos. Use a marquee or grid layout.",
                "priority": 2,
            },
            {
                "name": "Call to Action",
                "role": "cta",
                "query": "call to action button section",
                "description": "Promotional CTA for offers",
                "note": "Use for newsletter signup or current promotions. Include a discount code or incentive.",
                "priority": 2,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with store info and links",
                "note": "Include customer service links, payment methods, shipping info, and trust badges.",
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
                "note": "Keep minimal. Logo, category links, and search. Avoid heavy animations.",
                "priority": 1,
            },
            {
                "name": "Hero",
                "role": "hero",
                "query": "hero text minimal clean",
                "description": "Content-focused hero with title",
                "note": "Use for the featured or latest article. Show title, excerpt, and cover image.",
                "priority": 2,
            },
            {
                "name": "Article Cards",
                "role": "cards",
                "query": "card hover image layout grid",
                "description": "Article preview cards in grid layout",
                "note": "Core section. Use a 2-3 column grid with cover image, title, date, and excerpt.",
                "priority": 1,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text animation subtle gradient",
                "description": "Subtle heading effects",
                "note": "Use sparingly on section titles. Avoid on article body text for readability.",
                "priority": 3,
            },
            {
                "name": "Sidebar",
                "role": "sidebar",
                "query": "sidebar navigation categories",
                "description": "Category sidebar for content browsing",
                "note": "Show categories, recent posts, and tags. Sticky positioning works well here.",
                "priority": 2,
            },
            {
                "name": "Footer",
                "role": "footer",
                "query": "footer navigation links",
                "description": "Footer with archives and links",
                "note": "Include newsletter signup, category archives, and social links.",
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
                "note": "Include logo, version selector, search (keyboard shortcut), and GitHub link.",
                "priority": 1,
            },
            {
                "name": "Sidebar Navigation",
                "role": "sidebar",
                "query": "sidebar navigation tree menu",
                "description": "Docs sidebar with section navigation",
                "note": "Core navigation. Use collapsible tree with active section highlighting and scroll sync.",
                "priority": 1,
            },
            {
                "name": "Content Area",
                "role": "layout",
                "query": "layout content container",
                "description": "Main content area for documentation",
                "note": "Use a max-width container with comfortable reading width. Include a table of contents.",
                "priority": 1,
            },
            {
                "name": "Text Effects",
                "role": "text-effect",
                "query": "text highlight gradient code",
                "description": "Text emphasis for code and headings",
                "note": "Use for page titles or section headers. Keep code blocks in a monospace font without effects.",
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

        Analyses the description to detect the page type, extracts design
        tone preferences, selects the appropriate template, and fills each
        section with context-aware component scoring. Components are
        de-duplicated across sections, scored for design coherence and
        dependency reuse, and returned with implementation guidance.

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

        # Detect design tones from description
        detected_tones = self._detect_design_tones(page_description)

        # Resolve archetype for score weighting
        archetype = self._detect_archetype(page_description)
        arch_config = _ARCHETYPES.get(archetype, {})

        used_slugs: set[str] = set()
        collected_deps: set[str] = set()
        sections: list[LayoutSection] = []
        desc_tokens = _tokenise(page_description)

        for order, sec_def in enumerate(template["sections"], start=1):
            role = sec_def["role"]
            profile = _SECTION_PROFILES.get(role, {})

            # Score every component for this specific section
            scored: list[Recommendation] = []
            for comp in self._registry.all_components():
                if not include_pro and comp.is_pro:
                    continue
                if comp.slug in used_slugs:
                    continue

                reasons: list[str] = []
                fit = 0.0

                # 1) Section-role category match (strong signal)
                prof_cats = set(profile.get("categories", []))
                cat_overlap = prof_cats.intersection(set(comp.category))
                if cat_overlap:
                    fit += len(cat_overlap) * 3.0
                    reasons.append(f"Category fit: {', '.join(cat_overlap)}")

                # 2) Section-role tag match
                prof_tags = set(profile.get("tags", []))
                comp_tags = {t.lower() for t in comp.tags}
                tag_overlap = prof_tags.intersection(comp_tags)
                if tag_overlap:
                    fit += len(tag_overlap) * 1.5
                    reasons.append(f"Tag fit: {', '.join(sorted(tag_overlap)[:4])}")

                # 3) Section-specific score weights
                s = comp.scores
                for dim, weight in profile.get("weights", {}).items():
                    val = getattr(s, dim, 5)
                    if weight > 0:
                        fit += (val / 10.0) * weight
                    else:
                        fit += ((10 - val) / 10.0) * abs(weight)

                # 4) Archetype score weights (page-level context)
                for dim, weight in arch_config.get("score_weights", {}).items():
                    val = getattr(s, dim, 5)
                    w = weight * 0.3  # lower weight than section
                    if w > 0:
                        fit += (val / 10.0) * w
                    else:
                        fit += ((10 - val) / 10.0) * abs(w)

                # 5) Text relevance to user description
                text_score = 0.0
                text_score += _text_relevance(desc_tokens, comp.name, weight=2.0)
                text_score += _text_relevance(desc_tokens, comp.summary, weight=1.0)
                text_score += _text_relevance(
                    desc_tokens, " ".join(comp.tags), weight=1.5
                )
                if text_score > 0:
                    fit += text_score
                    reasons.append("Matches page description")

                # 6) Design tone coherence
                comp_tones = {t.lower() for t in comp.design_tone}
                tone_overlap = detected_tones.intersection(comp_tones)
                if tone_overlap:
                    fit += len(tone_overlap) * 2.0
                    reasons.append(f"Design tone: {', '.join(sorted(tone_overlap))}")

                # 7) Dependency reuse bonus
                comp_deps = set(comp.dependencies)
                shared = comp_deps.intersection(collected_deps)
                if shared and collected_deps:
                    fit += len(shared) * 0.5
                    reasons.append("Shares dependencies with selected components")

                if fit > 0:
                    scored.append(
                        Recommendation(
                            component=comp,
                            fit_score=round(fit, 3),
                            reasons=reasons,
                        )
                    )

            scored.sort(key=lambda r: r.fit_score, reverse=True)

            # Pick top N unique components
            picked: list[Recommendation] = scored[:components_per_section]
            for r in picked:
                used_slugs.add(r.component.slug)
                collected_deps.update(r.component.dependencies)

            sections.append(
                LayoutSection(
                    name=sec_def["name"],
                    role=role,
                    description=sec_def["description"],
                    implementation_note=sec_def.get("note", ""),
                    components=picked,
                    priority=sec_def["priority"],
                    build_order=order,
                )
            )

        # Aggregate dependencies and install commands
        all_deps: set[str] = set()
        install_cmds: list[str] = []
        slug_list: list[str] = []
        total = 0
        perf_sum = 0

        for sec in sections:
            for rec in sec.components:
                comp = rec.component
                all_deps.update(comp.dependencies)
                if comp.install_command:
                    install_cmds.append(comp.install_command)
                slug_list.append(comp.slug)
                total += 1
                perf_sum += comp.scores.performance_impact

        # Build batch install command
        batch = ""
        if slug_list:
            slugs_str = " ".join(f"@aceternity/{s}" for s in slug_list)
            batch = f"npx shadcn@latest add {slugs_str}"

        avg_perf = perf_sum / total if total > 0 else 5
        if avg_perf <= 3:
            perf_label = "lightweight"
        elif avg_perf <= 5:
            perf_label = "moderate"
        elif avg_perf <= 7:
            perf_label = "heavy"
        else:
            perf_label = "very heavy"

        # Determine theme label
        theme = "custom"
        if detected_tones:
            theme = " + ".join(sorted(detected_tones))

        return PageLayout(
            page_type=template_key,
            description=template["description"],
            detected_theme=theme,
            design_tones=sorted(detected_tones),
            sections=sections,
            all_dependencies=sorted(all_deps),
            install_commands=install_cmds,
            batch_install=batch,
            total_components=total,
            estimated_performance=perf_label,
            shared_dependency_count=len(collected_deps.intersection(all_deps)),
            unique_dependency_count=len(all_deps),
        )

    @staticmethod
    def available_page_types() -> dict[str, str]:
        """Return mapping of page type slug to description."""
        return {k: v["description"] for k, v in _PAGE_TEMPLATES.items()}

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _detect_design_tones(description: str) -> set[str]:
        """Extract design tones from a free-text description."""
        desc_lower = description.lower()
        tones: set[str] = set()
        for tone, keywords in _TONE_KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                tones.add(tone)
        return tones

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
