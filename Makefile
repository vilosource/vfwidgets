# VFWidgets Monorepo Makefile

.PHONY: help install install-dev test test-all format lint type-check clean

help:
	@echo "VFWidgets Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install all widgets in normal mode"
	@echo "  make install-dev    Install all widgets with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests"
	@echo "  make test-widget W=button  Test specific widget"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        Format all code with black"
	@echo "  make lint          Run ruff linter"
	@echo "  make type-check    Run mypy type checking"
	@echo "  make quality       Run all quality checks"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         Clean up cache files"
	@echo "  make new-widget N=name  Create new widget"
	@echo ""

install:
	@echo "Installing all widgets..."
	@pip install -r requirements-dev.txt
	@for widget in widgets/*/; do \
		if [ -f "$$widget/pyproject.toml" ]; then \
			echo "Installing $$widget..."; \
			pip install -e "$$widget"; \
		fi \
	done
	@if [ -d "shared/vfwidgets_common" ]; then \
		echo "Installing shared utilities..."; \
		pip install -e shared/vfwidgets_common; \
	fi

install-dev:
	@echo "Installing with development dependencies..."
	@pip install -r requirements-dev.txt
	@for widget in widgets/*/; do \
		if [ -f "$$widget/requirements-dev.txt" ]; then \
			echo "Installing dev deps for $$widget..."; \
			pip install -r "$$widget/requirements-dev.txt"; \
		fi \
	done
	@if [ -f "shared/vfwidgets_common/requirements-dev.txt" ]; then \
		pip install -r shared/vfwidgets_common/requirements-dev.txt; \
	fi

test:
	@echo "Running all tests..."
	@python -m pytest widgets/*/tests/ -v

test-widget:
	@if [ -z "$(W)" ]; then \
		echo "Please specify widget with W=widget_name"; \
		exit 1; \
	fi
	@echo "Testing widget: $(W)"
	@python -m pytest widgets/$(W)_widget/tests/ -v

format:
	@echo "Formatting code..."
	@black widgets/*/src/ shared/*/src/ tools/ --line-length 100

lint:
	@echo "Running linter..."
	@ruff check widgets/*/src/ shared/*/src/ tools/

type-check:
	@echo "Running type checker..."
	@for widget in widgets/*/; do \
		if [ -d "$$widget/src" ]; then \
			echo "Type checking $$widget..."; \
			mypy "$$widget/src" --ignore-missing-imports || true; \
		fi \
	done

quality: format lint type-check
	@echo "All quality checks complete!"

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

new-widget:
	@if [ -z "$(N)" ]; then \
		echo "Please specify widget name with N=widget_name"; \
		exit 1; \
	fi
	@echo "Creating new widget: $(N)"
	@python tools/create_widget.py $(N) --author "$(AUTHOR)" --email "$(EMAIL)"

# Widget-specific test runners
test-terminal:
	@cd widgets/terminal_widget && ./run_test.sh basic

test-button:
	@cd widgets/button_widget && python examples/basic_usage.py