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
