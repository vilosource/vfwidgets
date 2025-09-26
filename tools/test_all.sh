#!/bin/bash
# Test all widgets in the repository

set -e

echo "========================================="
echo "Testing all VFWidgets"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
FAILED_WIDGETS=()
PASSED_WIDGETS=()
SKIPPED_WIDGETS=()

# Test shared utilities first if they exist
if [ -d "shared/vfwidgets_common" ]; then
    echo -e "${YELLOW}Testing shared utilities...${NC}"
    cd shared/vfwidgets_common

    if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then
        if pytest tests/; then
            echo -e "${GREEN}✓ Shared utilities tests passed${NC}"
        else
            echo -e "${RED}✗ Shared utilities tests failed${NC}"
            FAILED_WIDGETS+=("shared/vfwidgets_common")
        fi
    else
        echo -e "${YELLOW}⚠ No tests found for shared utilities${NC}"
        SKIPPED_WIDGETS+=("shared/vfwidgets_common")
    fi

    cd ../..
    echo
fi

# Test each widget
for widget_dir in widgets/*/; do
    if [ -f "${widget_dir}pyproject.toml" ]; then
        widget_name=$(basename "$widget_dir")
        echo -e "${YELLOW}Testing ${widget_name}...${NC}"

        cd "$widget_dir"

        # Check if tests directory exists and has test files
        if [ -d "tests" ] && [ -n "$(ls -A tests/test_*.py 2>/dev/null)" ]; then
            # Run pytest
            if pytest tests/ --tb=short; then
                echo -e "${GREEN}✓ ${widget_name} tests passed${NC}"
                PASSED_WIDGETS+=("$widget_name")
            else
                echo -e "${RED}✗ ${widget_name} tests failed${NC}"
                FAILED_WIDGETS+=("$widget_name")
            fi
        else
            echo -e "${YELLOW}⚠ No tests found for ${widget_name}${NC}"
            SKIPPED_WIDGETS+=("$widget_name")
        fi

        # Run linting
        echo "Running linting..."
        if ruff check src/ --quiet; then
            echo -e "${GREEN}✓ Linting passed${NC}"
        else
            echo -e "${RED}✗ Linting failed - run 'ruff check src/' for details${NC}"
            FAILED_WIDGETS+=("$widget_name (linting)")
        fi

        # Run formatting check
        echo "Checking formatting..."
        if black --check src/ --quiet; then
            echo -e "${GREEN}✓ Formatting check passed${NC}"
        else
            echo -e "${YELLOW}⚠ Formatting issues - run 'black src/' to fix${NC}"
        fi

        # Run type checking (allow failures)
        echo "Running type checking..."
        if mypy src/ --ignore-missing-imports 2>/dev/null; then
            echo -e "${GREEN}✓ Type checking passed${NC}"
        else
            echo -e "${YELLOW}⚠ Type checking has warnings${NC}"
        fi

        cd ../..
        echo
    fi
done

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="

if [ ${#PASSED_WIDGETS[@]} -gt 0 ]; then
    echo -e "${GREEN}Passed (${#PASSED_WIDGETS[@]}):${NC}"
    for widget in "${PASSED_WIDGETS[@]}"; do
        echo "  ✓ $widget"
    done
fi

if [ ${#SKIPPED_WIDGETS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Skipped (${#SKIPPED_WIDGETS[@]}):${NC}"
    for widget in "${SKIPPED_WIDGETS[@]}"; do
        echo "  ⚠ $widget"
    done
fi

if [ ${#FAILED_WIDGETS[@]} -gt 0 ]; then
    echo -e "${RED}Failed (${#FAILED_WIDGETS[@]}):${NC}"
    for widget in "${FAILED_WIDGETS[@]}"; do
        echo "  ✗ $widget"
    done
    echo
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi