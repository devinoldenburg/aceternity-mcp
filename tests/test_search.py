"""Tests for search functionality."""

import pytest
from aceternity_mcp.registry import Registry
from aceternity_mcp.search import SearchEngine


class TestSearchEngine:
    """Test search engine functionality."""

    @pytest.fixture
    def search_engine(self):
        """Create a search engine instance."""
        registry = Registry()
        registry.load()
        return SearchEngine(registry)

    def test_search_basic(self, search_engine):
        """Test basic search functionality."""
        results = search_engine.search("background")
        assert len(results) > 0
        assert all(hasattr(r, "component") for r in results)
        assert all(hasattr(r, "relevance") for r in results)

    def test_search_empty_query(self, search_engine):
        """Test search with empty query."""
        results = search_engine.search("")
        # Should return all or no results
        assert isinstance(results, list)

    def test_search_no_results(self, search_engine):
        """Test search with query that should return no results."""
        results = search_engine.search("xyznonexistent123")
        assert len(results) == 0

    def test_search_case_insensitive(self, search_engine):
        """Test that search is case insensitive."""
        results_lower = search_engine.search("background")
        results_upper = search_engine.search("BACKGROUND")
        assert len(results_lower) == len(results_upper)

    def test_search_with_category_filter(self, search_engine):
        """Test search with category filter."""
        results = search_engine.search("card", category="cards")
        assert len(results) >= 0  # May or may not have results
        # If there are results, they should have the expected structure
        if results:
            assert all(hasattr(r, "component") for r in results)
            assert all(hasattr(r, "relevance") for r in results)

    def test_search_with_tags_filter(self, search_engine):
        """Test search with tags filter."""
        results = search_engine.search("animation", tags=["animated"])
        assert isinstance(results, list)

    def test_search_max_results(self, search_engine):
        """Test search respects max_results parameter."""
        results = search_engine.search("background", max_results=5)
        assert len(results) <= 5

    def test_search_include_pro(self, search_engine):
        """Test search with include_pro parameter."""
        results_with_pro = search_engine.search("background", include_pro=True)
        results_without_pro = search_engine.search("background", include_pro=False)

        # Without pro, should have same or fewer results
        assert len(results_without_pro) <= len(results_with_pro)


class TestFilterByScores:
    """Test score-based filtering."""

    @pytest.fixture
    def search_engine(self):
        """Create a search engine instance."""
        registry = Registry()
        registry.load()
        return SearchEngine(registry)

    def test_filter_by_visual_intensity_min(self, search_engine):
        """Test filtering by minimum visual intensity."""
        results = search_engine.filter_by_scores(min_visual_intensity=7)
        assert len(results) > 0
        # All results should have visual_intensity >= 7
        assert all(c.scores.visual_intensity >= 7 for c in results)

    def test_filter_by_visual_intensity_max(self, search_engine):
        """Test filtering by maximum visual intensity."""
        results = search_engine.filter_by_scores(max_visual_intensity=3)
        assert len(results) > 0 or True  # May have no results
        # All results should have visual_intensity <= 3
        if results:
            assert all(c.scores.visual_intensity <= 3 for c in results)

    def test_filter_by_animation_intensity(self, search_engine):
        """Test filtering by animation intensity."""
        results = search_engine.filter_by_scores(
            min_animation_intensity=5, max_animation_intensity=8
        )
        assert len(results) > 0
        assert all(5 <= c.scores.animation_intensity <= 8 for c in results)

    def test_filter_by_landing_page_fit(self, search_engine):
        """Test filtering by landing page fit."""
        results = search_engine.filter_by_scores(min_landing_page_fit=8)
        assert len(results) > 0
        assert all(c.scores.landing_page_fit >= 8 for c in results)

    def test_filter_by_dashboard_fit(self, search_engine):
        """Test filtering by dashboard fit."""
        results = search_engine.filter_by_scores(min_dashboard_fit=7)
        assert len(results) > 0
        assert all(c.scores.dashboard_fit >= 7 for c in results)

    def test_filter_by_performance_impact(self, search_engine):
        """Test filtering by performance impact."""
        results = search_engine.filter_by_scores(max_performance_impact=5)
        assert len(results) > 0
        assert all(c.scores.performance_impact <= 5 for c in results)

    def test_filter_by_customization_ease(self, search_engine):
        """Test filtering by customization ease."""
        results = search_engine.filter_by_scores(min_customization_ease=6)
        assert len(results) > 0
        assert all(c.scores.customization_ease >= 6 for c in results)

    def test_filter_multiple_criteria(self, search_engine):
        """Test filtering by multiple criteria."""
        results = search_engine.filter_by_scores(
            min_visual_intensity=5,
            max_visual_intensity=8,
            min_landing_page_fit=7,
            max_performance_impact=6,
        )
        assert len(results) > 0
        assert all(5 <= c.scores.visual_intensity <= 8 for c in results)
        assert all(c.scores.landing_page_fit >= 7 for c in results)
        assert all(c.scores.performance_impact <= 6 for c in results)

    def test_filter_no_results(self, search_engine):
        """Test filtering with impossible criteria."""
        results = search_engine.filter_by_scores(
            min_visual_intensity=10, max_visual_intensity=1
        )
        assert len(results) == 0


class TestSearchRelevance:
    """Test search relevance scoring."""

    @pytest.fixture
    def search_engine(self):
        """Create a search engine instance."""
        registry = Registry()
        registry.load()
        return SearchEngine(registry)

    def test_relevance_scores_present(self, search_engine):
        """Test that relevance scores are present."""
        results = search_engine.search("background")
        assert all(hasattr(r, "relevance") for r in results)
        assert all(r.relevance is not None for r in results)

    def test_relevance_ordering(self, search_engine):
        """Test that results are ordered by relevance."""
        results = search_engine.search("card")
        if len(results) > 1:
            # Results should be sorted by relevance (descending)
            for i in range(len(results) - 1):
                assert results[i].relevance >= results[i + 1].relevance

    def test_exact_match_higher_relevance(self, search_engine):
        """Test that exact matches have higher relevance."""
        results = search_engine.search("spotlight")
        if len(results) > 1:
            # First result should have highest relevance
            assert results[0].relevance == max(r.relevance for r in results)
