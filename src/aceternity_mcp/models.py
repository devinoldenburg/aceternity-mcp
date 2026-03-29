"""Data models for Aceternity UI component registry.

Defines the structured types used throughout the registry, search,
and recommendation layers. All models are plain dataclasses for
simplicity, serialisable to and from JSON without external deps.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Prop metadata
# ---------------------------------------------------------------------------


@dataclass
class PropInfo:
    """Describes a single component prop."""

    name: str
    type: str
    description: str
    required: bool = False
    default_value: str | None = None

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }
        if self.required:
            d["required"] = True
        if self.default_value is not None:
            d["defaultValue"] = self.default_value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PropInfo:
        return cls(
            name=data["name"],
            type=data["type"],
            description=data["description"],
            required=data.get("required", False),
            default_value=data.get("defaultValue"),
        )


# ---------------------------------------------------------------------------
# Compatibility matrix
# ---------------------------------------------------------------------------


@dataclass
class Compatibility:
    """Framework / library compatibility flags."""

    react: bool = True
    nextjs: bool = True
    tailwind: bool = True
    framer_motion: bool = True
    shadcn: bool = True

    def to_dict(self) -> dict[str, bool]:
        return {
            "react": self.react,
            "nextjs": self.nextjs,
            "tailwind": self.tailwind,
            "framerMotion": self.framer_motion,
            "shadcn": self.shadcn,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Compatibility:
        return cls(
            react=data.get("react", True),
            nextjs=data.get("nextjs", True),
            tailwind=data.get("tailwind", True),
            framer_motion=data.get("framerMotion", True),
            shadcn=data.get("shadcn", True),
        )


# ---------------------------------------------------------------------------
# Scoring metadata (1-10 scale)
# ---------------------------------------------------------------------------


@dataclass
class Scores:
    """Numeric scoring used by the recommendation engine."""

    visual_intensity: int = 5
    animation_intensity: int = 5
    layout_importance: int = 5
    customization_ease: int = 5
    landing_page_fit: int = 5
    dashboard_fit: int = 5
    performance_impact: int = 5

    def to_dict(self) -> dict[str, int]:
        return {
            "visualIntensity": self.visual_intensity,
            "animationIntensity": self.animation_intensity,
            "layoutImportance": self.layout_importance,
            "customizationEase": self.customization_ease,
            "landingPageFit": self.landing_page_fit,
            "dashboardFit": self.dashboard_fit,
            "performanceImpact": self.performance_impact,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Scores:
        return cls(
            visual_intensity=data.get("visualIntensity", 5),
            animation_intensity=data.get("animationIntensity", 5),
            layout_importance=data.get("layoutImportance", 5),
            customization_ease=data.get("customizationEase", 5),
            landing_page_fit=data.get("landingPageFit", 5),
            dashboard_fit=data.get("dashboardFit", 5),
            performance_impact=data.get("performanceImpact", 5),
        )


# ---------------------------------------------------------------------------
# Main component model
# ---------------------------------------------------------------------------


@dataclass
class AceternityComponent:
    """Full structured entry for a single Aceternity UI component."""

    # -- identity -------------------------------------------------------------
    slug: str
    name: str

    # -- classification -------------------------------------------------------
    category: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # -- descriptions ---------------------------------------------------------
    summary: str = ""
    detailed_description: str = ""  # minimum 60 words

    # -- semantic metadata ----------------------------------------------------
    purpose: list[str] = field(default_factory=list)
    behavior: list[str] = field(default_factory=list)
    visual_characteristics: list[str] = field(default_factory=list)
    difficulty: str = "intermediate"
    design_tone: list[str] = field(default_factory=list)
    layout_role: str = "supporting"
    recommendations: list[str] = field(default_factory=list)

    # -- installation ---------------------------------------------------------
    dependencies: list[str] = field(default_factory=list)
    install_command: str = ""
    registry_url: str = ""
    docs_url: str = ""

    # -- extras ---------------------------------------------------------------
    preview_available: bool = True
    examples: list[str] = field(default_factory=list)
    props: list[PropInfo] = field(default_factory=list)

    # -- compatibility --------------------------------------------------------
    compatibility: Compatibility = field(default_factory=Compatibility)

    # -- scoring --------------------------------------------------------------
    scores: Scores = field(default_factory=Scores)

    # -- pro flag -------------------------------------------------------------
    is_pro: bool = False

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        d: dict[str, Any] = {
            "slug": self.slug,
            "name": self.name,
            "category": self.category,
            "tags": self.tags,
            "summary": self.summary,
            "detailedDescription": self.detailed_description,
            "purpose": self.purpose,
            "behavior": self.behavior,
            "visualCharacteristics": self.visual_characteristics,
            "difficulty": self.difficulty,
            "designTone": self.design_tone,
            "layoutRole": self.layout_role,
            "recommendations": self.recommendations,
            "dependencies": self.dependencies,
            "installCommand": self.install_command,
            "registryUrl": self.registry_url,
            "docsUrl": self.docs_url,
            "previewAvailable": self.preview_available,
        }
        if self.examples:
            d["examples"] = self.examples
        if self.props:
            d["props"] = [p.to_dict() for p in self.props]
        d["compatibility"] = self.compatibility.to_dict()
        d["scores"] = self.scores.to_dict()
        if self.is_pro:
            d["isPro"] = True
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AceternityComponent:
        """Construct from a dictionary (e.g. parsed JSON)."""
        props_raw = data.get("props", [])
        props = [PropInfo.from_dict(p) for p in props_raw] if props_raw else []

        compat_raw = data.get("compatibility", {})
        compat = Compatibility.from_dict(compat_raw) if compat_raw else Compatibility()

        scores_raw = data.get("scores", {})
        scores = Scores.from_dict(scores_raw) if scores_raw else Scores()

        return cls(
            slug=data["slug"],
            name=data["name"],
            category=data.get("category", []),
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            detailed_description=data.get("detailedDescription", ""),
            purpose=data.get("purpose", []),
            behavior=data.get("behavior", []),
            visual_characteristics=data.get("visualCharacteristics", []),
            difficulty=data.get("difficulty", "intermediate"),
            design_tone=data.get("designTone", []),
            layout_role=data.get("layoutRole", "supporting"),
            recommendations=data.get("recommendations", []),
            dependencies=data.get("dependencies", []),
            install_command=data.get("installCommand", ""),
            registry_url=data.get("registryUrl", ""),
            docs_url=data.get("docsUrl", ""),
            preview_available=data.get("previewAvailable", True),
            examples=data.get("examples", []),
            props=props,
            compatibility=compat,
            scores=scores,
            is_pro=data.get("isPro", False),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> AceternityComponent:
        """Load from a JSON file on disk."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def to_json(self, *, indent: int = 2) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Category model
# ---------------------------------------------------------------------------


@dataclass
class Category:
    """A registry category grouping related components."""

    slug: str
    name: str
    description: str
    component_slugs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "components": self.component_slugs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Category:
        return cls(
            slug=data["slug"],
            name=data["name"],
            description=data["description"],
            component_slugs=data.get("components", []),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> Category:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)
