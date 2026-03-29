# 🔒 Quality Assurance Quick Reference

## 📋 Quick Start

### Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### Install Git Hooks (Automatic)
```bash
pre-commit install
```

This installs both pre-commit and pre-push hooks automatically.

---

## 🚀 Before Every Commit

The **pre-commit hook** runs automatically and checks:
- ✅ Code formatting (Ruff Format)
- ✅ Linting (Ruff Check)
- ✅ Type hints (MyPy - non-blocking)

If formatting fails, it will auto-fix and stage the changes.

---

## 🚀 Before Every Push

The **pre-push hook** runs automatically and checks:
- ✅ All unit tests pass
- ✅ Code coverage ≥80%
- ✅ Type checking (MyPy strict)
- ✅ Linting (Ruff)
- ✅ Build succeeds (wheel + sdist)
- ✅ All modules import correctly
- ✅ Registry is valid
- ✅ Security scan passes

**This is your final safety net before pushing!**

---

## 🧪 Manual Testing

### Run All Checks Locally
```bash
# Comprehensive check (recommended before committing)
./scripts/run-all-checks.sh

# Or just run tests
pytest tests/ -v

# Check coverage
pytest --cov=src/aceternity_mcp --cov-fail-under=80 tests/

# Type check
mypy src/aceternity_mcp/ --strict

# Lint
ruff check src/ tests/ scripts/

# Format
ruff format src/ tests/ scripts/

# Build
python -m build --wheel --sdist

# Validate registry
python scripts/validate_registry.py
```

---

## 🆘 Emergency Bypass (NOT RECOMMENDED)

### Bypass Pre-Commit
```bash
git commit --no-verify -m "your message"
```

### Bypass Pre-Push
```bash
git push --no-verify
```

⚠️ **WARNING**: Bypassing will cause CI/CD to fail and should only be used in emergencies!

---

## 📊 Quality Gates

| Check | Tool | Threshold | Blocking |
|-------|------|-----------|----------|
| Formatting | Ruff | 100% | ✅ Pre-commit |
| Linting | Ruff | 0 errors | ✅ Pre-commit |
| Types | MyPy | Strict | ⚠️ Warning |
| Tests | Pytest | 100% pass | ✅ Pre-push |
| Coverage | Pytest-cov | ≥80% | ✅ Pre-push |
| Build | build | Success | ✅ Pre-push |
| Security | Bandit | 0 issues | ⚠️ Warning |
| Registry | Custom | Valid JSON | ✅ Pre-push |

---

## 🔧 Troubleshooting

### Pre-commit hook failing on formatting?
```bash
ruff format src/ tests/ scripts/
git add -u
git commit
```

### Tests failing?
```bash
pytest tests/ -v --tb=long
```

### Type errors?
```bash
mypy src/aceternity_mcp/ --strict --show-error-codes
```

### Build failing?
```bash
python -m build --wheel --sdist --verbose
```

### Registry validation failing?
```bash
python scripts/validate_registry.py
```

---

## 📝 Best Practices

1. **Run checks early**: Run `./scripts/run-all-checks.sh` before committing
2. **Small commits**: Make small, focused commits for faster feedback
3. **Fix immediately**: Address issues as soon as they appear
4. **Don't bypass**: Only bypass in true emergencies
5. **Update tests**: When adding features, add tests first (TDD)

---

## 🎯 Why So Many Checks?

Each check catches different types of issues:

- **Formatting**: Consistency and readability
- **Linting**: Bugs, anti-patterns, style issues
- **Types**: Type safety, better IDE support
- **Tests**: Functional correctness
- **Coverage**: Test completeness
- **Build**: Package integrity
- **Security**: Vulnerability detection
- **Registry**: Data integrity

**Multiple layers = Better protection against bugs!** 🛡️

---

## 📞 Need Help?

If you're stuck:
1. Read the error message carefully
2. Check the specific tool's documentation
3. Run the check in isolation to debug
4. Ask team members for help

Remember: These checks are here to **help you**, not slow you down! 🚀
