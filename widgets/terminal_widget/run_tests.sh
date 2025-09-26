#!/bin/bash
# Test runner script for VFWidgets Terminal Widget

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="fast"
HEADLESS=false
COVERAGE=false
VERBOSE=""

# Help function
show_help() {
    echo "Usage: ./run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -t, --type TYPE   Test type: fast, unit, integration, gui, slow, all (default: fast)"
    echo "  -H, --headless    Run tests in headless mode (no GUI windows)"
    echo "  -c, --coverage    Enable coverage reporting"
    echo "  -v, --verbose     Verbose output"
    echo "  -m, --marker M    Run tests with specific marker"
    echo ""
    echo "Test Types:"
    echo "  fast         - Quick unit tests only (default)"
    echo "  unit         - All unit tests"
    echo "  integration  - Integration tests"
    echo "  gui          - GUI tests (may show windows unless --headless)"
    echo "  slow         - Slow tests including real terminal"
    echo "  performance  - Performance benchmarks"
    echo "  all          - All tests"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh                    # Run fast tests"
    echo "  ./run_tests.sh -t unit -c         # Run unit tests with coverage"
    echo "  ./run_tests.sh -t slow --headless # Run slow tests without GUI"
    echo "  ./run_tests.sh -t all -H -c       # Run all tests headless with coverage"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -H|--headless)
            HEADLESS=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -m|--marker)
            MARKER="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add verbose flag
if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

# Add headless flag
if [ "$HEADLESS" = true ]; then
    echo -e "${BLUE}🖥️  Running in HEADLESS mode (no GUI windows)${NC}"

    # Use Xvfb for headless testing instead of offscreen platform
    # QWebEngineView requires a display to work properly
    if command -v Xvfb >/dev/null 2>&1; then
        echo -e "${BLUE}📺 Starting Xvfb virtual display...${NC}"
        export DISPLAY=:99
        Xvfb :99 -screen 0 1024x768x16 &
        XVFB_PID=$!
        sleep 1  # Give Xvfb time to start

        # Ensure Xvfb is killed on exit
        trap "kill $XVFB_PID 2>/dev/null || true" EXIT INT TERM
    else
        echo -e "${YELLOW}⚠️  Xvfb not found. Install with: sudo apt-get install xvfb${NC}"
        echo -e "${YELLOW}   Falling back to offscreen platform (may cause issues with WebEngine tests)${NC}"
        export QT_QPA_PLATFORM=offscreen
    fi

    PYTEST_CMD="$PYTEST_CMD --headless"
fi

# Add coverage flags
if [ "$COVERAGE" = true ]; then
    echo -e "${BLUE}📊 Coverage reporting enabled${NC}"
    PYTEST_CMD="$PYTEST_CMD --cov=src/vfwidgets_terminal --cov-report=term-missing --cov-report=html"
fi

# Add test selection based on type
case "$TEST_TYPE" in
    fast)
        echo -e "${GREEN}⚡ Running fast tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD -m 'unit and not slow'"
        ;;
    unit)
        echo -e "${GREEN}🧪 Running unit tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD -m unit"
        ;;
    integration)
        echo -e "${GREEN}🔗 Running integration tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD -m integration --integration"
        ;;
    gui)
        echo -e "${GREEN}🖼️  Running GUI tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD -m gui --gui"
        ;;
    slow)
        echo -e "${YELLOW}🐢 Running slow tests (this may take a while)...${NC}"
        if [ "$HEADLESS" = false ]; then
            echo -e "${YELLOW}⚠️  Warning: GUI windows may appear. Use --headless to prevent this.${NC}"
        fi
        PYTEST_CMD="$PYTEST_CMD --slow -m slow"
        ;;
    performance)
        echo -e "${GREEN}📈 Running performance tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD -m performance"
        ;;
    all)
        echo -e "${GREEN}🎯 Running all tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD --slow --integration --gui"
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        show_help
        exit 1
        ;;
esac

# Add custom marker if provided
if [ -n "$MARKER" ]; then
    echo -e "${BLUE}🏷️  Running tests with marker: $MARKER${NC}"
    PYTEST_CMD="$PYTEST_CMD -m $MARKER"
fi

# Show command being run
echo -e "${BLUE}Running: $PYTEST_CMD${NC}"
echo ""

# Run the tests
set +e
eval $PYTEST_CMD
TEST_RESULT=$?
set -e

# Report results
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"

    if [ "$COVERAGE" = true ]; then
        echo -e "${BLUE}📊 Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo -e "${RED}❌ Some tests failed!${NC}"
fi

exit $TEST_RESULT