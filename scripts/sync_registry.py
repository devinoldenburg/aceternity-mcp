#!/usr/bin/env python3
"""Sync and enrich the local Aceternity component registry.

This script builds a three-layer local registry:

1) Raw source layer (``registry/raw/components.json``)
   - Discovered facts from the public shadcn/Aceternity registry namespace.
   - No source code content is stored.

2) Enriched metadata layer (``registry/components/*.json``)
   - Long-form descriptions, purpose/behavior metadata, inferred tags,
     compatibility, and scoring.

3) Runtime index layer (``registry/index.json`` + ``registry/categories/*.json``)
   - Normalized indexes consumed by the MCP server.

Usage:
  python scripts/sync_registry.py

Optional:
  python scripts/sync_registry.py --api-key "$ACETERNITY_API_KEY"

Note: API key is optional and is not written to disk.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
RAW_DIR = REGISTRY_DIR / "raw"
COMPONENTS_DIR = REGISTRY_DIR / "components"
CATEGORIES_DIR = REGISTRY_DIR / "categories"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_json(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _slug_to_name(slug: str) -> str:
    overrides = {
        "3d-pin": "3D Pin",
        "3d-card": "3D Card Effect",
        "3d-globe": "3D Globe",
        "3d-marquee": "3D Marquee",
        "gooey-input": "Gooey Input",
        "svg-mask-effect": "SVG Mask Effect",
        "tailwindcss-buttons": "Tailwind CSS Buttons",
        "text-flipping-board": "Text Flipping Board",
        "card-hover-effect": "Card Hover Effect",
        "spotlight-new": "Spotlight New",
        "world-map": "World Map",
        "code-block": "Code Block",
        "ascii-art": "ASCII Art",
        "resizable-navbar": "Resizable Navbar",
        "layout-text-flip": "Layout Text Flip",
        "container-text-flip": "Container Text Flip",
        "google-gemini-effect": "Google Gemini Effect",
        "apple-cards-carousel": "Apple Cards Carousel",
    }
    if slug in overrides:
        return overrides[slug]

    out = []
    for part in slug.split("-"):
        if part == "3d":
            out.append("3D")
        elif part == "ui":
            out.append("UI")
        elif part == "css":
            out.append("CSS")
        elif part.isdigit():
            out.append(part)
        else:
            out.append(part.capitalize())
    return " ".join(out)


DOCS_OVERRIDES: dict[str, str] = {
    "3d-card": "3d-card-effect",
    "cover": "container-cover",
    "lamp": "lamp-effect",
    "globe": "github-globe",
    "shooting-stars": "shooting-stars-and-stars-background",
    "stars-background": "shooting-stars-and-stars-background",
}


def _docs_url(slug: str) -> str:
    path = DOCS_OVERRIDES.get(slug, slug)
    return f"https://ui.aceternity.com/components/{path}"


def _registry_url(slug: str) -> str:
    return f"https://ui.aceternity.com/registry/{slug}.json"


def _infer_component_kind(slug: str) -> str:
    if "background" in slug or slug in {"vortex", "sparkles", "meteors", "scales"}:
        return "background effect"
    if "card" in slug or "cards" in slug or "bento" in slug:
        return "card component"
    if "navbar" in slug or "sidebar" in slug or "dock" in slug or "menu" in slug:
        return "navigation component"
    if "text" in slug or "typewriter" in slug or "flip" in slug:
        return "text effect"
    if (
        "input" in slug
        or "signup" in slug
        or "upload" in slug
        or slug in {"label", "input"}
    ):
        return "form/input component"
    if "loader" in slug:
        return "loader component"
    if "hero" in slug or slug in {"lamp", "spotlight", "spotlight-new"}:
        return "hero/section component"
    if "timeline" in slug or "parallax" in slug or "tracing" in slug:
        return "scroll interaction component"
    if "globe" in slug or "map" in slug:
        return "visualization component"
    return "UI component"


def _infer_categories(slug: str) -> list[str]:
    categories: set[str] = set()

    if any(
        k in slug for k in ["hero", "spotlight", "lamp", "highlight", "parallax-hero"]
    ):
        categories.add("hero-sections")
    if any(
        k in slug
        for k in [
            "background",
            "vortex",
            "sparkles",
            "meteors",
            "stars",
            "aurora",
            "scales",
        ]
    ):
        categories.add("backgrounds")
    if any(
        k in slug
        for k in ["card", "cards", "bento", "wobble", "comet", "glare", "evervault"]
    ):
        categories.add("cards")
    if any(k in slug for k in ["testimonial", "testimonials", "card-stack"]):
        categories.add("testimonials")
    if any(
        k in slug for k in ["navbar", "menu", "floating-navbar", "resizable-navbar"]
    ):
        categories.add("navbars")
    if "sidebar" in slug:
        categories.add("sidebars")
    if any(
        k in slug
        for k in ["navbar", "sidebar", "dock", "menu", "tabs", "sticky-banner"]
    ):
        categories.add("navigation")
    if any(k in slug for k in ["button", "stateful", "hero-highlight", "cover"]):
        categories.add("cta")
    if any(
        k in slug
        for k in ["text", "typewriter", "flip", "encrypted", "terminal", "code-block"]
    ):
        categories.add("text-effects")
    if any(
        k in slug
        for k in ["input", "signup", "upload", "label", "stateful-button", "gooey"]
    ):
        categories.add("forms")
    if any(k in slug for k in ["loader", "loading"]):
        categories.add("loaders")
    if any(k in slug for k in ["timeline", "parallax", "tracing", "scroll", "reveal"]):
        categories.add("scroll-effects")
    if any(
        k in slug
        for k in ["globe", "map", "ascii", "pixel", "canvas", "shader", "world"]
    ):
        categories.add("visualization")
    if any(k in slug for k in ["3d", "tilt", "draggable", "marquee"]):
        categories.add("3d-effects")
    if any(k in slug for k in ["bento", "feature", "timeline", "compare"]):
        categories.add("feature-sections")

    # Useful fallback categories
    if not categories:
        categories.add("layout")
    if (
        len(categories) == 1
        and "hero-sections" not in categories
        and "navigation" not in categories
    ):
        categories.add("layout")

    return sorted(categories)


def _infer_tags(slug: str, categories: list[str]) -> list[str]:
    tokens = set(filter(None, re.split(r"[-_]+", slug.lower())))

    synonyms = {
        "navbar": "navigation",
        "sidebar": "navigation",
        "dock": "navigation",
        "hero": "hero",
        "parallax": "scroll",
        "scroll": "scroll",
        "background": "background",
        "card": "card",
        "cards": "card",
        "input": "form",
        "signup": "form",
        "upload": "form",
        "loader": "loading",
        "3d": "3d",
        "globe": "data-viz",
        "map": "data-viz",
        "text": "text",
        "tooltip": "hover",
    }

    tags = set()
    for token in tokens:
        tags.add(token)
        if token in synonyms:
            tags.add(synonyms[token])

    if "backgrounds" in categories:
        tags.update({"decorative", "atmospheric"})
    if "hero-sections" in categories:
        tags.update({"headline", "landing"})
    if "cards" in categories:
        tags.update({"content", "showcase"})
    if "navigation" in categories:
        tags.update({"menu", "layout"})
    if "text-effects" in categories:
        tags.update({"typography", "animated"})

    motion_tokens = {
        "animated",
        "animation",
        "scroll",
        "parallax",
        "reveal",
        "hover",
        "motion",
        "marquee",
        "flip",
        "typewriter",
        "beams",
        "sparkles",
        "ripple",
    }
    if tags.intersection(motion_tokens):
        tags.add("animated")

    return sorted(tags)


def _infer_dependencies(slug: str, categories: list[str]) -> list[str]:
    deps = {"clsx", "tailwind-merge"}

    # Most Aceternity interactive components rely on Motion.
    if any(
        cat in categories
        for cat in [
            "backgrounds",
            "hero-sections",
            "cards",
            "scroll-effects",
            "3d-effects",
            "text-effects",
            "navigation",
        ]
    ):
        deps.add("motion")

    extra_map = {
        "world-map": {"dotted-map", "next-themes"},
        "globe": {"cobe"},
        "3d-globe": {"cobe"},
        "code-block": {"react-syntax-highlighter"},
        "terminal": {"react-syntax-highlighter"},
        "file-upload": {"react-dropzone"},
        "sidebar": {"@tabler/icons-react"},
        "carousel": {"embla-carousel-react"},
    }

    if slug in extra_map:
        deps.update(extra_map[slug])

    return sorted(deps)


def _infer_summary(name: str, kind: str, categories: list[str]) -> str:
    if kind == "background effect":
        return f"A reusable {name} background effect that adds depth, focus, and atmosphere to modern UI sections."
    if kind == "navigation component":
        return f"A {name} navigation component for responsive headers, sidebars, and interaction-friendly layout flows."
    if kind == "text effect":
        return f"A {name} text effect for expressive headings, highlights, and animated content emphasis."
    if kind == "card component":
        return f"A {name} card component for showcasing features, testimonials, and product content with visual polish."
    if kind == "form/input component":
        return f"A {name} form component that improves data entry UX with clear states and modern interactions."
    if kind == "loader component":
        return f"A {name} loader component for communicating progress and improving perceived responsiveness."
    return f"A reusable {name} component for React and Next.js projects using Tailwind CSS and modern interaction patterns."


def _infer_purpose(kind: str, categories: list[str]) -> list[str]:
    purpose = {
        "background effect": [
            "Create visual atmosphere around hero and CTA content",
            "Guide user attention without changing structural layout",
            "Improve perceived polish for premium landing pages",
        ],
        "navigation component": [
            "Provide clear wayfinding across pages and sections",
            "Support responsive navigation patterns on desktop and mobile",
            "Improve information architecture and scanning",
        ],
        "card component": [
            "Group related content into digestible visual blocks",
            "Highlight features, testimonials, or product capabilities",
            "Increase engagement through interaction and motion",
        ],
        "text effect": [
            "Draw attention to key headlines and supporting copy",
            "Communicate brand tone through animated typography",
            "Increase visual rhythm in content-heavy sections",
        ],
        "form/input component": [
            "Improve clarity and confidence while entering information",
            "Provide interactive feedback during form completion",
            "Increase conversion for signup and contact flows",
        ],
        "loader component": [
            "Set user expectations during asynchronous operations",
            "Reduce perceived waiting time with meaningful feedback",
            "Maintain visual continuity between loading and loaded states",
        ],
    }
    if kind in purpose:
        return purpose[kind]
    return [
        "Add a reusable presentational building block to UI flows",
        "Improve consistency across pages and sections",
        "Accelerate implementation with an install-ready component",
    ]


def _infer_behavior(slug: str, kind: str) -> list[str]:
    behavior = []

    if any(
        k in slug
        for k in ["hover", "spotlight", "tooltip", "card", "glare", "wobble", "lens"]
    ):
        behavior.append("Responds to pointer hover and movement with visual feedback")
    if any(k in slug for k in ["scroll", "parallax", "timeline", "tracing", "sticky"]):
        behavior.append("Reacts to scroll progress with transition or reveal effects")
    if any(k in slug for k in ["input", "signup", "upload", "button"]):
        behavior.append(
            "Supports interaction states for typing, focus, submit, or upload"
        )
    if any(k in slug for k in ["tabs", "navbar", "sidebar", "dock", "menu"]):
        behavior.append(
            "Handles navigation state changes with responsive layout behavior"
        )
    if any(
        k in slug
        for k in ["loader", "animated", "flip", "typewriter", "beams", "sparkles"]
    ):
        behavior.append("Uses timed animation sequences for dynamic visual presence")

    if not behavior:
        behavior.append(
            "Provides composable UI behavior with optional animation and styling controls"
        )

    return behavior


def _infer_visual_characteristics(
    kind: str, categories: list[str], slug: str
) -> list[str]:
    visual = []

    if kind == "background effect":
        visual.extend(["Atmospheric", "Layered", "Decorative"])
    if kind == "card component":
        visual.extend(["Structured", "Content-focused", "Interactive"])
    if kind == "navigation component":
        visual.extend(["Layout-critical", "Functional", "Adaptive"])
    if kind == "text effect":
        visual.extend(["Expressive", "Typographic", "Attention-guiding"])
    if kind == "form/input component":
        visual.extend(["Utility-first", "Conversion-oriented", "State-driven"])

    if any(k in slug for k in ["3d", "globe", "marquee", "vortex", "shader"]):
        visual.append("Visually dominant")
    if any(k in slug for k in ["minimal", "line", "grid", "scales", "label", "input"]):
        visual.append("Subtle")
    if any(cat in categories for cat in ["hero-sections", "backgrounds"]):
        visual.append("Landing-page friendly")

    # Keep unique ordering
    out = []
    seen = set()
    for v in visual:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out[:6]


def _infer_scores(slug: str, categories: list[str]) -> dict[str, int]:
    visual = 5
    animation = 5
    layout = 5
    customization = 7
    landing = 6
    dashboard = 5
    perf = 5

    if "backgrounds" in categories:
        visual += 2
        animation += 1
        layout -= 2
        landing += 2
        dashboard -= 2
        perf += 1
    if "hero-sections" in categories:
        visual += 2
        animation += 1
        layout += 1
        landing += 3
        dashboard -= 2
        perf += 1
    if "navigation" in categories:
        layout += 3
        dashboard += 3
        visual -= 1
        animation -= 1
        perf -= 1
    if "cards" in categories:
        visual += 1
        animation += 1
        landing += 1
        dashboard += 1
    if "forms" in categories:
        layout += 2
        customization += 1
        dashboard += 2
        animation -= 2
        perf -= 1
    if "loaders" in categories:
        animation += 3
        layout -= 2
        dashboard += 2

    if any(k in slug for k in ["3d", "vortex", "shader", "pixel", "marquee", "globe"]):
        visual += 2
        animation += 2
        perf += 2
    if any(k in slug for k in ["grid", "line", "label", "input", "stateful"]):
        customization += 1

    def clamp(v: int) -> int:
        return max(1, min(10, v))

    return {
        "visualIntensity": clamp(visual),
        "animationIntensity": clamp(animation),
        "layoutImportance": clamp(layout),
        "customizationEase": clamp(customization),
        "landingPageFit": clamp(landing),
        "dashboardFit": clamp(dashboard),
        "performanceImpact": clamp(perf),
    }


def _infer_difficulty(slug: str, categories: list[str], dependencies: list[str]) -> str:
    complexity = 0
    if "motion" in dependencies:
        complexity += 1
    if any(
        cat in categories for cat in ["3d-effects", "visualization", "scroll-effects"]
    ):
        complexity += 1
    if any(
        k in slug for k in ["shader", "globe", "parallax", "timeline", "ascii", "pixel"]
    ):
        complexity += 1

    if complexity <= 1:
        return "beginner"
    if complexity == 2:
        return "intermediate"
    return "advanced"


def _infer_design_tone(
    slug: str, categories: list[str], scores: dict[str, int]
) -> list[str]:
    tones: list[str] = ["modern"]
    if scores["visualIntensity"] >= 8:
        tones.append("dramatic")
    if scores["visualIntensity"] <= 4:
        tones.append("minimal")
    if any(cat in categories for cat in ["hero-sections", "backgrounds", "3d-effects"]):
        tones.append("premium")
    if any(k in slug for k in ["grid", "code", "terminal", "timeline"]):
        tones.append("technical")
    if any(k in slug for k in ["wobble", "sparkles", "ripple", "gooey"]):
        tones.append("playful")

    out: list[str] = []
    for t in tones:
        if t not in out:
            out.append(t)
    return out[:4]


def _infer_layout_role(categories: list[str], scores: dict[str, int]) -> str:
    if any(cat in categories for cat in ["navigation", "forms", "feature-sections"]):
        return "layout-critical"
    if (
        any(cat in categories for cat in ["backgrounds", "text-effects"])
        and scores["layoutImportance"] <= 5
    ):
        return "decorative"
    return "supporting"


def _infer_recommendations(
    slug: str, categories: list[str], scores: dict[str, int]
) -> list[str]:
    recommendations: list[str] = []

    if scores["landingPageFit"] >= 8:
        recommendations.append(
            "Best for premium landing page sections and hero compositions."
        )
    if scores["dashboardFit"] >= 8:
        recommendations.append(
            "Good fit for dashboards, admin panels, and data-dense application layouts."
        )
    if scores["performanceImpact"] <= 4:
        recommendations.append(
            "Suitable for performance-sensitive pages that still need polished visuals."
        )
    if scores["animationIntensity"] >= 8:
        recommendations.append(
            "Use as a focal animated accent and pair with calmer surrounding components."
        )
    if "navigation" in categories:
        recommendations.append(
            "Combine with hero and feature sections to establish clear top-level page flow."
        )
    if "backgrounds" in categories:
        recommendations.append(
            "Use as a supporting atmospheric layer rather than the primary layout structure."
        )
    if "cards" in categories:
        recommendations.append(
            "Pairs well with testimonials, feature grids, and product highlight sections."
        )

    if not recommendations:
        recommendations.append(
            "Use where moderate motion and reusable composition improve UX and clarity."
        )

    return recommendations[:4]


def _build_detailed_description(
    *,
    name: str,
    kind: str,
    categories: list[str],
    summary: str,
    has_motion: bool,
    visual_intensity: int,
) -> str:
    best_for = ", ".join(categories[:3]) if categories else "general interfaces"
    dominance = (
        "subtle"
        if visual_intensity <= 4
        else "balanced"
        if visual_intensity <= 7
        else "visually dominant"
    )
    motion_text = (
        "It typically relies on motion-driven transitions and timing curves to feel alive and premium."
        if has_motion
        else "It can be used with little or no motion when a quieter presentation is required."
    )

    return (
        f"{name} is a reusable {kind} designed to help teams compose polished UI sections faster without "
        f"rebuilding common interaction patterns from scratch. It works by combining Tailwind-driven styling "
        f"with composable React structure, and in many setups it can be paired with utility props and class "
        f"overrides for project-specific branding. It is best suited for {best_for} contexts where clear visual "
        f"hierarchy matters. Visually, it feels {dominance} and can act as either a supporting accent or a focal "
        f"element depending on spacing, color contrast, and surrounding content density. {motion_text} It combines "
        f"well with complementary navigation, hero, card, and typography primitives, but should be used carefully "
        f"to avoid animation overload, accessibility conflicts, or unnecessary performance cost on low-powered devices."
    )


def _category_descriptions() -> dict[str, str]:
    return {
        "hero-sections": "Primary above-the-fold components that shape first impression and conversion direction.",
        "backgrounds": "Decorative and atmospheric background effects for hero sections, CTAs, and thematic surfaces.",
        "feature-sections": "Structured blocks for presenting capabilities, comparisons, and value propositions.",
        "testimonials": "Social proof components focused on quotes, credibility signals, and trust-building content.",
        "pricing": "Pricing-related components intended for plans, tiers, and conversion decision support.",
        "navbars": "Top navigation patterns for global site structure and orientation.",
        "sidebars": "Persistent or collapsible sidebar patterns for app and dashboard contexts.",
        "cta": "Call-to-action focused elements that drive user conversion and next-step actions.",
        "cards": "Content grouping components for features, testimonials, product highlights, and interactive showcases.",
        "navigation": "Navigation and wayfinding components including navbars, sidebars, docks, menus, and tabs.",
        "text-effects": "Animated or expressive typography components for headlines, highlights, and messaging emphasis.",
        "forms": "Input and conversion-focused components for signup, upload, stateful actions, and data collection.",
        "loaders": "Loading and progress indicators for asynchronous operations and transitional states.",
        "scroll-effects": "Components that react to scroll position for reveal, timeline, and parallax storytelling.",
        "visualization": "Visual and media-driven components including maps, globes, shaders, canvas, and image effects.",
        "3d-effects": "Three-dimensional or perspective-based effects for premium, interactive visual experiences.",
        "layout": "General layout and composition primitives useful as structure and section scaffolding.",
    }


# ---------------------------------------------------------------------------
# Registry generation
# ---------------------------------------------------------------------------


def _fetch_registry_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    offset = 0
    limit = 100

    while True:
        payload = _run_json(
            [
                "npx",
                "-y",
                "shadcn@latest",
                "list",
                "@aceternity",
                "--offset",
                str(offset),
                "--limit",
                str(limit),
            ]
        )
        items.extend(payload.get("items", []))
        pagination = payload.get("pagination", {})
        if not pagination.get("hasMore"):
            break
        offset += limit

    dedup = {}
    for item in items:
        dedup[item["name"]] = item
    return [dedup[k] for k in sorted(dedup.keys())]


def _build_component_entry(slug: str) -> dict[str, Any]:
    name = _slug_to_name(slug)
    categories = _infer_categories(slug)

    # Category refinements
    if any(k in slug for k in ["pricing", "plan", "tier", "billing"]):
        if "pricing" not in categories:
            categories.append("pricing")
    if any(k in slug for k in ["testimonial", "testimonials", "card-stack"]):
        if "testimonials" not in categories:
            categories.append("testimonials")
    if "navbar" in slug and "navbars" not in categories:
        categories.append("navbars")
    if "sidebar" in slug and "sidebars" not in categories:
        categories.append("sidebars")
    if any(k in slug for k in ["cta", "button", "stateful", "cover"]):
        if "cta" not in categories:
            categories.append("cta")
    categories = sorted(set(categories))

    tags = _infer_tags(slug, categories)
    kind = _infer_component_kind(slug)
    summary = _infer_summary(name, kind, categories)
    dependencies = _infer_dependencies(slug, categories)
    scores = _infer_scores(slug, categories)
    difficulty = _infer_difficulty(slug, categories, dependencies)
    design_tone = _infer_design_tone(slug, categories, scores)
    layout_role = _infer_layout_role(categories, scores)
    recommendations = _infer_recommendations(slug, categories, scores)
    detailed = _build_detailed_description(
        name=name,
        kind=kind,
        categories=categories,
        summary=summary,
        has_motion="motion" in dependencies,
        visual_intensity=scores["visualIntensity"],
    )

    return {
        "slug": slug,
        "name": name,
        "category": categories,
        "tags": tags,
        "summary": summary,
        "detailedDescription": detailed,
        "purpose": _infer_purpose(kind, categories),
        "behavior": _infer_behavior(slug, kind),
        "visualCharacteristics": _infer_visual_characteristics(kind, categories, slug),
        "difficulty": difficulty,
        "designTone": design_tone,
        "layoutRole": layout_role,
        "recommendations": recommendations,
        "dependencies": dependencies,
        "installCommand": f"npx shadcn@latest add @aceternity/{slug}",
        "registryUrl": _registry_url(slug),
        "docsUrl": _docs_url(slug),
        "previewAvailable": True,
        "examples": [_docs_url(slug)],
        "compatibility": {
            "react": True,
            "nextjs": True,
            "tailwind": True,
            "framerMotion": "motion" in dependencies,
            "shadcn": True,
        },
        "scores": scores,
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def generate_registry(api_key: str | None = None) -> None:
    items = _fetch_registry_items()

    COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    components: list[dict[str, Any]] = []
    raw_items: list[dict[str, Any]] = []

    for item in items:
        slug = item["name"]
        component = _build_component_entry(slug)
        components.append(component)
        _write_json(COMPONENTS_DIR / f"{slug}.json", component)

        raw_items.append(
            {
                "slug": slug,
                "name": component["name"],
                "installCommand": component["installCommand"],
                "registryUrl": component["registryUrl"],
                "docsUrl": component["docsUrl"],
                "dependencies": component["dependencies"],
                "discoverySource": "npx shadcn@latest list @aceternity",
                "containsSourceFiles": False,
            }
        )

    # Build categories from enriched components
    cat_desc = _category_descriptions()
    cat_map: dict[str, list[str]] = {k: [] for k in cat_desc}
    for comp in components:
        for cat in comp["category"]:
            cat_map.setdefault(cat, [])
            cat_map[cat].append(comp["slug"])

    categories_payload = []
    for slug, comp_slugs in sorted(cat_map.items()):
        payload = {
            "slug": slug,
            "name": _slug_to_name(slug),
            "description": cat_desc.get(
                slug,
                "A grouped set of related Aceternity components for focused UI tasks.",
            ),
            "components": sorted(comp_slugs),
        }
        categories_payload.append(payload)
        _write_json(CATEGORIES_DIR / f"{slug}.json", payload)

    # Raw layer file
    raw_payload = {
        "source": {
            "registry": "@aceternity",
            "command": "npx shadcn@latest list @aceternity",
            "fetchedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "apiKeyProvided": bool(api_key),
            "apiKeyStored": False,
            "note": "No source component file contents are stored in this layer.",
        },
        "components": raw_items,
    }
    _write_json(RAW_DIR / "components.json", raw_payload)

    # Root index
    index_payload = {
        "name": "aceternity-registry",
        "version": "1.0.0",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "componentCount": len(components),
        "categoryCount": len(categories_payload),
        "layers": {
            "raw": "registry/raw/components.json",
            "enriched": "registry/components/*.json",
            "runtime": "served via MCP tools",
        },
        "components": [
            {
                "slug": c["slug"],
                "name": c["name"],
                "category": c["category"],
                "docsUrl": c["docsUrl"],
            }
            for c in sorted(components, key=lambda x: x["name"].lower())
        ],
        "categories": [
            {
                "slug": c["slug"],
                "name": c["name"],
                "componentCount": len(c["components"]),
            }
            for c in categories_payload
        ],
    }
    _write_json(REGISTRY_DIR / "index.json", index_payload)

    print(
        f"Generated registry with {len(components)} components and "
        f"{len(categories_payload)} categories."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync local Aceternity registry")
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional API key for future authenticated registry endpoints (not persisted)",
    )
    args = parser.parse_args()
    generate_registry(api_key=args.api_key)


if __name__ == "__main__":
    main()
