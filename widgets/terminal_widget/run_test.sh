#!/bin/bash
# Quick test script for terminal widget

set -e

echo "========================================="
echo "VFWidgets Terminal - Test Runner"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Not in terminal_widget directory${NC}"
    echo "Please run from widgets/terminal_widget/"
    exit 1
fi

# Parse arguments
TEST_TYPE=${1:-basic}

# Function to install dependencies
install_deps() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -e . > /dev/null 2>&1
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Function to run unit tests
run_unit_tests() {
    echo -e "\n${YELLOW}Running unit tests...${NC}"
    if python -m pytest tests/ -v; then
        echo -e "${GREEN}✓ Unit tests passed${NC}"
    else
        echo -e "${RED}✗ Unit tests failed${NC}"
    fi
}

# Function to run interactive test
run_interactive_test() {
    echo -e "\n${YELLOW}Running interactive test with DEBUG logging...${NC}"
    echo "Starting terminal widget test window..."
    echo -e "${YELLOW}⚡ Right-click on the terminal to test context menu logging!${NC}"
    python test_terminal.py --mode $1 --debug
}

# Function to run examples
run_example() {
    echo -e "\n${YELLOW}Running example: $1${NC}"
    python examples/$1
}

# Main menu
case "$TEST_TYPE" in
    install)
        install_deps
        ;;
    unit)
        run_unit_tests
        ;;
    basic)
        run_interactive_test basic
        ;;
    python)
        run_interactive_test python
        ;;
    capture)
        run_interactive_test capture
        ;;
    example-basic)
        run_example basic_usage.py
        ;;
    example-advanced)
        run_example advanced_features.py
        ;;
    all)
        install_deps
        run_unit_tests
        echo -e "\n${YELLOW}Ready for interactive tests${NC}"
        echo "Run one of:"
        echo "  ./run_test.sh basic"
        echo "  ./run_test.sh python"
        echo "  ./run_test.sh capture"
        ;;
    *)
        echo "Usage: ./run_test.sh [command]"
        echo ""
        echo "Commands:"
        echo "  install          - Install dependencies"
        echo "  unit             - Run unit tests (pytest)"
        echo "  basic            - Run basic interactive test"
        echo "  python           - Run Python REPL test"
        echo "  capture          - Run output capture test"
        echo "  example-basic    - Run basic usage example"
        echo "  example-advanced - Run advanced features example"
        echo "  all              - Install deps and run unit tests"
        echo ""
        echo "Default: basic"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Done!${NC}"