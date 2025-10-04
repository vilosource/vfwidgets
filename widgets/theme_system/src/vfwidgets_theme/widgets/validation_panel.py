"""Validation Panel Widget - Theme Editor Component.

This module provides the ValidationPanel for displaying accessibility validation results.

Phase 4: Validation & Accessibility
"""

import re
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..core.theme import HEX_COLOR_PATTERN, RGB_COLOR_PATTERN, RGBA_COLOR_PATTERN
from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class ValidationPanel(ThemedWidget, QWidget):
    """Accessibility validation panel for theme editor.

    Features:
    - WCAG AA/AAA compliance badges
    - Contrast ratio calculations
    - Validation error/warning list
    - Auto-fix suggestions (clickable)
    - "Show Me" feature to highlight problematic tokens

    Signals:
        fix_requested(str, str): Emitted when user clicks fix (token_path, suggested_value)
        token_highlight_requested(str): Emitted to highlight token in browser
    """

    # Signals
    fix_requested = Signal(str, str)  # token_path, suggested_value
    token_highlight_requested = Signal(str)  # token_path

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize validation panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Validation state
        self._current_issues: List[Dict] = []
        self._wcag_aa_pass: bool = True
        self._wcag_aaa_pass: bool = True

        # Setup UI
        self._setup_ui()

        logger.debug("ValidationPanel initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with WCAG badges
        header_layout = QHBoxLayout()

        header_label = QLabel("Accessibility Validation")
        header_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # WCAG AA badge
        self._aa_badge = QLabel("AA")
        self._aa_badge.setFixedSize(30, 20)
        self._aa_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_badge(self._aa_badge, True)
        header_layout.addWidget(self._aa_badge)

        # WCAG AAA badge
        self._aaa_badge = QLabel("AAA")
        self._aaa_badge.setFixedSize(35, 20)
        self._aaa_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_badge(self._aaa_badge, True)
        header_layout.addWidget(self._aaa_badge)

        layout.addLayout(header_layout)

        # Issues list
        self._issues_list = QListWidget()
        self._issues_list.itemClicked.connect(self._on_issue_clicked)
        layout.addWidget(self._issues_list)

        # Summary label
        self._summary_label = QLabel("No issues found ✓")
        self._summary_label.setStyleSheet("color: #4caf50; padding: 5px;")
        layout.addWidget(self._summary_label)

    def _update_badge(self, badge: QLabel, passes: bool) -> None:
        """Update WCAG badge appearance.

        Args:
            badge: Badge label widget
            passes: Whether compliance check passes
        """
        if passes:
            badge.setStyleSheet(
                "background-color: #4caf50; color: white; "
                "font-weight: bold; border-radius: 3px;"
            )
        else:
            badge.setStyleSheet(
                "background-color: #f44336; color: white; "
                "font-weight: bold; border-radius: 3px;"
            )

    def validate_theme(self, theme_colors: Dict[str, str]) -> None:
        """Validate theme colors for accessibility.

        Args:
            theme_colors: Dict of token_path -> color_value
        """
        self._current_issues = []
        errors = 0
        warnings = 0

        # Check contrast ratios for common token pairs
        contrast_pairs = [
            ("colors.foreground", "colors.background", "Normal text", 4.5, 7.0),
            ("button.foreground", "button.background", "Button text", 4.5, 7.0),
            ("input.foreground", "input.background", "Input text", 4.5, 7.0),
            ("list.foreground", "list.background", "List text", 4.5, 7.0),
        ]

        for fg_token, bg_token, description, aa_ratio, aaa_ratio in contrast_pairs:
            if fg_token in theme_colors and bg_token in theme_colors:
                fg_color = self._parse_color(theme_colors[fg_token])
                bg_color = self._parse_color(theme_colors[bg_token])

                if fg_color and bg_color:
                    ratio = self._calculate_contrast_ratio(fg_color, bg_color)

                    # Check AA compliance
                    if ratio < aa_ratio:
                        self._current_issues.append({
                            "level": "error",
                            "description": f"{description}: Contrast ratio {ratio:.2f}:1 (needs {aa_ratio}:1 for AA)",
                            "tokens": [fg_token, bg_token],
                            "ratio": ratio,
                            "required_aa": aa_ratio,
                            "required_aaa": aaa_ratio,
                        })
                        errors += 1
                        self._wcag_aa_pass = False

                    # Check AAA compliance
                    elif ratio < aaa_ratio:
                        self._current_issues.append({
                            "level": "warning",
                            "description": f"{description}: Contrast ratio {ratio:.2f}:1 (needs {aaa_ratio}:1 for AAA)",
                            "tokens": [fg_token, bg_token],
                            "ratio": ratio,
                            "required_aa": aa_ratio,
                            "required_aaa": aaa_ratio,
                        })
                        warnings += 1
                        self._wcag_aaa_pass = False

        # Update UI
        self._update_issues_list()
        self._update_badges()
        self._update_summary(errors, warnings)

        logger.info(f"Validation complete: {errors} errors, {warnings} warnings")

    def _parse_color(self, color_str: str) -> Optional[QColor]:
        """Parse color string to QColor.

        Args:
            color_str: Color string (hex, rgb, rgba)

        Returns:
            QColor if valid, None otherwise
        """
        if not color_str:
            return None

        # Hex format
        if HEX_COLOR_PATTERN.match(color_str):
            return QColor(color_str)

        # RGB format
        rgb_match = RGB_COLOR_PATTERN.match(color_str)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return QColor(r, g, b)

        # RGBA format
        rgba_match = RGBA_COLOR_PATTERN.match(color_str)
        if rgba_match:
            r, g, b = map(int, rgba_match.groups()[:3])
            return QColor(r, g, b)

        return None

    def _calculate_contrast_ratio(self, color1: QColor, color2: QColor) -> float:
        """Calculate WCAG contrast ratio between two colors.

        Args:
            color1: First color
            color2: Second color

        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        # Calculate relative luminance
        def luminance(color: QColor) -> float:
            r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0

            # Apply gamma correction
            def gamma(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            r, g, b = gamma(r), gamma(g), gamma(b)

            # Calculate luminance
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = luminance(color1)
        l2 = luminance(color2)

        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1

        # Calculate contrast ratio
        return (l1 + 0.05) / (l2 + 0.05)

    def _update_issues_list(self) -> None:
        """Update issues list widget."""
        self._issues_list.clear()

        for issue in self._current_issues:
            item = QListWidgetItem()

            # Create issue text
            icon = "❌" if issue["level"] == "error" else "⚠️"
            text = f"{icon} {issue['description']}"

            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, issue)

            # Color by level
            if issue["level"] == "error":
                item.setForeground(QColor("#f44336"))
            else:
                item.setForeground(QColor("#ff9800"))

            self._issues_list.addItem(item)

    def _update_badges(self) -> None:
        """Update WCAG compliance badges."""
        self._update_badge(self._aa_badge, self._wcag_aa_pass)
        self._update_badge(self._aaa_badge, self._wcag_aaa_pass)

    def _update_summary(self, errors: int, warnings: int) -> None:
        """Update summary label.

        Args:
            errors: Number of errors
            warnings: Number of warnings
        """
        if errors > 0:
            self._summary_label.setText(f"{errors} error(s), {warnings} warning(s)")
            self._summary_label.setStyleSheet("color: #f44336; padding: 5px;")
        elif warnings > 0:
            self._summary_label.setText(f"{warnings} warning(s)")
            self._summary_label.setStyleSheet("color: #ff9800; padding: 5px;")
        else:
            self._summary_label.setText("No issues found ✓")
            self._summary_label.setStyleSheet("color: #4caf50; padding: 5px;")

    def _on_issue_clicked(self, item: QListWidgetItem) -> None:
        """Handle issue click (show tokens involved).

        Args:
            item: Clicked list item
        """
        issue = item.data(Qt.ItemDataRole.UserRole)
        if issue and "tokens" in issue:
            # Highlight first token
            if issue["tokens"]:
                self.token_highlight_requested.emit(issue["tokens"][0])
                logger.debug(f"Highlighting token: {issue['tokens'][0]}")

    def clear(self) -> None:
        """Clear validation results."""
        self._current_issues = []
        self._wcag_aa_pass = True
        self._wcag_aaa_pass = True
        self._issues_list.clear()
        self._update_badges()
        self._summary_label.setText("No validation performed")
        self._summary_label.setStyleSheet("color: #888; padding: 5px;")

    def get_issues_count(self) -> Tuple[int, int]:
        """Get count of errors and warnings.

        Returns:
            Tuple of (errors, warnings)
        """
        errors = sum(1 for issue in self._current_issues if issue["level"] == "error")
        warnings = sum(1 for issue in self._current_issues if issue["level"] == "warning")
        return errors, warnings
