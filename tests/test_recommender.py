"""Tests for recommender functionality."""

import pytest

from aceternity_mcp.recommender import Recommender
from aceternity_mcp.registry import Registry


class TestRecommender:
    """Test recommender functionality."""

    @pytest.fixture
    def recommender(self):
        """Create a recommender instance."""
        registry = Registry()
        registry.load()
        return Recommender(registry)

    def test_recommend_for_use_case(self, recommender):
        """Test basic use case recommendations."""
        recs = recommender.recommend_for_use_case("landing page with dark theme")
        assert len(recs) > 0
        assert all(hasattr(r, "component") for r in recs)
        assert all(hasattr(r, "fit_score") for r in recs)
        assert all(hasattr(r, "reasons") for r in recs)

    def test_recommend_empty_description(self, recommender):
        """Test recommendations with empty description."""
        recs = recommender.recommend_for_use_case("")
        # May return empty or default recommendations
        assert isinstance(recs, list)

    def test_recommend_max_results(self, recommender):
        """Test recommendations respect max_results."""
        recs = recommender.recommend_for_use_case("dashboard", max_results=5)
        assert len(recs) <= 5

    def test_recommend_include_pro(self, recommender):
        """Test recommendations with include_pro parameter."""
        recs_with_pro = recommender.recommend_for_use_case(
            "landing page", include_pro=True
        )
        recs_without_pro = recommender.recommend_for_use_case(
            "landing page", include_pro=False
        )

        # Without pro, should have same or fewer results
        assert len(recs_without_pro) <= len(recs_with_pro)

    def test_recommend_fit_scores(self, recommender):
        """Test that recommendations have fit scores."""
        recs = recommender.recommend_for_use_case("SaaS landing page")
        assert all(0 <= r.fit_score <= 100 for r in recs)

    def test_recommend_reasons(self, recommender):
        """Test that recommendations have reasons."""
        recs = recommender.recommend_for_use_case("dashboard")
        assert all(len(r.reasons) > 0 for r in recs)


class TestRecommendCombination:
    """Test combination recommendations."""

    @pytest.fixture
    def recommender(self):
        """Create a recommender instance."""
        registry = Registry()
        registry.load()
        return Recommender(registry)

    def test_recommend_combination(self, recommender):
        """Test combination recommendations."""
        combo = recommender.recommend_combination("SaaS landing page")
        assert isinstance(combo, dict)
        assert len(combo) > 0

    def test_combination_has_sections(self, recommender):
        """Test that combinations have sections."""
        combo = recommender.recommend_combination("dashboard")
        # Should have multiple sections
        assert len(combo) >= 1

    def test_combination_section_structure(self, recommender):
        """Test that combination sections have proper structure."""
        combo = recommender.recommend_combination("landing page")
        for section, recs in combo.items():
            assert isinstance(section, str)
            assert isinstance(recs, list)
            if recs:
                assert all(hasattr(r, "component") for r in recs)
                assert all(hasattr(r, "fit_score") for r in recs)

    def test_combination_include_pro(self, recommender):
        """Test combination with include_pro parameter."""
        combo_with_pro = recommender.recommend_combination(
            "landing page", include_pro=True
        )
        combo_without_pro = recommender.recommend_combination(
            "landing page", include_pro=False
        )

        # Compare total recommendations
        total_with = sum(len(recs) for recs in combo_with_pro.values())
        total_without = sum(len(recs) for recs in combo_without_pro.values())
        assert total_without <= total_with


class TestMatchToProject:
    """Test project matching functionality."""

    @pytest.fixture
    def recommender(self):
        """Create a recommender instance."""
        registry = Registry()
        registry.load()
        return Recommender(registry)

    def test_match_to_project(self, recommender):
        """Test matching components to project."""
        recs = recommender.match_to_project(
            "Building a fintech dashboard with dark mode"
        )
        assert len(recs) > 0
        assert all(hasattr(r, "component") for r in recs)
        assert all(hasattr(r, "fit_score") for r in recs)

    def test_match_max_results(self, recommender):
        """Test matching respects max_results."""
        recs = recommender.match_to_project("landing page", max_results=10)
        assert len(recs) <= 10

    def test_match_fit_scores(self, recommender):
        """Test that matches have fit scores."""
        recs = recommender.match_to_project("dashboard")
        assert all(0 <= r.fit_score <= 100 for r in recs)

    def test_match_reasons(self, recommender):
        """Test that matches have reasons."""
        recs = recommender.match_to_project("SaaS website")
        assert all(len(r.reasons) > 0 for r in recs)


class TestGeneratePageLayout:
    """Test page layout generation."""

    @pytest.fixture
    def recommender(self):
        """Create a recommender instance."""
        registry = Registry()
        registry.load()
        return Recommender(registry)

    def test_generate_landing_layout(self, recommender):
        """Test generating a landing page layout."""
        layout = recommender.generate_page_layout("startup landing page")
        assert layout.page_type == "landing"
        assert len(layout.sections) > 0
        assert layout.total_components > 0

    def test_generate_dashboard_layout(self, recommender):
        """Test generating a dashboard layout."""
        layout = recommender.generate_page_layout("admin dashboard")
        assert layout.page_type == "dashboard"
        assert len(layout.sections) > 0

    def test_generate_portfolio_layout(self, recommender):
        """Test generating a portfolio layout."""
        layout = recommender.generate_page_layout("creative portfolio showcase")
        assert layout.page_type == "portfolio"
        assert len(layout.sections) > 0

    def test_generate_saas_layout(self, recommender):
        """Test generating a SaaS page layout."""
        layout = recommender.generate_page_layout("SaaS platform product page")
        assert layout.page_type == "saas"
        assert len(layout.sections) > 0

    def test_generate_ecommerce_layout(self, recommender):
        """Test generating an e-commerce layout."""
        layout = recommender.generate_page_layout("online store e-commerce")
        assert layout.page_type == "ecommerce"
        assert len(layout.sections) > 0

    def test_generate_blog_layout(self, recommender):
        """Test generating a blog layout."""
        layout = recommender.generate_page_layout("developer blog articles")
        assert layout.page_type == "blog"
        assert len(layout.sections) > 0

    def test_generate_docs_layout(self, recommender):
        """Test generating a documentation layout."""
        layout = recommender.generate_page_layout("API documentation site")
        assert layout.page_type == "documentation"
        assert len(layout.sections) > 0

    def test_explicit_page_type(self, recommender):
        """Test explicit page type override."""
        layout = recommender.generate_page_layout(
            "some random page", page_type="dashboard"
        )
        assert layout.page_type == "dashboard"

    def test_layout_has_install_commands(self, recommender):
        """Test that layout includes install commands."""
        layout = recommender.generate_page_layout("landing page")
        assert len(layout.install_commands) > 0
        assert all(cmd.startswith("npx") for cmd in layout.install_commands)

    def test_layout_has_dependencies(self, recommender):
        """Test that layout aggregates dependencies."""
        layout = recommender.generate_page_layout("SaaS landing page")
        assert len(layout.all_dependencies) > 0

    def test_layout_has_performance_estimate(self, recommender):
        """Test that layout has performance estimate."""
        layout = recommender.generate_page_layout("landing page")
        assert layout.estimated_performance in (
            "lightweight",
            "moderate",
            "heavy",
            "very heavy",
        )

    def test_layout_sections_have_priority(self, recommender):
        """Test that sections have priority levels."""
        layout = recommender.generate_page_layout("landing page")
        for sec in layout.sections:
            assert sec.priority in (1, 2, 3)

    def test_layout_no_duplicate_components(self, recommender):
        """Test that components are not repeated across sections."""
        layout = recommender.generate_page_layout("SaaS landing page")
        slugs = []
        for sec in layout.sections:
            for rec in sec.components:
                slugs.append(rec.component.slug)
        assert len(slugs) == len(set(slugs))

    def test_layout_sections_have_components(self, recommender):
        """Test that most sections have at least one component."""
        layout = recommender.generate_page_layout("landing page")
        sections_with_comps = sum(1 for s in layout.sections if len(s.components) > 0)
        assert sections_with_comps >= len(layout.sections) // 2

    def test_layout_include_pro(self, recommender):
        """Test include_pro parameter."""
        layout_with = recommender.generate_page_layout("landing page", include_pro=True)
        layout_without = recommender.generate_page_layout(
            "landing page", include_pro=False
        )
        assert layout_without.total_components <= layout_with.total_components

    def test_components_per_section(self, recommender):
        """Test components_per_section parameter."""
        layout = recommender.generate_page_layout(
            "landing page", components_per_section=1
        )
        for sec in layout.sections:
            assert len(sec.components) <= 1

    def test_available_page_types(self):
        """Test available_page_types returns valid types."""
        types = Recommender.available_page_types()
        assert isinstance(types, dict)
        assert "landing" in types
        assert "dashboard" in types
        assert "portfolio" in types
        assert "saas" in types
        assert "ecommerce" in types
        assert "blog" in types
        assert "documentation" in types

    def test_layout_has_batch_install(self, recommender):
        """Test that layout includes batch install command."""
        layout = recommender.generate_page_layout("landing page")
        assert layout.batch_install.startswith("npx shadcn@latest add")
        assert "@aceternity/" in layout.batch_install

    def test_layout_detects_design_tones(self, recommender):
        """Test design tone detection from description."""
        layout = recommender.generate_page_layout(
            "premium dark modern SaaS landing page"
        )
        assert "dark" in layout.design_tones
        assert "premium" in layout.design_tones
        assert "modern" in layout.design_tones
        assert layout.detected_theme != "custom"

    def test_layout_sections_have_build_order(self, recommender):
        """Test that sections have sequential build order."""
        layout = recommender.generate_page_layout("landing page")
        orders = [s.build_order for s in layout.sections]
        assert orders == list(range(1, len(orders) + 1))

    def test_layout_sections_have_implementation_notes(self, recommender):
        """Test that sections include implementation notes."""
        layout = recommender.generate_page_layout("SaaS landing page")
        notes = [s.implementation_note for s in layout.sections]
        assert any(n != "" for n in notes)

    def test_layout_has_dependency_counts(self, recommender):
        """Test that layout tracks dependency statistics."""
        layout = recommender.generate_page_layout("landing page")
        assert layout.unique_dependency_count > 0

    def test_design_tone_coherence(self, recommender):
        """Test that dark theme boosts dark-toned components."""
        layout_dark = recommender.generate_page_layout("dark premium SaaS landing page")
        layout_minimal = recommender.generate_page_layout("clean minimal blog")
        # Different descriptions should produce different layouts
        dark_slugs = {
            rec.component.slug for sec in layout_dark.sections for rec in sec.components
        }
        minimal_slugs = {
            rec.component.slug
            for sec in layout_minimal.sections
            for rec in sec.components
        }
        assert dark_slugs != minimal_slugs

    def test_detect_design_tones_static(self):
        """Test design tone detection as a static method."""
        tones = Recommender._detect_design_tones("dark premium futuristic AI dashboard")
        assert "dark" in tones
        assert "premium" in tones
        assert "tech" in tones

    def test_no_tones_detected(self):
        """Test that no tones are detected for generic description."""
        tones = Recommender._detect_design_tones("a page")
        assert isinstance(tones, set)


class TestRecommenderScoring:
    """Test recommender scoring logic."""

    @pytest.fixture
    def recommender(self):
        """Create a recommender instance."""
        registry = Registry()
        registry.load()
        return Recommender(registry)

    def test_fit_score_range(self, recommender):
        """Test that fit scores are in valid range."""
        recs = recommender.recommend_for_use_case("landing page")
        assert all(0 <= r.fit_score <= 100 for r in recs)

    def test_fit_score_ordering(self, recommender):
        """Test that recommendations are ordered by fit score."""
        recs = recommender.recommend_for_use_case("dashboard")
        if len(recs) > 1:
            for i in range(len(recs) - 1):
                assert recs[i].fit_score >= recs[i + 1].fit_score

    def test_different_use_cases_different_results(self, recommender):
        """Test that different use cases return different results."""
        recs_landing = recommender.recommend_for_use_case("landing page")
        recs_dashboard = recommender.recommend_for_use_case("dashboard")

        # Should have different top recommendations
        if recs_landing and recs_dashboard:
            assert recs_landing[0].component.slug != recs_dashboard[0].component.slug
