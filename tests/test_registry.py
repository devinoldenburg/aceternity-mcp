"""Tests for registry loading and management."""

import json

import pytest

from aceternity_mcp.registry import Registry, _find_registry_dir


class TestFindRegistryDir:
    """Test registry directory detection."""

    def test_find_registry_in_pipx(self):
        """Test finding registry in pipx installation."""
        # This test assumes the registry is properly installed
        registry_dir = _find_registry_dir()
        assert registry_dir.exists()
        assert registry_dir.is_dir()
        assert (registry_dir / "components").exists()
        assert (registry_dir / "categories").exists()
        assert (registry_dir / "index.json").exists()

    def test_registry_has_components(self):
        """Test that registry contains component files."""
        registry_dir = _find_registry_dir()
        components_dir = registry_dir / "components"
        component_files = list(components_dir.glob("*.json"))
        assert len(component_files) > 0

    def test_registry_has_categories(self):
        """Test that registry contains category files."""
        registry_dir = _find_registry_dir()
        categories_dir = registry_dir / "categories"
        category_files = list(categories_dir.glob("*.json"))
        assert len(category_files) > 0


class TestRegistryLoading:
    """Test registry loading functionality."""

    @pytest.fixture
    def registry(self):
        """Create a loaded registry instance."""
        reg = Registry()
        reg.load()
        return reg

    def test_registry_loads(self, registry):
        """Test that registry loads successfully."""
        assert registry.is_loaded

    def test_registry_has_components(self, registry):
        """Test that registry contains components."""
        assert registry.component_count > 0
        components = registry.all_components()
        assert len(components) > 0

    def test_registry_has_categories(self, registry):
        """Test that registry contains categories."""
        assert registry.category_count > 0
        categories = registry.all_categories()
        assert len(categories) > 0

    def test_component_slugs(self, registry):
        """Test that component slugs are returned."""
        slugs = registry.component_slugs()
        assert len(slugs) > 0
        assert isinstance(slugs[0], str)

    def test_category_slugs(self, registry):
        """Test that category slugs are returned."""
        slugs = registry.category_slugs()
        assert len(slugs) > 0
        assert isinstance(slugs[0], str)


class TestRegistryAccess:
    """Test registry access methods."""

    @pytest.fixture
    def registry(self):
        """Create a loaded registry instance."""
        reg = Registry()
        reg.load()
        return reg

    def test_get_component(self, registry):
        """Test getting a component by slug."""
        slugs = registry.component_slugs()
        if slugs:
            component = registry.get_component(slugs[0])
            assert component is not None
            assert component.slug == slugs[0]

    def test_get_nonexistent_component(self, registry):
        """Test getting a nonexistent component."""
        component = registry.get_component("nonexistent-component-12345")
        assert component is None

    def test_get_category(self, registry):
        """Test getting a category by slug."""
        categories = registry.category_slugs()
        if categories:
            category = registry.get_category(categories[0])
            assert category is not None
            assert category.slug == categories[0]

    def test_get_nonexistent_category(self, registry):
        """Test getting a nonexistent category."""
        category = registry.get_category("nonexistent-category")
        assert category is None

    def test_components_in_category(self, registry):
        """Test getting components in a category."""
        categories = registry.category_slugs()
        if categories:
            components = registry.components_in_category(categories[0])
            # Components may or may not be in a specific category
            assert isinstance(components, list)


class TestComponentModel:
    """Test AceternityComponent model."""

    @pytest.fixture
    def registry(self):
        """Create a loaded registry instance."""
        reg = Registry()
        reg.load()
        return reg

    def test_component_has_required_fields(self, registry):
        """Test that components have required fields."""
        components = registry.all_components()
        if components:
            comp = components[0]
            assert hasattr(comp, "slug")
            assert hasattr(comp, "name")
            assert hasattr(comp, "category")
            assert hasattr(comp, "detailed_description")

    def test_component_to_dict(self, registry):
        """Test converting component to dict."""
        components = registry.all_components()
        if components:
            comp = components[0]
            data = comp.to_dict()
            assert isinstance(data, dict)
            assert "slug" in data
            assert "name" in data

    def test_component_install_command(self, registry):
        """Test that components have install commands."""
        components = registry.all_components()
        if components:
            comp = components[0]
            assert comp.install_command is not None
            assert len(comp.install_command) > 0


class TestCategoryModel:
    """Test Category model."""

    @pytest.fixture
    def registry(self):
        """Create a loaded registry instance."""
        reg = Registry()
        reg.load()
        return reg

    def test_category_has_required_fields(self, registry):
        """Test that categories have required fields."""
        categories = registry.all_categories()
        if categories:
            cat = categories[0]
            assert hasattr(cat, "slug")
            assert hasattr(cat, "name")
            assert hasattr(cat, "description")

    def test_category_to_dict(self, registry):
        """Test converting category to dict."""
        categories = registry.all_categories()
        if categories:
            cat = categories[0]
            data = cat.to_dict()
            assert isinstance(data, dict)
            assert "slug" in data
            assert "name" in data


class TestRegistryIndex:
    """Test registry index file."""

    def test_index_file_exists(self):
        """Test that index.json exists."""
        registry_dir = _find_registry_dir()
        index_file = registry_dir / "index.json"
        assert index_file.exists()

    def test_index_file_valid_json(self):
        """Test that index.json is valid JSON."""
        registry_dir = _find_registry_dir()
        index_file = registry_dir / "index.json"
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_index_has_components(self):
        """Test that index contains components."""
        registry_dir = _find_registry_dir()
        index_file = registry_dir / "index.json"
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "components" in data
        assert len(data["components"]) > 0

    def test_index_has_categories(self):
        """Test that index contains categories."""
        registry_dir = _find_registry_dir()
        index_file = registry_dir / "index.json"
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "categories" in data
        assert len(data["categories"]) > 0


class TestRegistryComponents:
    """Test individual component files."""

    def test_component_files_valid(self):
        """Test that all component files are valid JSON."""
        registry_dir = _find_registry_dir()
        components_dir = registry_dir / "components"

        for component_file in components_dir.glob("*.json"):
            with open(component_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "slug" in data
            assert "name" in data
            assert "detailedDescription" in data or "description" in data

    def test_component_has_description(self):
        """Test that components have descriptions."""
        registry_dir = _find_registry_dir()
        components_dir = registry_dir / "components"

        component_files = list(components_dir.glob("*.json"))[:5]  # Test first 5
        for component_file in component_files:
            with open(component_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check both possible field names
            has_desc = "detailedDescription" in data or "description" in data
            assert has_desc
            desc = data.get("detailedDescription", data.get("description", ""))
            assert len(desc) > 0


class TestRegistryCategories:
    """Test individual category files."""

    def test_category_files_valid(self):
        """Test that all category files are valid JSON."""
        registry_dir = _find_registry_dir()
        categories_dir = registry_dir / "categories"

        for category_file in categories_dir.glob("*.json"):
            with open(category_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "slug" in data
            assert "name" in data

    def test_category_has_components(self):
        """Test that categories have components."""
        registry_dir = _find_registry_dir()
        categories_dir = registry_dir / "categories"

        category_files = list(categories_dir.glob("*.json"))[:5]  # Test first 5
        for category_file in category_files:
            with open(category_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check for either component_slugs or components
            has_components = "component_slugs" in data or "components" in data
            assert has_components
            if "component_slugs" in data:
                assert isinstance(data["component_slugs"], list)
            if "components" in data:
                assert isinstance(data["components"], list)
