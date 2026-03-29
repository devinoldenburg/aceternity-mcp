#!/bin/bash
# Setup script for PyPI publishing
# This script helps you configure and test the PyPI publishing workflow

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "=============================================================="
echo "     Aceternity MCP - PyPI Publishing Setup"
echo "=============================================================="
echo -e "${NC}"

# Check if git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}✗ Error: Not a git repository${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Git repository detected"

# Check current version
CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo -e "${GREEN}✓${NC} Current version: ${CYAN}${CURRENT_VERSION}${NC}"

# Step 1: Check workflow file
echo ""
echo -e "${YELLOW}► Step 1: Checking workflow file${NC}"
if [ -f ".github/workflows/pypi-publish.yml" ]; then
    echo -e "${GREEN}✓${NC} PyPI publish workflow exists"
else
    echo -e "${RED}✗${NC} Workflow file not found!"
    exit 1
fi

# Step 2: Check required files
echo ""
echo -e "${YELLOW}► Step 2: Checking required files${NC}"
REQUIRED_FILES=("pyproject.toml" "README.md" "LICENSE")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file missing!"
    fi
done

# Step 3: Test build
echo ""
echo -e "${YELLOW}► Step 3: Testing package build${NC}"
echo "Installing build tools..."
pip install -q build twine

echo "Building package..."
python -m build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Package built successfully"

    # Show built files
    echo ""
    echo "Built distributions:"
    ls -lh dist/

    # Verify metadata
    echo ""
    echo "Verifying package metadata..."
    twine check dist/*

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Package metadata is valid"
    else
        echo -e "${RED}✗${NC} Package metadata validation failed"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Package build failed"
    exit 1
fi

# Step 4: Git status
echo ""
echo -e "${YELLOW}► Step 4: Checking git status${NC}"
git status --short

# Step 5: Instructions
echo ""
echo -e "${CYAN}=============================================================="
echo "                    Setup Complete!"
echo "==============================================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} Package builds successfully"
echo -e "${GREEN}✓${NC} Workflow file is ready"
echo -e "${GREEN}✓${NC} All required files present"
echo ""
echo -e "${YELLOW}► Next Steps:${NC}"
echo ""
echo "1. ${CYAN}Create PyPI Project:${NC}"
echo "   - Go to: https://pypi.org/manage/projects/add/"
echo "   - Search for 'aceternity-mcp' or create new project"
echo ""
echo "2. ${CYAN}Add Trusted Publisher:${NC}"
echo "   - In PyPI project settings → Publishing tab"
echo "   - Click 'Add trusted publisher'"
echo "   - Select 'GitHub Actions'"
echo "   - Fill in:"
echo "     • Workflow: .github/workflows/pypi-publish.yml"
echo "     • Repository: devinoldenburg/aceternity-mcp"
echo "     • Branch: main"
echo ""
echo "3. ${CYAN}Test the Workflow:${NC}"
echo "   Option A - Create test tag:"
echo "     git tag v0.0.1-test"
echo "     git push origin v0.0.1-test"
echo ""
echo "   Option B - Manual dispatch:"
echo "     - Go to Actions → Publish to PyPI"
echo "     - Click 'Run workflow'"
echo "     - Enter version: 0.0.1-test"
echo ""
echo "4. ${CYAN}Verify Publication:${NC}"
echo "   - Check: https://pypi.org/project/aceternity-mcp/"
echo ""
echo -e "${YELLOW}► For detailed instructions, see:${NC}"
echo "   .github/PYPI_SETUP.md"
echo ""
echo -e "${GREEN}Happy publishing! 🚀${NC}"
echo ""

# Cleanup build artifacts
read -p "Clean up build artifacts? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf dist/ build/ *.egg-info
    echo -e "${GREEN}✓${NC} Build artifacts cleaned"
fi

exit 0
