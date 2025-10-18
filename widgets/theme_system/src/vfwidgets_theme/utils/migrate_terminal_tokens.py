"""Theme Migration Utility for Terminal Token Namespace Standardization.

This utility migrates theme files from the old terminal.* format to the new
terminal.colors.* format.

Usage:
    python -m vfwidgets_theme.utils.migrate_terminal_tokens <theme_file>
    python -m vfwidgets_theme.utils.migrate_terminal_tokens <theme_directory>
"""

import json
import sys
from pathlib import Path
from typing import Any

# Token migration mapping: old format -> new format
TOKEN_MIGRATION_MAP = {
    "terminal.background": "terminal.colors.background",
    "terminal.foreground": "terminal.colors.foreground",
    "terminal.ansiBlack": "terminal.colors.ansiBlack",
    "terminal.ansiRed": "terminal.colors.ansiRed",
    "terminal.ansiGreen": "terminal.colors.ansiGreen",
    "terminal.ansiYellow": "terminal.colors.ansiYellow",
    "terminal.ansiBlue": "terminal.colors.ansiBlue",
    "terminal.ansiMagenta": "terminal.colors.ansiMagenta",
    "terminal.ansiCyan": "terminal.colors.ansiCyan",
    "terminal.ansiWhite": "terminal.colors.ansiWhite",
    "terminal.ansiBrightBlack": "terminal.colors.ansiBrightBlack",
    "terminal.ansiBrightRed": "terminal.colors.ansiBrightRed",
    "terminal.ansiBrightGreen": "terminal.colors.ansiBrightGreen",
    "terminal.ansiBrightYellow": "terminal.colors.ansiBrightYellow",
    "terminal.ansiBrightBlue": "terminal.colors.ansiBrightBlue",
    "terminal.ansiBrightMagenta": "terminal.colors.ansiBrightMagenta",
    "terminal.ansiBrightCyan": "terminal.colors.ansiBrightCyan",
    "terminal.ansiBrightWhite": "terminal.colors.ansiBrightWhite",
}


def migrate_theme_dict(theme_data: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Migrate theme dictionary to new terminal token format.

    Args:
        theme_data: Theme dictionary to migrate

    Returns:
        Tuple of (migrated_theme_data, migration_count)

    """
    migration_count = 0

    if "colors" not in theme_data:
        return theme_data, migration_count

    colors = theme_data["colors"]
    migrated_colors = {}

    for key, value in colors.items():
        if key in TOKEN_MIGRATION_MAP:
            new_key = TOKEN_MIGRATION_MAP[key]
            migrated_colors[new_key] = value
            migration_count += 1
            print(f"  Migrated: {key} -> {new_key}")
        else:
            migrated_colors[key] = value

    theme_data["colors"] = migrated_colors
    return theme_data, migration_count


def migrate_theme_file(theme_file_path: Path, dry_run: bool = False) -> bool:
    """Migrate a single theme file.

    Args:
        theme_file_path: Path to theme JSON file
        dry_run: If True, don't write changes, just report what would be done

    Returns:
        True if migration was performed, False otherwise

    """
    if not theme_file_path.exists():
        print(f"Error: File not found: {theme_file_path}")
        return False

    if theme_file_path.suffix != ".json":
        print(f"Skipping non-JSON file: {theme_file_path}")
        return False

    print(f"\nProcessing: {theme_file_path}")

    try:
        # Read theme file
        with open(theme_file_path, encoding="utf-8") as f:
            theme_data = json.load(f)

        # Migrate tokens
        migrated_data, migration_count = migrate_theme_dict(theme_data)

        if migration_count == 0:
            print("  No terminal tokens to migrate")
            return False

        print(f"  Total migrations: {migration_count}")

        if dry_run:
            print(f"  DRY RUN: Would update {theme_file_path}")
            return True

        # Create backup
        backup_path = theme_file_path.with_suffix(".json.bak")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(theme_data, f, indent=2)
        print(f"  Created backup: {backup_path}")

        # Write migrated theme
        with open(theme_file_path, "w", encoding="utf-8") as f:
            json.dump(migrated_data, f, indent=2)
        print(f"  Updated: {theme_file_path}")

        return True

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {theme_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing {theme_file_path}: {e}")
        return False


def migrate_directory(directory_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Migrate all theme files in a directory.

    Args:
        directory_path: Path to directory containing theme files
        dry_run: If True, don't write changes, just report what would be done

    Returns:
        Tuple of (files_migrated, files_processed)

    """
    if not directory_path.is_dir():
        print(f"Error: Not a directory: {directory_path}")
        return 0, 0

    theme_files = list(directory_path.glob("*.json"))
    if not theme_files:
        print(f"No JSON files found in {directory_path}")
        return 0, 0

    files_migrated = 0
    files_processed = 0

    for theme_file in theme_files:
        if migrate_theme_file(theme_file, dry_run=dry_run):
            files_migrated += 1
        files_processed += 1

    return files_migrated, files_processed


def main():
    """Main entry point for migration utility."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Missing theme file or directory path")
        sys.exit(1)

    path_arg = sys.argv[1]
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("DRY RUN MODE: No files will be modified\n")

    path = Path(path_arg).expanduser().resolve()

    if path.is_file():
        success = migrate_theme_file(path, dry_run=dry_run)
        sys.exit(0 if success else 1)
    elif path.is_dir():
        files_migrated, files_processed = migrate_directory(path, dry_run=dry_run)
        print(f"\n{'DRY RUN ' if dry_run else ''}Summary:")
        print(f"  Files processed: {files_processed}")
        print(f"  Files {'would be ' if dry_run else ''}migrated: {files_migrated}")
        sys.exit(0)
    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
