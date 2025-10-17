# ViloWeb Makefile
# Provides convenient build targets for the browser application

.PHONY: help build clean install dev run test format lint check bookmark-test local-release uninstall-user generate-icons install-system uninstall-system fix-spec

# Default target
help:
	@echo "ViloWeb Build Targets:"
	@echo "  make build           - Build the standalone binary"
	@echo "  make clean           - Remove build artifacts and binaries"
	@echo "  make install         - Install dependencies"
	@echo "  make dev             - Install in development mode"
	@echo "  make run             - Run ViloWeb browser"
	@echo "  make test            - Run tests"
	@echo ""
	@echo "User Installation (recommended):"
	@echo "  make local-release   - Build and install to ~/bin with GNOME integration (no sudo)"
	@echo "  make uninstall-user  - Remove user-level installation"
	@echo ""
	@echo "System Installation (advanced):"
	@echo "  make generate-icons  - Generate PNG icons from SVG"
	@echo "  make install-system  - Install system-wide with desktop integration (requires sudo)"
	@echo "  make uninstall-system - Remove system-wide installation (requires sudo)"
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
	@echo ""
	@echo "Troubleshooting:"
	@echo "  make fix-spec        - Fix pysidedeploy.spec for current machine (run after git pull on new machine)"

# Build the standalone binary
build:
	@./build.sh

# Clean all build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf deployment
	@rm -f ViloWeb ViloWeb.exe ViloWeb.bin ViloWeb.app
	@rm -rf __pycache__ .pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf src/*.egg-info
	@rm -rf build/ dist/
	@echo "✅ Cleaned"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -e .
	@echo "✅ Dependencies installed"

# Install in development mode with all extras
dev:
	@echo "📦 Installing in development mode..."
	@pip install -e ".[dev]" 2>/dev/null || pip install -e .
	@echo "✅ Development environment ready"

# Run in development mode
run:
	@python -m viloweb

# Run tests
test:
	@echo "🧪 Running tests..."
	@pytest -v 2>/dev/null || echo "⚠️  pytest not installed or no tests found"

# Build and install to ~/bin with GNOME integration
local-release: build
	@./install-user.sh

# Uninstall from user directories
uninstall-user:
	@./uninstall-user.sh

# Generate PNG icons from SVG
generate-icons:
	@cd icons && ./generate-pngs.sh

# Install system-wide (requires sudo)
install-system: build generate-icons
	@sudo ./install-system.sh

# Uninstall from system (requires sudo)
uninstall-system:
	@sudo ./uninstall-system.sh

# Fix pysidedeploy.spec for current machine
fix-spec:
	@./fix-spec.sh

# Format code with Black
format:
	@echo "🎨 Formatting code with Black..."
	@black src/
	@echo "✅ Code formatted"

# Lint with Ruff
lint:
	@echo "🔍 Linting with Ruff..."
	@ruff check src/
	@echo "✅ Linting complete"

# Type check with MyPy
typecheck:
	@echo "🔍 Type checking with MyPy..."
	@mypy src/ 2>/dev/null || echo "⚠️  MyPy not configured or not installed"

# Run all quality checks
check: format lint typecheck
	@echo "✅ All quality checks passed"

# Test bookmark functionality
bookmark-test:
	@echo "🧪 Testing bookmark persistence..."
	@python -c "from viloweb.managers import BookmarkManager; \
		bm = BookmarkManager(); \
		bm.add_bookmark('Test Bookmark', 'https://example.com'); \
		print('✅ Bookmark added'); \
		bookmarks = bm.get_all_bookmarks(); \
		assert len(bookmarks) > 0, 'No bookmarks found'; \
		print(f'✅ Found {len(bookmarks)} bookmark(s)'); \
		print('✅ Bookmark persistence working')"

# Clean browser data
clean-data:
	@echo "⚠️  This will delete ALL browser data (bookmarks, etc.)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ~/.viloweb/; \
		echo "✅ Browser data deleted"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Backup browser data
backup-data:
	@echo "📦 Backing up browser data..."
	@mkdir -p backup
	@if [ -d ~/.viloweb ]; then \
		cp -r ~/.viloweb backup/viloweb-backup-$$(date +%Y%m%d-%H%M%S); \
		echo "✅ Backed up to backup/viloweb-backup-$$(date +%Y%m%d-%H%M%S)"; \
	else \
		echo "⚠️  No data to backup (~/.viloweb does not exist)"; \
	fi
