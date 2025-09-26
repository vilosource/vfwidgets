#!/bin/bash
# VFWidgets Setup Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================="
echo "VFWidgets Setup"
echo "========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.9+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Not in a virtual environment${NC}"
    echo "It's recommended to use a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install mode selection
echo "Select installation mode:"
echo "1) User mode - Install widgets for use"
echo "2) Developer mode - Install with all dev dependencies"
echo "3) Minimal - Install only core dependencies"
read -p "Choice (1-3): " INSTALL_MODE

case $INSTALL_MODE in
    1)
        echo -e "\n${YELLOW}Installing in user mode...${NC}"

        # Install global dev requirements (minimal for users)
        pip install -q PySide6>=6.9.0

        # Install each widget
        for widget in widgets/*/; do
            if [ -f "$widget/pyproject.toml" ]; then
                widget_name=$(basename "$widget")
                echo -e "Installing ${widget_name}..."
                pip install -q -e "$widget"
            fi
        done

        # Install shared utilities
        if [ -d "shared/vfwidgets_common" ]; then
            echo -e "Installing shared utilities..."
            pip install -q -e shared/vfwidgets_common
        fi
        ;;

    2)
        echo -e "\n${YELLOW}Installing in developer mode...${NC}"

        # Install global dev requirements
        echo "Installing development tools..."
        pip install -q -r requirements-dev.txt

        # Install each widget with dev dependencies
        for widget in widgets/*/; do
            if [ -f "$widget/requirements-dev.txt" ]; then
                widget_name=$(basename "$widget")
                echo -e "Installing ${widget_name} with dev dependencies..."
                pip install -q -r "$widget/requirements-dev.txt"
                pip install -q -e "$widget"
            fi
        done

        # Install shared utilities with dev deps
        if [ -f "shared/vfwidgets_common/requirements-dev.txt" ]; then
            echo -e "Installing shared utilities with dev dependencies..."
            pip install -q -r shared/vfwidgets_common/requirements-dev.txt
            pip install -q -e shared/vfwidgets_common
        fi

        # Set up pre-commit hooks (optional)
        if command -v pre-commit &> /dev/null; then
            echo "Setting up pre-commit hooks..."
            pre-commit install
        fi
        ;;

    3)
        echo -e "\n${YELLOW}Installing minimal dependencies...${NC}"
        pip install -q PySide6>=6.9.0
        echo -e "${GREEN}✓ Minimal installation complete${NC}"
        echo "You can manually install widgets as needed:"
        echo "  pip install -e widgets/button_widget"
        echo "  pip install -e widgets/terminal_widget"
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Test imports
echo "Testing installations..."
python3 -c "from vfwidgets_button import ButtonWidget; print('✓ Button widget')" 2>/dev/null || echo "⚠ Button widget not installed"
python3 -c "from vfwidgets_terminal import TerminalWidget; print('✓ Terminal widget')" 2>/dev/null || echo "⚠ Terminal widget not installed"

echo ""
echo "Next steps:"
echo "  • Run examples: python widgets/button_widget/examples/basic_usage.py"
echo "  • Run tests: make test"
echo "  • Create new widget: make new-widget N=mywidget"
echo ""

if [ "$INSTALL_MODE" == "2" ]; then
    echo "Developer commands:"
    echo "  • Format code: make format"
    echo "  • Run linter: make lint"
    echo "  • Type check: make type-check"
    echo "  • Run all checks: make quality"
    echo ""
fi