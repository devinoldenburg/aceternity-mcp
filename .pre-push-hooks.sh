#!/bin/bash
set -e

echo "🔍 Running comprehensive pre-push validation..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to run a check
run_check() {
    local name=$1
    local command=$2
    echo -n "⏳ Running $name... "
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

# 1. Run all tests
echo ""
echo "📊 TEST SUITE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Unit Tests" "pytest tests/ -v --tb=short" || true

# 2. Run with coverage
echo ""
echo "📈 COVERAGE ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Coverage Check (80% minimum)" "pytest --cov=src/aceternity_mcp --cov-report=term-missing --cov-fail-under=80 tests/" || true

# 3. Type checking
echo ""
echo "🔤 TYPE CHECKING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "MyPy Strict" "mypy src/aceternity_mcp/ --strict --no-implicit-any --disallow-untyped-defs" || true

# 4. Linting
echo ""
echo "🔍 LINTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Ruff Check" "ruff check src/ tests/" || true
run_check "Ruff Format Check" "ruff format src/ tests/ --check" || true

# 5. Build validation
echo ""
echo "📦 BUILD VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Build Wheel" "python -m build --wheel --outdir dist/" || true
run_check "Build Source" "python -m build --sdist --outdir dist/" || true

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
    run_check "Registry Schema" "python scripts/validate_registry.py" || true
fi

# 8. Security scan
echo ""
echo "🔒 SECURITY SCAN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_check "Bandit Security" "bandit -r src/aceternity_mcp/ -c pyproject.toml" || true

# Final result
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED! Ready to push!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED! Please fix the issues above before pushing.${NC}"
    echo ""
    echo -e "${YELLOW}To bypass this check (NOT RECOMMENDED), use:${NC}"
    echo "  git push --no-verify"
    echo ""
    exit 1
fi
