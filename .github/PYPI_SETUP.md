# PyPI Trusted Publishing Setup for Aceternity MCP

## Overview

This repository uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) for secure, automated PyPI releases without storing API keys as secrets.

## How It Works

1. **Tag-based publishing**: Push a version tag (e.g., `v1.0.0`) to trigger automatic PyPI publication
2. **GitHub Actions**: The workflow builds the package and publishes using OIDC authentication
3. **No API keys needed**: Uses GitHub's OIDC tokens for secure authentication

## Setup Instructions

### Step 1: Create PyPI Project

1. Go to https://pypi.org/manage/projects/add/
2. Search for "aceternity-mcp" or create a new project
3. Once created, go to project settings → "Publishing" tab

### Step 2: Add Trusted Publisher

In the PyPI project settings:

1. Click "Add trusted publisher"
2. Select "GitHub Actions"
3. Fill in the details:
   - **Workflow**: `.github/workflows/pypi-publish.yml`
   - **Repository**: `devinoldenburg/aceternity-mcp`
   - **Environment**: `pypi` (or leave blank for all environments)
   - **Branch**: `main` (or your default branch)

4. Click "Add publisher"

### Step 3: Create PyPI Environment (Optional but Recommended)

In GitHub repository settings:

1. Go to Settings → Environments
2. Click "New environment"
3. Name it `pypi`
4. (Optional) Add required reviewers for manual approval
5. Save

### Step 4: Test the Workflow

#### Option A: Tag-based Publishing

```bash
# Create and push a test tag
git tag v0.0.1-test
git push origin v0.0.1-test
```

This will trigger the workflow automatically.

#### Option B: Manual Dispatch

1. Go to Actions tab in GitHub
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Enter version number (e.g., `0.0.1-test`)
5. Click "Run workflow"

### Step 5: Verify Publication

Check that your package was published:
- https://pypi.org/project/aceternity-mcp/

## Publishing a New Release

### Standard Release Flow

```bash
# 1. Update version in pyproject.toml (if not using auto-versioning)
# Edit pyproject.toml and update: version = "1.0.0"

# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 1.0.0"

# 3. Create version tag
git tag v1.0.0

# 4. Push tag to trigger deployment
git push origin v1.0.0
```

### Pre-release

```bash
# Create a pre-release tag
git tag v1.0.0rc1
git push origin v1.0.0rc1
```

The workflow will automatically detect pre-release tags and publish accordingly.

## Workflow Features

### Automatic Version Detection

The workflow automatically:
- Extracts version from tag name (removes 'v' prefix)
- Updates `pyproject.toml` before building
- Uses the version for GitHub release name

### Build Verification

Before publishing:
- Builds both wheel and source distribution
- Runs `twine check` to verify metadata
- Fails fast if package is invalid

### GitHub Release Creation

After successful PyPI publish:
- Automatically creates a GitHub release
- Generates release notes from commits
- Links to PyPI project page

### Security Features

- ✅ No API keys stored
- ✅ Uses OIDC authentication
- ✅ Permission-scoped tokens
- ✅ Environment protection rules
- ✅ Audit trail in both GitHub and PyPI

## Manual Publishing (Fallback)

If automated publishing fails, you can publish manually:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Then upload to PyPI
twine upload dist/*
```

You'll need a PyPI API token for manual uploads:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YourPyPITokenHere
```

## Troubleshooting

### Workflow Fails at Publishing

Check:
1. Trusted publisher is correctly configured in PyPI
2. Repository name matches exactly (including organization)
3. Workflow file path is correct
4. Environment name matches (if using environments)

### "Forbidden" Error

This usually means:
- Trusted publisher not configured correctly
- Repository/owner name mismatch
- Branch protection rules blocking the workflow

### Package Already Exists

If you try to publish the same version twice:
- PyPI doesn't allow overwriting published versions
- You must increment the version number
- For testing, use TestPyPI: `twine upload --repository testpypi dist/*`

## Testing with TestPyPI

Before publishing to real PyPI, test with TestPyPI:

### Add TestPyPI Publisher

1. Go to https://test.pypi.org/manage/projects/add/
2. Create project "aceternity-mcp" (if doesn't exist)
3. Add trusted publisher (same as above but for test.pypi.org)

### Update Workflow for Testing

Create a separate workflow file `.github/workflows/pypi-test.yml`:

```yaml
name: Publish to TestPyPI

on:
  push:
    branches:
      - main

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/p/aceternity-mcp
    permissions:
      contents: read
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
      - run: twine check dist/*
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

## Version Management

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Versions

- `1.0.0alpha1` or `1.0.0a1` - Alpha release
- `1.0.0beta1` or `1.0.0b1` - Beta release
- `1.0.0rc1` - Release candidate
- `1.0.0.dev1` - Development release

### Automated Version Bumping (Optional)

Install bump2version for automated version management:

```bash
pip install bump2version
```

Create `.bumpversion.cfg`:

```ini
[bumpversion]
current_version = 1.0.0
commit = True
tag = True
parse = (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)((?P<release>[a-z]+)(?P<build>\d+))?
serialize = 
    {major}.{minor}.{patch}{release}{build}
    {major}.{minor}.{patch}

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"
```

Usage:

```bash
# Bump patch version (1.0.0 → 1.0.1)
bump2version patch

# Bump minor version (1.0.0 → 1.1.0)
bump2version minor

# Bump major version (1.0.0 → 2.0.0)
bump2version major

# Create pre-release
bump2version --new-version 1.0.0rc1 release
```

## CI/CD Pipeline Integration

The publishing workflow integrates with your CI/CD:

```
Push to main → Run tests → Build → (Manual tag) → Publish to PyPI
```

Recommended workflow:

1. All PRs must pass CI tests
2. Merge to main branch
3. Run tests on main
4. Create version tag
5. Push tag to trigger PyPI publish
6. GitHub release created automatically

## Links and Resources

- [PyPI Trusted Publishing Docs](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions PyPI Publisher](https://github.com/pypa/gh-action-pypi-publish)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [TestPyPI](https://test.pypi.org/)

## Support

If you encounter issues:

1. Check workflow run logs in GitHub Actions
2. Verify trusted publisher configuration in PyPI
3. Test with TestPyPI first
4. Check PyPI's [status page](https://status.python.org/)
5. Open an issue in this repository

---

**Last Updated**: 2026-03-29
**Workflow Version**: 1.0.0
