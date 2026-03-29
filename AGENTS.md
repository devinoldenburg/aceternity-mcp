# AGENTS.md - Automated Quality Assurance System

## Pre-Commit & Pre-Push Validation Pipeline

This project enforces strict quality gates that must pass before any code can be committed or pushed.

---

## Pre-Commit Checks (Run Automatically)

Before any commit is accepted, the following checks run automatically:

### 1. Code Formatting
- **Ruff Format**: Ensures consistent code style
- **Line Length**: Max 88 characters
- **Import Sorting**: Automatic organization

### 2. Linting & Static Analysis
- **Ruff Linter**: Catches errors, bugs, and style issues
- **PyUpgrade**: Ensures modern Python syntax
- **Security Checks**: Detects security vulnerabilities

### 3. Type Checking
- **MyPy**: Strict static type checking
- **Type Coverage**: All functions must be typed
- **No Any**: Strict avoidance of `Any` type

### 4. Code Quality
- **Complexity Checks**: Cyclomatic complexity limits
- **Code Duplication**: Detects copy-paste code
- **Best Practices**: Enforces Python best practices

---

## Pre-Push Checks (Run Automatically)

Before any push to remote, all of these tests must pass:

### 1. Unit Tests
```bash
pytest tests/ -v --tb=short
```
- All unit tests must pass
- No test failures allowed
- Test coverage must be maintained

### 2. Integration Tests
```bash
pytest tests/ -m integration -v
```
- End-to-end functionality verified
- Component interactions tested

### 3. Coverage Validation
```bash
pytest --cov=src/aceternity_mcp --cov-report=term-missing --cov-fail-under=80
```
- Minimum 80% code coverage required
- Missing coverage reported

### 4. Build Validation
```bash
python -m build --wheel --sdist
```
- Package builds successfully
- No build warnings or errors

### 5. Import Validation
```bash
python -c "from aceternity_mcp import cli, server, install, uninstall"
```
- All modules importable
- No circular dependencies

### 6. Registry Validation
```bash
python scripts/validate_registry.py
```
- All registry entries valid
- Component schemas correct
- No broken references

### 7. Documentation Checks
- All public functions have docstrings
- Type hints present
- README up to date

---

## CI/CD Pipeline (GitHub Actions)

On every push to any branch, GitHub Actions runs:

### Workflow: `quality-gates.yml`
1. **Setup**: Python 3.10, 3.11, 3.12, 3.13
2. **Install Dependencies**: All dev and test dependencies
3. **Lint**: Ruff, MyPy
4. **Test**: All pytest suites
5. **Coverage**: Report generation
6. **Build**: Wheel and sdist
7. **Security**: Dependency vulnerability scan

### Workflow: `publish.yml`
- Only runs on tagged releases
- Requires all quality gates to pass
- Manual approval required

---

## Required Tools

Install all development dependencies:

```bash
pip install -e ".[dev]"
```

Or install tools individually:

```bash
pip install ruff mypy pytest pytest-cov build
```

---

## Configuration Files

- `pyproject.toml`: Tool configurations
- `.pre-commit-config.yaml`: Pre-commit hooks
- `.ruff.toml`: Ruff linting rules
- `mypy.ini`: MyPy type checking settings
- `.github/workflows/`: CI/CD pipelines

---

## Breaking Changes Policy

If you need to introduce a breaking change:

1. Update version number (semver major)
2. Add migration guide to README
3. Add deprecation warnings in code (if applicable)
4. Update all affected tests
5. Document in CHANGELOG
6. Get explicit approval via PR review

---

## Bug Prevention Checklist

Before submitting any code:

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Code is formatted (ruff format)
- [ ] No linting errors (ruff check)
- [ ] Type hints are complete (mypy)
- [ ] Coverage is maintained
- [ ] Documentation updated
- [ ] Registry validated (if applicable)
- [ ] Build succeeds locally

---

## Quality Metrics

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Test Coverage | >=80% | Pre-push block |
| Type Coverage | 100% | MyPy strict |
| Lint Errors | 0 | Pre-commit block |
| Build Warnings | 0 | CI block |
| Security Issues | 0 | Automated scan |

---

## Emergency Override

In rare cases, you may need to bypass checks:

```bash
# Bypass pre-commit (NOT RECOMMENDED)
git commit --no-verify -m "message"

# Bypass pre-push (NOT RECOMMENDED)
git push --no-verify
```

**WARNING**: Bypassing checks will result in immediate CI failure and should only be done in exceptional circumstances with team approval.

---

## Continuous Improvement

This quality system evolves. To suggest improvements:

1. Open an issue with proposal
2. Discuss with team
3. Implement via PR
4. Update this document

These checks exist to help you write better code, not to slow you down. Catch issues early, fix them quickly, and ship with confidence.
