#!/bin/bash
# Setup script for comprehensive quality assurance

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Setting Up Comprehensive Quality Assurance System       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Install Python dependencies
echo -e "${BLUE}📦 Installing Python development dependencies...${NC}"
python -m pip install --break-system-packages -e ".[dev]" 2>/dev/null || \
    python -m pip install --break-system-packages ruff mypy pytest pytest-cov build bandit pre-commit

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# 2. Install Git hooks
echo -e "${BLUE}🔧 Installing Git hooks...${NC}"

# Pre-commit hook
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hook installed${NC}"
else
    # Use custom hook
    cp .git/hooks/pre-commit.sample .git/hooks/pre-commit.bak 2>/dev/null || true
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✓ Custom pre-commit hook activated${NC}"
fi

# Pre-push hook
chmod +x .git/hooks/pre-push
chmod +x .pre-push-hooks.sh
echo -e "${GREEN}✓ Pre-push hook installed${NC}"
echo ""

# 3. Verify installation
echo -e "${BLUE}🔍 Verifying installation...${NC}"

echo -n "  • Ruff: "
if command -v ruff &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "  • MyPy: "
if command -v mypy &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "  • Pytest: "
if command -v pytest &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "  • Pre-commit: "
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""

# 4. Run initial validation
echo -e "${BLUE}🧪 Running initial validation...${NC}"
if ./scripts/run-all-checks.sh; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ Setup Complete! All checks passing!                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
else
    echo ""
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  Setup complete, but some checks are failing.        ║${NC}"
    echo -e "${YELLOW}║  Please fix the issues above before committing.          ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • AGENTS.md - Quality assurance overview"
echo "  • QUALITY_CHECKS.md - Quick reference guide"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "  1. Review QUALITY_CHECKS.md for usage"
echo "  2. Run './scripts/run-all-checks.sh' before committing"
echo "  3. Hooks will run automatically on commit/push"
echo ""
