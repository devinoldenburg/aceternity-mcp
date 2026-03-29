"""Test configuration and fixtures."""

import pytest
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def test_dir():
    """Get the test directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_component_data():
    """Sample component data for testing."""
    return {
        "slug": "test-component",
        "name": "Test Component",
        "description": "A test component for testing purposes",
        "category": "test",
        "tags": ["test", "sample"],
        "install_command": "npx shadcn-ui@latest add test-component",
        "dependencies": ["react", "framer-motion"],
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "slug": "test-category",
        "name": "Test Category",
        "description": "A test category for testing purposes",
        "component_slugs": ["test-component-1", "test-component-2"],
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


def pytest_collection_modifyitems(config, items):
    """Modify collected test items."""
    # Add 'slow' marker to tests that take longer
    for item in items:
        if "integration" in item.nodeid or "repair" in item.nodeid:
            item.add_marker(pytest.mark.slow)
