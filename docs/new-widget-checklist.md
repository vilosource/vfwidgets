# New Widget Creation Checklist

Quick reference for creating new widgets in the VFWidgets monorepo.

## ⚠️ IMPORTANT: Monorepo Rules

- **DO NOT** create `.gitignore` in widget directories (use root monorepo `.gitignore`)
- **DO NOT** create `.github/` folders in widgets (use root monorepo workflows)
- **DO NOT** duplicate root-level tooling configs (ruff, black, mypy use root config)
- **DO** create widget-specific `pyproject.toml`, `requirements.txt`, `LICENSE`

## Directory Structure Template

```
vfwidgets/widgets/YOUR_WIDGET_NAME/
├── docs/                           # Widget-specific documentation
│   ├── YOUR_WIDGET-SPECIFICATION.md
│   ├── api.md
│   └── usage.md
├── src/
│   └── YOUR_PACKAGE_NAME/         # Python package (use underscores)
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── unit/
│   ├── integration/
│   └── __init__.py
├── examples/
│   ├── 01_basic_usage.py
│   └── run_examples.py
├── benchmarks/                     # Optional
├── pyproject.toml                 # Widget-specific package config
├── requirements.txt                # Runtime dependencies only
├── requirements-dev.txt           # Development dependencies
├── README.md                       # Widget documentation
├── LICENSE                         # Widget license (typically MIT)
└── CHANGELOG.md                   # Widget version history
```

## Required Files Checklist

### ✅ Must Have
- [ ] `pyproject.toml` - Package metadata and build config
- [ ] `requirements.txt` - Runtime dependencies (usually just `PySide6>=6.x.x`)
- [ ] `requirements-dev.txt` - Dev dependencies (include `-r requirements.txt`)
- [ ] `README.md` - User-facing documentation
- [ ] `LICENSE` - License file (copy from another widget)
- [ ] `src/PACKAGE_NAME/__init__.py` - Package initialization

### ✅ Should Have
- [ ] `CHANGELOG.md` - Version history
- [ ] `docs/WIDGET-SPECIFICATION.md` - Requirements specification
- [ ] `examples/01_basic_usage.py` - Basic example
- [ ] `tests/__init__.py` - Test package marker

### ❌ Must NOT Have
- [ ] `.gitignore` - Uses root monorepo file
- [ ] `.github/` - Uses root monorepo workflows
- [ ] `.vscode/`, `.idea/` - Personal IDE configs
- [ ] `setup.py` - Use modern pyproject.toml instead
- [ ] `.git/` - Part of monorepo, not separate

## Quick Start Commands

```bash
# 1. Navigate to widgets directory
cd ~/GitHub/vfwidgets/widgets

# 2. Create widget directory
mkdir -p YOUR_WIDGET_NAME/{docs,src/YOUR_PACKAGE_NAME,tests/{unit,integration},examples}

# 3. Navigate to widget
cd YOUR_WIDGET_NAME

# 4. Copy template files from existing widget
cp ../button_widget/{pyproject.toml,requirements.txt,requirements-dev.txt,LICENSE,README.md} .

# 5. Edit pyproject.toml to update:
#    - name: "your-widget-name"
#    - description
#    - package paths

# 6. Create initial package file
echo '"""Your widget package."""

__version__ = "0.1.0"
' > src/YOUR_PACKAGE_NAME/__init__.py
```

## pyproject.toml Template

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-widget-name"
version = "0.1.0"
description = "Brief widget description"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
dependencies = [
    "PySide6>=6.5.0",
]

[tool.setuptools.packages.find]
where = ["src"]
include = ["your_package_name*"]
```

## Common Mistakes to Avoid

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|------------------|
| Creating `.gitignore` | Monorepo uses root `.gitignore` | Use root file |
| Hardcoding paths | Breaks in different environments | Use relative imports |
| Missing `__init__.py` | Package won't be importable | Create even if empty |
| Wrong package name | Hyphens in package names | Use underscores for packages |
| Duplicate tool configs | Inconsistent formatting | Use root configs |

## Testing Your Widget

```bash
# From widget directory
pip install -e .                    # Install in development mode
pytest tests/                       # Run tests
python examples/01_basic_usage.py   # Test example

# From monorepo root
pytest widgets/YOUR_WIDGET_NAME/    # Run widget tests
ruff check widgets/YOUR_WIDGET_NAME # Check linting
```

## Integration with Root Monorepo

The root monorepo provides:
- `.gitignore` - Covers all common Python/Qt ignores
- `pyproject.toml` - Shared tool configs (ruff, black, mypy)
- `.github/workflows/` - CI/CD pipelines
- `Makefile` - Common development tasks

Your widget uses these automatically - don't duplicate!

## Final Checklist Before Commit

- [ ] Widget follows naming convention: `lowercase_with_underscores`
- [ ] Package is importable: `from your_package_name import YourWidget`
- [ ] No `.gitignore` or `.github/` in widget directory
- [ ] `pyproject.toml` has correct package name and paths
- [ ] At least one working example in `examples/`
- [ ] README has basic usage example
- [ ] No absolute paths in code

---

*Remember: This is a monorepo - leverage shared infrastructure, don't duplicate it!*