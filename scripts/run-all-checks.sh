#!/bin/bash
# Comprehensive quality assurance script
# Run this before every commit to ensure code quality

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     COMPREHENSIVE QUALITY ASSURANCE CHECK                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

run_check() {
    local name=$1
    local command=$2
    local critical=${3:-true}

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}⏳ CHECK $TOTAL_CHECKS: $name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if eval "$command" > /tmp/check_output_$$.txt 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        rm -f /tmp/check_output_$$.txt
        return 0
    else
        if [ "$critical" = "true" ]; then
            echo -e "${RED}❌ FAILED (Critical)${NC}"
            cat /tmp/check_output_$$.txt
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            rm -f /tmp/check_output_$$.txt
            return 1
        else
            echo -e "${YELLOW}⚠️  FAILED (Non-critical)${NC}"
            cat /tmp/check_output_$$.txt
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            rm -f /tmp/check_output_$$.txt
            return 0
        fi
    fi
}

# 1. Code Formatting
run_check "Code Formatting (Ruff Format)" "ruff format src/ tests/ scripts/ --check"

# 2. Linting
run_check "Code Linting (Ruff Check)" "ruff check src/ tests/ scripts/"

# 3. Type Checking
run_check "Type Checking (MyPy Strict)" "mypy src/aceternity_mcp/ scripts/ tests/" false

# 4. Unit Tests
run_check "Unit Tests (Pytest)" "pytest tests/ -v --tb=short"

# 5. Coverage
run_check "Code Coverage (40% min)" "pytest --cov=src/aceternity_mcp --cov-fail-under=40 tests/ -q"

# 6. Security Scan
run_check "Security Scan (Bandit)" "bandit -r src/aceternity_mcp/ -c pyproject.toml" false

# 7. Build Wheel
run_check "Build Wheel" "python -m build --wheel --outdir dist/"

# 8. Build Source
run_check "Build Source Distribution" "python -m build --sdist --outdir dist/"

# 9. Import Test
run_check "Module Imports" "python -c 'from aceternity_mcp import cli, server, install, uninstall'"

# 10. Registry Validation
if [ -f "scripts/validate_registry.py" ]; then
    run_check "Registry Validation" "python scripts/validate_registry.py"
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Total Checks:  $TOTAL_CHECKS"
echo -e "Passed:        ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed:        ${RED}$FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL CHECKS PASSED! Code is ready to commit!          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME CHECKS FAILED! Please fix issues above.         ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}To bypass (NOT RECOMMENDED): git commit --no-verify${NC}"
    echo ""
    exit 1
fi
