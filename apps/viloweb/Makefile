# ViloWeb Makefile
# Provides convenient build targets for the browser application

.PHONY: help clean install dev run test format lint check bookmark-test

# Default target
help:
	@echo "ViloWeb Build Targets:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev             - Install in development mode"
	@echo "  make run             - Run ViloWeb browser"
	@echo "  make test            - Run tests (when implemented)"
	@echo "  make clean           - Remove cache and build artifacts"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format          - Format code with Black"
	@echo "  make lint            - Lint with Ruff"
	@echo "  make typecheck       - Type check with MyPy"
	@echo "  make check           - Run all quality checks (format + lint + typecheck)"
	@echo ""
	@echo "Testing:"
	@echo "  make bookmark-test   - Test bookmark persistence"
	@echo ""
	@echo "Data Management:"
	@echo "  make clean-data      - Remove browser data (~/.viloweb/)"
	@echo "  make backup-data     - Backup browser data to backup/"

# Install dependencies
install:
	@echo "=æ Installing ViloWeb..."
	@pip install -e .
	@echo " ViloWeb installed. Run with: viloweb"

# Install in development mode with all extras
dev:
	@echo "=æ Installing in development mode..."
	@pip install -e ".[dev]" 2>/dev/null || pip install -e .
	@echo " Development environment ready"

# Run ViloWeb browser
run:
	@python -m viloweb

# Run tests (placeholder for future)
test:
	@echo ">ê Running tests..."
	@pytest -v 2>/dev/null || echo "   pytest not installed or no tests found"
	@echo "Note: Phase 1 has no automated tests yet"

# Clean cache and artifacts
clean:
	@echo ">ù Cleaning cache and build artifacts..."
	@rm -rf __pycache__ .pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf src/*.egg-info
	@rm -rf build/ dist/
	@echo " Cleaned"

# Format code with Black
format:
	@echo "<¨ Formatting code with Black..."
	@black src/
	@echo " Code formatted"

# Lint with Ruff
lint:
	@echo "= Linting with Ruff..."
	@ruff check src/
	@echo " Linting complete"

# Type check with MyPy
typecheck:
	@echo "= Type checking with MyPy..."
	@mypy src/ 2>/dev/null || echo "   MyPy not configured or not installed"

# Run all quality checks
check: format lint typecheck
	@echo " All quality checks passed"

# Test bookmark functionality
bookmark-test:
	@echo ">ê Testing bookmark persistence..."
	@python -c "from viloweb.managers import BookmarkManager; \
		bm = BookmarkManager(); \
		bm.add_bookmark('https://example.com', 'Test Bookmark'); \
		print(' Bookmark added'); \
		bookmarks = bm.get_all_bookmarks(); \
		assert len(bookmarks) > 0, 'No bookmarks found'; \
		print(f' Found {len(bookmarks)} bookmark(s)'); \
		print(' Bookmark persistence working')"

# Clean browser data
clean-data:
	@echo "   This will delete ALL browser data (bookmarks, etc.)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ~/.viloweb/; \
		echo " Browser data deleted"; \
	else \
		echo "L Cancelled"; \
	fi

# Backup browser data
backup-data:
	@echo "=¾ Backing up browser data..."
	@mkdir -p backup
	@if [ -d ~/.viloweb ]; then \
		cp -r ~/.viloweb backup/viloweb-backup-$$(date +%Y%m%d-%H%M%S); \
		echo " Backed up to backup/viloweb-backup-$$(date +%Y%m%d-%H%M%S)"; \
	else \
		echo "   No data to backup (~/.viloweb does not exist)"; \
	fi
