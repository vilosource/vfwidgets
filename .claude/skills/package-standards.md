---
name: package-standards
description: Ensure consistent package configuration, naming conventions, dependencies, and version management. Use when configuring pyproject.toml, managing dependencies, or bumping versions.
allowed-tools:
  - Read
  - Edit
---

# Package Standards Skill

When configuring widget packages, follow VFWidgets monorepo standards for consistency, compatibility, and best practices.

## Naming Conventions

VFWidgets uses a strict naming convention across all packages:

### Package Names

```
Python package:    vfwidgets_<name>        (underscores)
PyPI distribution: vfwidgets-<name>        (hyphens)
Widget directory:  <name>_widget           (underscores)
Import statement:  from vfwidgets_<name>   (underscores)
```

**Examples**:

| Widget Directory | Python Package | PyPI Name | Import |
|-----------------|----------------|-----------|--------|
| `button_widget` | `vfwidgets_button` | `vfwidgets-button` | `from vfwidgets_button import Button` |
| `theme_system` | `vfwidgets_theme` | `vfwidgets-theme` | `from vfwidgets_theme import ThemedWidget` |
| `chrome-tabbed-window` | `chrome_tabbed_window` | `chrome-tabbed-window` | `from chrome_tabbed_window import ChromeTabbedWindow` |

**Note**: `chrome-tabbed-window` is an exception for compatibility with the chrome-tabs naming pattern.

## pyproject.toml Structure

### Required Sections

Every widget must have:

1. **[build-system]** - Build configuration
2. **[project]** - Package metadata
3. **[project.optional-dependencies]** - Dev dependencies
4. **[project.urls]** - Project links
5. **[tool.setuptools.packages.find]** - Package discovery
6. **[tool.black]** - Code formatting config
7. **[tool.ruff]** - Linting config
8. **[tool.pytest.ini_options]** - Testing config

### Minimal Template

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vfwidgets-<name>"
version = "0.1.0"
description = "<Brief widget description>"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "VFWidgets Team"},
]
maintainers = [
    {name = "VFWidgets Team"},
]
keywords = [
    "qt",
    "pyside6",
    "widgets",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "PySide6>=6.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.0.0",
    "pytest-xvfb>=2.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/vilosource/vfwidgets"
Repository = "https://github.com/vilosource/vfwidgets/tree/main/widgets/<name>"
Issues = "https://github.com/vilosource/vfwidgets/issues"

[tool.setuptools.packages.find]
where = ["src"]
include = ["vfwidgets_<name>*"]

[tool.setuptools.package-data]
vfwidgets_<name> = ["py.typed"]

[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "N", "SIM"]
ignore = ["E501", "N802", "N803"]

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers", "--cov=vfwidgets_<name>"]
```

## Dependency Management

### Core Dependencies

**Minimum PySide6 version**:
- Use `PySide6>=6.5.0` for most widgets
- Use `PySide6>=6.9.0` if requiring newer Qt features

**Common dependencies**:
```toml
dependencies = [
    "PySide6>=6.5.0",
    "vfwidgets-common>=0.1.0",  # Base utilities
]
```

### Optional Dependencies

**Theme support**:
```toml
[project.optional-dependencies]
theme = ["vfwidgets-theme>=2.0.0"]
```

**Development tools**:
```toml
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.0.0",
    "pytest-xvfb>=2.0.0",  # Headless testing
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]
```

**Documentation**:
```toml
docs = [
    "sphinx>=6.0.0",
    "sphinx-rtd-theme>=1.2.0",
    "myst-parser>=1.0.0",
]
```

## Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/):

**Version format**: `MAJOR.MINOR.PATCH`

### When to Bump

**MAJOR** (1.0.0 → 2.0.0):
- Breaking API changes
- Incompatible changes
- Major architecture changes

**MINOR** (1.0.0 → 1.1.0):
- New features (backward compatible)
- New public API methods
- Deprecations (with warnings)

**PATCH** (1.0.0 → 1.0.1):
- Bug fixes
- Performance improvements
- Documentation updates
- Internal refactoring (no API changes)

### Development Status

Update classifier based on stability:

```toml
classifiers = [
    "Development Status :: 3 - Alpha",      # 0.x.x versions
    "Development Status :: 4 - Beta",       # Early 1.x.x
    "Development Status :: 5 - Production/Stable",  # Mature 1.x.x+
]
```

**Guideline**:
- `0.x.x` = Alpha (breaking changes allowed)
- `1.0.0-1.9.9` = Beta (API stabilizing)
- `2.0.0+` = Stable (strict semver)

## Tool Configuration Standards

### Black (Code Formatting)

**Line length**: 100 characters (monorepo standard)

```toml
[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312"]
include = '\\.pyi?$'
```

### Ruff (Linting)

**Standard ruleset**:

```toml
[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by black)
    "N802",  # Qt event handlers use mixedCase (mousePressEvent, etc.)
    "N803",  # Qt method parameters use mixedCase (for QTabWidget compatibility)
]
```

**Qt-specific ignores**:
- `N802`: Allow `mixedCase` for Qt event handlers (`paintEvent`, `mousePressEvent`)
- `N803`: Allow `mixedCase` for Qt method parameters
- `N815`: Allow `mixedCase` for Qt signals/properties

### MyPy (Type Checking)

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
no_implicit_optional = true
check_untyped_defs = true

[[tool.mypy.overrides]]
module = "PySide6.*"
ignore_missing_imports = true
```

### Pytest (Testing)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=vfwidgets_<name>",
    "--cov-branch",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]

[tool.coverage.run]
branch = true
source = ["vfwidgets_<name>"]
```

## Python Version Support

**Minimum**: Python 3.8

**Tested versions**: 3.8, 3.9, 3.10, 3.11, 3.12

```toml
requires-python = ">=3.8"

classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

**Compatibility considerations**:
- Use `typing-extensions>=4.0.0` for Python 3.8 compatibility
- Avoid Python 3.10+ syntax (match/case, pipe union types)
- Test with oldest supported version (3.8)

## Package Discovery Configuration

Use `src/` layout for package structure:

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["vfwidgets_<name>*"]
```

**Directory structure**:
```
widgets/<name>/
├── src/
│   └── vfwidgets_<name>/
│       ├── __init__.py
│       └── ...
└── pyproject.toml
```

## Type Checking Marker

Include `py.typed` marker for type checkers:

```toml
[tool.setuptools.package-data]
vfwidgets_<name> = ["py.typed"]
```

Create empty `src/vfwidgets_<name>/py.typed` file.

## Version Bumping Process

### 1. Update Version in pyproject.toml

```toml
[project]
version = "1.2.3"  # Update this
```

### 2. Update __init__.py

```python
"""Package with version."""

__version__ = "1.2.3"  # Match pyproject.toml
```

### 3. Update CHANGELOG.md

```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature X

### Fixed
- Bug in component Y
```

### 4. Commit with Version Tag

```bash
git add pyproject.toml src/<package>/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"
git tag v1.2.3
git push && git push --tags
```

## Common Mistakes

### ❌ Mistake 1: Inconsistent Package Names

**Wrong**:
```toml
name = "my-widget"  # Hyphen
include = ["my_widget*"]  # Underscore
```

**Correct**:
```toml
name = "vfwidgets-my-widget"  # PyPI uses hyphens
include = ["vfwidgets_my_widget*"]  # Python uses underscores
```

### ❌ Mistake 2: Wrong Line Length

**Wrong**:
```toml
[tool.black]
line-length = 88  # Black default
```

**Correct**:
```toml
[tool.black]
line-length = 100  # VFWidgets standard
```

### ❌ Mistake 3: Missing py.typed

**Wrong**: No `py.typed` marker

**Correct**:
```toml
[tool.setuptools.package-data]
vfwidgets_<name> = ["py.typed"]
```

And create: `src/vfwidgets_<name>/py.typed` (empty file)

## Reference Examples

For pyproject.toml examples:

- **Minimal widget**: `widgets/button_widget/pyproject.toml`
- **Complex widget**: `widgets/multisplit_widget/pyproject.toml`
- **Mature widget**: `widgets/chrome-tabbed-window/pyproject.toml`
- **Theme system**: `widgets/theme_system/pyproject.toml`

## Package Standards Checklist

Before marking package configuration as complete:

- [ ] Package name follows `vfwidgets-<name>` convention (PyPI)
- [ ] Python package uses `vfwidgets_<name>` convention
- [ ] Version follows semantic versioning
- [ ] `requires-python = ">=3.8"`
- [ ] `PySide6>=6.5.0` (or 6.9.0+) in dependencies
- [ ] Black line-length = 100
- [ ] Ruff line-length = 100
- [ ] Qt naming rules ignored (N802, N803)
- [ ] `py.typed` marker included
- [ ] `pyproject.toml` has all required sections
- [ ] Development dependencies in `[project.optional-dependencies.dev]`
- [ ] Version in `pyproject.toml` matches `__init__.py`
- [ ] CHANGELOG.md updated with version changes
