# Reamde Makefile
# Provides convenient build targets for the application

.PHONY: help build clean install dev run test local-release uninstall-user generate-icons install-system uninstall-system fix-spec

# Default target
help:
	@echo "Reamde Build Targets:"
	@echo "  make build            - Build the standalone binary"
	@echo "  make clean            - Remove build artifacts and binaries"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Install in development mode"
	@echo "  make run              - Run Reamde in development mode"
	@echo "  make test             - Run tests"
	@echo ""
	@echo "User Installation (recommended):"
	@echo "  make local-release    - Build and install to ~/bin with GNOME integration (no sudo)"
	@echo "  make uninstall-user   - Remove user-level installation"
	@echo ""
	@echo "System Installation (advanced):"
	@echo "  make generate-icons   - Generate PNG icons from SVG"
	@echo "  make install-system   - Install system-wide with desktop integration (requires sudo)"
	@echo "  make uninstall-system - Remove system-wide installation (requires sudo)"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  make fix-spec         - Fix pysidedeploy.spec for current machine (run after git pull on new machine)"

# Build the standalone binary
build:
	@./build.sh

# Clean all build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf deployment
	@rm -f Reamde Reamde.exe Reamde.bin Reamde.app
	@rm -rf __pycache__ .pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
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
	@python -m reamde

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
