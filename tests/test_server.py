"""Tests for MCP server tools."""

import json

from aceternity_mcp.server import (
    filter_by_scores,
    generate_page_layout,
    get_category,
    get_component,
    install_component,
    list_categories,
    list_components,
    match_components_to_project,
    recommend_combination,
    recommend_components,
    search_components,
)


class TestListComponents:
    """Test list_components tool."""

    def test_list_all_components(self):
        """Test listing all components."""
        result = list_components()
        data = json.loads(result)
        assert "total" in data
        assert "components" in data
        assert data["total"] > 0
        assert len(data["components"]) > 0

    def test_list_components_by_category(self):
        """Test listing components by category."""
        result = list_components(category="backgrounds")
        data = json.loads(result)
        assert "total" in data
        assert "components" in data

    def test_list_components_exclude_pro(self):
        """Test listing components without pro."""
        result = list_components(include_pro=False)
        data = json.loads(result)
        assert "total" in data
        assert "components" in data
        # All components should not be pro
        assert all(not c.get("isPro", False) for c in data["components"])


class TestListCategories:
    """Test list_categories tool."""

    def test_list_all_categories(self):
        """Test listing all categories."""
        result = list_categories()
        data = json.loads(result)
        assert "total" in data
        assert "categories" in data
        assert data["total"] > 0
        assert len(data["categories"]) > 0

    def test_category_structure(self):
        """Test category data structure."""
        result = list_categories()
        data = json.loads(result)
        for cat in data["categories"]:
            assert "slug" in cat
            assert "name" in cat
            assert "description" in cat
            assert "componentCount" in cat


class TestSearchComponents:
    """Test search_components tool."""

    def test_search_basic(self):
        """Test basic search."""
        result = search_components("background")
        data = json.loads(result)
        assert "query" in data
        assert "total" in data
        assert "results" in data
        assert data["total"] > 0

    def test_search_with_category(self):
        """Test search with category filter."""
        result = search_components("card", category="cards")
        data = json.loads(result)
        assert "total" in data
        assert "results" in data

    def test_search_max_results(self):
        """Test search respects max_results."""
        result = search_components("background", max_results=5)
        data = json.loads(result)
        assert data["total"] <= 5

    def test_search_relevance(self):
        """Test that search results have relevance scores."""
        result = search_components("spotlight")
        data = json.loads(result)
        if data["results"]:
            assert "relevance" in data["results"][0]


class TestGetComponent:
    """Test get_component tool."""

    def test_get_existing_component(self):
        """Test getting an existing component."""
        # First get a valid slug
        all_comps = json.loads(list_components())
        if all_comps["components"]:
            slug = all_comps["components"][0]["slug"]
            result = get_component(slug)
            data = json.loads(result)
            assert "slug" in data
            assert data["slug"] == slug

    def test_get_nonexistent_component(self):
        """Test getting a nonexistent component."""
        result = get_component("nonexistent-component")
        data = json.loads(result)
        assert "error" in data


class TestGetCategory:
    """Test get_category tool."""

    def test_get_existing_category(self):
        """Test getting an existing category."""
        all_cats = json.loads(list_categories())
        if all_cats["categories"]:
            slug = all_cats["categories"][0]["slug"]
            result = get_category(slug)
            data = json.loads(result)
            assert "slug" in data
            assert data["slug"] == slug

    def test_get_nonexistent_category(self):
        """Test getting a nonexistent category."""
        result = get_category("nonexistent-category")
        data = json.loads(result)
        assert "error" in data


class TestRecommendComponents:
    """Test recommend_components tool."""

    def test_recommend_basic(self):
        """Test basic recommendations."""
        result = recommend_components("landing page with dark theme")
        data = json.loads(result)
        assert "description" in data
        assert "total" in data
        assert "recommendations" in data

    def test_recommend_max_results(self):
        """Test recommendations respect max_results."""
        result = recommend_components("dashboard", max_results=5)
        data = json.loads(result)
        assert data["total"] <= 5

    def test_recommend_fit_score(self):
        """Test that recommendations have fit scores."""
        result = recommend_components("SaaS website")
        data = json.loads(result)
        if data["recommendations"]:
            assert "fitScore" in data["recommendations"][0]


class TestRecommendCombination:
    """Test recommend_combination tool."""

    def test_recommend_combination_basic(self):
        """Test basic combination recommendations."""
        result = recommend_combination("landing page")
        data = json.loads(result)
        assert "description" in data
        assert "sections" in data
        assert isinstance(data["sections"], dict)

    def test_recommend_combination_sections(self):
        """Test that combination has sections."""
        result = recommend_combination("dashboard")
        data = json.loads(result)
        assert len(data["sections"]) >= 1


class TestMatchComponentsToProject:
    """Test match_components_to_project tool."""

    def test_match_basic(self):
        """Test basic project matching."""
        result = match_components_to_project("Building a fintech dashboard")
        data = json.loads(result)
        assert "projectDescription" in data
        assert "total" in data
        assert "matchedComponents" in data

    def test_match_max_results(self):
        """Test matching respects max_results."""
        result = match_components_to_project("landing page", max_results=10)
        data = json.loads(result)
        assert data["total"] <= 10


class TestInstallComponent:
    """Test install_component tool."""

    def test_install_existing_component(self):
        """Test install instructions for existing component."""
        all_comps = json.loads(list_components())
        if all_comps["components"]:
            slug = all_comps["components"][0]["slug"]
            result = install_component(slug)
            data = json.loads(result)
            assert "slug" in data
            assert "installCommand" in data
            assert "steps" in data
            assert len(data["steps"]) > 0

    def test_install_nonexistent_component(self):
        """Test install instructions for nonexistent component."""
        result = install_component("nonexistent")
        data = json.loads(result)
        assert "error" in data


class TestFilterByScores:
    """Test filter_by_scores tool."""

    def test_filter_visual_intensity(self):
        """Test filtering by visual intensity."""
        result = filter_by_scores(min_visual_intensity=7)
        data = json.loads(result)
        assert "total" in data
        assert "components" in data

    def test_filter_animation_intensity(self):
        """Test filtering by animation intensity."""
        result = filter_by_scores(min_animation_intensity=5, max_animation_intensity=8)
        data = json.loads(result)
        assert "total" in data

    def test_filter_landing_page_fit(self):
        """Test filtering by landing page fit."""
        result = filter_by_scores(min_landing_page_fit=8)
        data = json.loads(result)
        assert "total" in data

    def test_filter_performance_impact(self):
        """Test filtering by performance impact."""
        result = filter_by_scores(max_performance_impact=5)
        data = json.loads(result)
        assert "total" in data

    def test_filter_multiple_criteria(self):
        """Test filtering by multiple criteria."""
        result = filter_by_scores(
            min_visual_intensity=5, max_visual_intensity=8, min_landing_page_fit=7
        )
        data = json.loads(result)
        assert "total" in data


class TestGeneratePageLayout:
    """Test generate_page_layout tool."""

    def test_generate_basic(self):
        """Test basic page layout generation."""
        result = generate_page_layout("SaaS landing page with dark theme")
        data = json.loads(result)
        assert "pageType" in data
        assert "sections" in data
        assert "totalComponents" in data
        assert "installCommands" in data
        assert "allDependencies" in data
        assert data["totalComponents"] > 0

    def test_generate_with_page_type(self):
        """Test layout with explicit page type."""
        result = generate_page_layout("my page", page_type="dashboard")
        data = json.loads(result)
        assert data["pageType"] == "dashboard"

    def test_generate_sections_structure(self):
        """Test that sections have proper structure."""
        result = generate_page_layout("portfolio website")
        data = json.loads(result)
        for sec in data["sections"]:
            assert "name" in sec
            assert "role" in sec
            assert "description" in sec
            assert "priority" in sec
            assert "components" in sec
            assert sec["priority"] in ("essential", "recommended", "optional")

    def test_generate_components_have_install(self):
        """Test that components include install commands."""
        result = generate_page_layout("landing page")
        data = json.loads(result)
        for sec in data["sections"]:
            for comp in sec["components"]:
                assert "installCommand" in comp
                assert "fitScore" in comp
                assert "slug" in comp

    def test_generate_has_dependencies(self):
        """Test that layout includes aggregated dependencies."""
        result = generate_page_layout("SaaS product page")
        data = json.loads(result)
        assert isinstance(data["allDependencies"], list)
        assert len(data["allDependencies"]) > 0

    def test_generate_performance_estimate(self):
        """Test that layout has performance estimate."""
        result = generate_page_layout("landing page")
        data = json.loads(result)
        assert data["estimatedPerformance"] in (
            "lightweight",
            "moderate",
            "heavy",
            "very heavy",
        )

    def test_generate_no_duplicate_slugs(self):
        """Test that no component appears in multiple sections."""
        result = generate_page_layout("SaaS landing page")
        data = json.loads(result)
        slugs = []
        for sec in data["sections"]:
            for comp in sec["components"]:
                slugs.append(comp["slug"])
        assert len(slugs) == len(set(slugs))

    def test_generate_components_per_section(self):
        """Test components_per_section parameter."""
        result = generate_page_layout("landing page", components_per_section=1)
        data = json.loads(result)
        for sec in data["sections"]:
            assert len(sec["components"]) <= 1


class TestComponentSummary:
    """Test component summary format."""

    def test_summary_has_required_fields(self):
        """Test that summaries have required fields."""
        result = list_components()
        data = json.loads(result)
        if data["components"]:
            comp = data["components"][0]
            assert "slug" in comp
            assert "name" in comp
            assert "category" in comp
            assert "tags" in comp
            assert "summary" in comp
            assert "isPro" in comp
