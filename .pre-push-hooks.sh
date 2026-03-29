#!/bin/bash
set -e

echo "🔍 Running pre-push validation..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

REGISTRY_INDEX_FILE="registry/index.json"
REGISTRY_RAW_FILE="registry/raw/components.json"
REGISTRY_INDEX_BACKUP=""
REGISTRY_RAW_BACKUP=""

if [ -f "$REGISTRY_INDEX_FILE" ]; then
    REGISTRY_INDEX_BACKUP=$(mktemp)
    cp "$REGISTRY_INDEX_FILE" "$REGISTRY_INDEX_BACKUP"
fi

if [ -f "$REGISTRY_RAW_FILE" ]; then
    REGISTRY_RAW_BACKUP=$(mktemp)
    cp "$REGISTRY_RAW_FILE" "$REGISTRY_RAW_BACKUP"
fi

restore_registry_files() {
    if [ -n "$REGISTRY_INDEX_BACKUP" ] && [ -f "$REGISTRY_INDEX_BACKUP" ]; then
        cp "$REGISTRY_INDEX_BACKUP" "$REGISTRY_INDEX_FILE"
        rm -f "$REGISTRY_INDEX_BACKUP"
    fi

    if [ -n "$REGISTRY_RAW_BACKUP" ] && [ -f "$REGISTRY_RAW_BACKUP" ]; then
        cp "$REGISTRY_RAW_BACKUP" "$REGISTRY_RAW_FILE"
        rm -f "$REGISTRY_RAW_BACKUP"
    fi
}

trap restore_registry_files EXIT

# Function to run a check
run_check() {
    local name=$1
    local command=$2
    echo -n "⏳ $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        eval "$command"
        FAILED=1
        return 1
    fi
}

# 0. Install package in development mode (required for tests)
echo ""
echo "📦 INSTALLING PACKAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "⏳ Installing package... "
if python -m pip install -e . --break-system-packages --quiet > /dev/null 2>&1; then
    echo -e "${GREEN}✓ INSTALLED${NC}"
else
    echo -e "${YELLOW}⚠ INSTALL SKIPPED${NC}"
fi

# 1. Run all tests
echo ""
echo "📊 TEST SUITE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Unit Tests" "pytest tests/ -v --tb=short" || true

# 2. Run with coverage (report only, don't fail)
echo ""
echo "📈 COVERAGE ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "⏳ Coverage Report... "
if pytest --cov=src/aceternity_mcp --cov-report=term-missing tests/ > /tmp/coverage.txt 2>&1; then
    COVERAGE=$(grep "TOTAL" /tmp/coverage.txt | awk '{print $NF}' | sed 's/%//')
    if [ -n "$COVERAGE" ]; then
        echo -e "${GREEN}✓ ${COVERAGE}%${NC}"
    else
        echo -e "${YELLOW}⚠ GENERATED${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SKIPPED${NC}"
fi

# 3. Type checking
echo ""
echo "🔤 TYPE CHECKING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "MyPy" "mypy src/aceternity_mcp/" || true

# 4. Linting (only fail on critical errors in src/)
echo ""
echo "🔍 LINTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "⏳ Ruff Check (errors only)... "
if ruff check src/ --select=E,F 2>&1 | grep -q "error"; then
    echo -e "${RED}✗ FAILED${NC}"
    ruff check src/ --select=E,F
    FAILED=1
else
    echo -e "${GREEN}✓ PASSED${NC}"
fi

echo -n "⏳ Ruff Format... "
if ruff format src/ tests/ --check > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${YELLOW}⚠ NEEDS FORMATTING${NC}"
fi

# 5. Build validation (optional)
echo ""
echo "📦 BUILD VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python -m pip show build > /dev/null 2>&1; then
    rm -rf dist/
    run_check "Build Wheel" "python -m build --wheel --outdir dist/" || true
    run_check "Build Source" "python -m build --sdist --outdir dist/" || true
    rm -rf dist/
else
    echo -e "${YELLOW}⏭️  Skipped (install: pip install build)${NC}"
fi

# 6. Import validation
echo ""
echo "📥 IMPORT VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Module Imports" "python -c 'from aceternity_mcp import cli, server, install, uninstall'" || true

# 7. Registry validation
echo ""
echo "🗂️ REGISTRY VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "scripts/validate_registry.py" ]; then
    run_check "Registry" "python scripts/validate_registry.py" || true
fi

# 8. Security scan (optional)
echo ""
echo "🔒 SECURITY SCAN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v bandit &> /dev/null; then
    run_check "Bandit" "bandit -r src/aceternity_mcp/ -c pyproject.toml" || true
else
    echo -e "${YELLOW}⏭️  Skipped (bandit not installed)${NC}"
fi

# Final result
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED!${NC}"
    echo ""
    echo -e "${YELLOW}Fix issues and re-run, or use 'git push --no-verify' to bypass${NC}"
    echo ""
    exit 1
fi
