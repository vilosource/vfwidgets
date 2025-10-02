#!/usr/bin/env python3
"""
Phase 2 Features Demo
=====================

Demonstrates all 4 Phase 2 Developer Experience features:
1. Theme Inheritance (extend)
2. Theme Composition (compose)
3. Accessibility Validation (WCAG)
4. Enhanced Error Messages
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vfwidgets_theme.core.theme import ThemeBuilder, ThemeComposer, ThemeValidator


def demo_feature_1_inheritance():
    """Demonstrate theme inheritance."""
    print("\n" + "="*70)
    print("FEATURE 1: THEME INHERITANCE")
    print("="*70)

    # Create a base dark theme
    base_dark = (ThemeBuilder("my-dark")
        .set_type("dark")
        .add_color("colors.background", "#1e1e1e")
        .add_color("colors.foreground", "#d4d4d4")
        .add_color("button.background", "#0e639c")
        .add_color("button.foreground", "#ffffff")
        .build())

    print("\n1. Created base dark theme with 4 colors")
    print(f"   - colors.background: {base_dark.colors['colors.background']}")
    print(f"   - button.background: {base_dark.colors['button.background']}")

    # Create variant that extends base theme
    red_variant = (ThemeBuilder("dark-red-variant")
        .extend(base_dark)
        .add_color("button.background", "#cc0000")  # Override
        .add_color("button.hoverBackground", "#ff0000")  # Add new
        .build())

    print("\n2. Created variant extending base theme:")
    print(f"   - Inherited colors.background: {red_variant.colors['colors.background']}")
    print(f"   - Overridden button.background: {red_variant.colors['button.background']}")
    print(f"   - Added button.hoverBackground: {red_variant.colors['button.hoverBackground']}")
    print(f"   - Parent tracked in metadata: {red_variant.metadata.get('parent_theme')}")

    print("\n✅ Theme inheritance allows DRY theme variants!")


def demo_feature_2_composition():
    """Demonstrate theme composition."""
    print("\n" + "="*70)
    print("FEATURE 2: THEME COMPOSITION")
    print("="*70)

    # Create component themes
    base = (ThemeBuilder("base")
        .add_color("colors.background", "#1e1e1e")
        .add_color("colors.foreground", "#d4d4d4")
        .build())

    buttons = (ThemeBuilder("button-theme")
        .add_color("button.background", "#0e639c")
        .add_color("button.foreground", "#ffffff")
        .add_color("button.hoverBackground", "#1177bb")
        .build())

    inputs = (ThemeBuilder("input-theme")
        .add_color("input.background", "#3c3c3c")
        .add_color("input.foreground", "#cccccc")
        .add_color("input.border", "#3c3c3c")
        .build())

    print("\n1. Created 3 component themes:")
    print(f"   - base: {len(base.colors)} colors")
    print(f"   - buttons: {len(buttons.colors)} colors")
    print(f"   - inputs: {len(inputs.colors)} colors")

    # Compose themes
    composer = ThemeComposer()
    app_theme = composer.compose(base, buttons, inputs, name="my-app")

    print("\n2. Composed into single theme:")
    print(f"   - Total colors: {len(app_theme.colors)}")
    print(f"   - From base: {app_theme.colors['colors.background']}")
    print(f"   - From buttons: {app_theme.colors['button.background']}")
    print(f"   - From inputs: {app_theme.colors['input.background']}")
    print(f"   - Composition tracked: {app_theme.metadata.get('composed_from')}")

    # Quick partial override
    variant = composer.compose_partial(app_theme, {
        "button.background": "#ff0000",
        "button.hoverBackground": "#cc0000"
    })

    print("\n3. Created quick variant with compose_partial:")
    print(f"   - Overridden button.background: {variant.colors['button.background']}")
    print(f"   - Kept other properties: {variant.colors['input.background']}")

    print("\n✅ Theme composition enables modular theme design!")


def demo_feature_3_accessibility():
    """Demonstrate accessibility validation."""
    print("\n" + "="*70)
    print("FEATURE 3: ACCESSIBILITY VALIDATION")
    print("="*70)

    # Good contrast theme
    good_theme = (ThemeBuilder("good-contrast")
        .add_color("colors.background", "#ffffff")
        .add_color("colors.foreground", "#000000")
        .add_color("button.background", "#0066cc")
        .add_color("button.foreground", "#ffffff")
        .build())

    validator = ThemeValidator()
    result_good = validator.validate_accessibility(good_theme)

    print("\n1. Validating theme with GOOD contrast:")
    print(f"   - Is valid: {result_good.is_valid}")
    print(f"   - Errors: {len(result_good.errors)}")
    print(f"   - Warnings: {len(result_good.warnings)}")

    # Calculate specific contrast ratio
    ratio = validator._calculate_contrast_ratio("#ffffff", "#000000")
    print(f"   - White/Black ratio: {ratio:.2f}:1 (max ~21:1)")

    # Poor contrast theme
    poor_theme = (ThemeBuilder("poor-contrast")
        .add_color("colors.background", "#ffffff")
        .add_color("colors.foreground", "#f0f0f0")  # Very low contrast!
        .add_color("button.background", "#f8f8f8")
        .add_color("button.foreground", "#eeeeee")
        .build())

    result_poor = validator.validate_accessibility(poor_theme)

    print("\n2. Validating theme with POOR contrast:")
    print(f"   - Is valid: {result_poor.is_valid}")
    print(f"   - Errors: {len(result_poor.errors)}")
    print(f"   - Warnings: {len(result_poor.warnings)}")

    if result_poor.warnings:
        print("\n   Warnings:")
        for warning in result_poor.warnings[:2]:  # Show first 2
            print(f"     - {warning}")

    if result_poor.suggestions:
        print("\n   Suggestions:")
        for suggestion in result_poor.suggestions[:2]:  # Show first 2
            print(f"     - {suggestion}")

    print("\n✅ Accessibility validation catches WCAG compliance issues!")


def demo_feature_4_error_messages():
    """Demonstrate enhanced error messages."""
    print("\n" + "="*70)
    print("FEATURE 4: ENHANCED ERROR MESSAGES")
    print("="*70)

    validator = ThemeValidator()

    # Typo in property name
    print("\n1. Error message for typo 'button.backgroud':")
    print("-" * 70)
    error_msg = validator.format_error("button.backgroud", "not_found")
    print(error_msg)

    # List available properties
    print("\n2. Available button properties:")
    button_props = validator.get_available_properties("button")
    print(f"   - Found {len(button_props)} button properties")
    print(f"   - First 5: {button_props[:5]}")

    # Another typo example
    print("\n3. Error message for typo 'input.forground':")
    print("-" * 70)
    error_msg2 = validator.format_error("input.forground", "not_found")
    print(error_msg2)

    print("\n✅ Enhanced error messages guide developers to correct usage!")


def main():
    """Run all feature demos."""
    print("\n" + "="*70)
    print("PHASE 2 FEATURES DEMO")
    print("VFWidgets Theme System - Developer Experience Enhancements")
    print("="*70)

    try:
        demo_feature_1_inheritance()
        demo_feature_2_composition()
        demo_feature_3_accessibility()
        demo_feature_4_error_messages()

        print("\n" + "="*70)
        print("ALL PHASE 2 FEATURES DEMONSTRATED SUCCESSFULLY!")
        print("="*70)
        print("\nPhase 2 makes theme customization 10x easier:")
        print("  1. Extend existing themes (DRY)")
        print("  2. Compose modular theme components")
        print("  3. Validate accessibility automatically")
        print("  4. Get helpful error messages")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
