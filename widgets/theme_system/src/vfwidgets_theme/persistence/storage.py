"""Theme Persistence Storage System

This module implements comprehensive theme persistence with:
- JSON serialization for theme data
- Theme validation on load
- Automatic backup before save
- Migration support for old formats
- Compression for large themes
"""

import datetime
import gzip
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.theme import Theme
from ..errors import ThemeError


class PersistenceError(ThemeError):
    """Base error for persistence operations."""

    pass


class ThemeFormatError(PersistenceError):
    """Error for invalid theme format."""

    pass


@dataclass
class ThemeValidationResult:
    """Result of theme validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0


class BackupManager:
    """Manages theme backups with rotation."""

    def __init__(self, backup_dir: Path, max_backups: int = 10):
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, original_file: Path) -> Optional[Path]:
        """Create backup of theme file."""
        if not original_file.exists():
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original_file.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(original_file, backup_path)
            self._rotate_backups(original_file.stem)
            return backup_path
        except Exception as e:
            raise PersistenceError(f"Failed to create backup: {e}") from e

    def _rotate_backups(self, base_name: str):
        """Remove old backups to maintain max_backups limit."""
        pattern = f"{base_name}_*.bak"
        backups = sorted(self.backup_dir.glob(pattern))

        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
            except Exception:
                pass  # Ignore backup cleanup errors

    def list_backups(self, base_name: str) -> List[Path]:
        """List available backups for a theme."""
        pattern = f"{base_name}_*.bak"
        return sorted(self.backup_dir.glob(pattern), reverse=True)

    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore a backup to target location."""
        try:
            shutil.copy2(backup_path, target_path)
            return True
        except Exception:
            return False


class ThemeMigrator:
    """Handles migration of old theme formats."""

    CURRENT_VERSION = "1.0.0"

    @classmethod
    def detect_version(cls, theme_data: Dict[str, Any]) -> str:
        """Detect theme format version."""
        # Check for version field
        if "version" in theme_data:
            return str(theme_data["version"])

        # Legacy detection based on structure
        if "properties" in theme_data and isinstance(theme_data["properties"], dict):
            return "0.9"  # Legacy format

        return "unknown"

    @classmethod
    def migrate_theme(cls, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate theme data to current format."""
        version = cls.detect_version(theme_data)

        if version == cls.CURRENT_VERSION:
            return theme_data

        if version == "0.9":
            return cls._migrate_from_v09(theme_data)

        if version == "unknown":
            return cls._migrate_unknown(theme_data)

        raise ThemeFormatError(f"Unsupported theme version: {version}")

    @classmethod
    def _migrate_from_v09(cls, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from v0.9 format."""
        migrated = {
            "version": cls.CURRENT_VERSION,
            "name": theme_data.get("name", "Migrated Theme"),
            "description": theme_data.get("description", "Migrated from v0.9"),
            "author": theme_data.get("author", "Unknown"),
            "created_at": theme_data.get("created_at", datetime.datetime.now().isoformat()),
            "updated_at": datetime.datetime.now().isoformat(),
            "migration_info": {
                "original_version": "0.9",
                "migrated_at": datetime.datetime.now().isoformat(),
            },
        }

        # Migrate properties
        if "properties" in theme_data:
            migrated["properties"] = theme_data["properties"]
        else:
            migrated["properties"] = {}

        # Migrate metadata if present
        if "metadata" in theme_data:
            migrated["metadata"] = theme_data["metadata"]

        return migrated

    @classmethod
    def _migrate_unknown(cls, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Best effort migration for unknown format."""
        # Try to extract what we can
        migrated = {
            "version": cls.CURRENT_VERSION,
            "name": "Unknown Format Theme",
            "description": "Migrated from unknown format",
            "author": "Unknown",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "migration_info": {
                "original_version": "unknown",
                "migrated_at": datetime.datetime.now().isoformat(),
                "original_keys": list(theme_data.keys()),
            },
        }

        # Try to find properties
        properties = {}

        # Look for common property structures
        if "colors" in theme_data:
            for key, value in theme_data["colors"].items():
                properties[f"color.{key}"] = value

        if "fonts" in theme_data:
            for key, value in theme_data["fonts"].items():
                properties[f"font.{key}"] = value

        if "properties" in theme_data:
            properties.update(theme_data["properties"])

        migrated["properties"] = properties

        return migrated


class ThemeValidator:
    """Validates theme data structure and content."""

    REQUIRED_FIELDS = ["name", "version", "properties"]
    RECOMMENDED_FIELDS = ["description", "author", "created_at"]

    @classmethod
    def validate_theme(cls, theme_data: Dict[str, Any]) -> ThemeValidationResult:
        """Validate theme data structure."""
        errors = []
        warnings = []

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in theme_data:
                errors.append(f"Missing required field: {field}")

        # Check recommended fields
        for field in cls.RECOMMENDED_FIELDS:
            if field not in theme_data:
                warnings.append(f"Missing recommended field: {field}")

        # Validate specific field types
        if "properties" in theme_data:
            prop_errors = cls._validate_properties(theme_data["properties"])
            errors.extend(prop_errors)

        if "version" in theme_data:
            version_errors = cls._validate_version(theme_data["version"])
            errors.extend(version_errors)

        # Check for unknown fields that might be typos
        known_fields = {
            "name",
            "version",
            "properties",
            "description",
            "author",
            "created_at",
            "updated_at",
            "metadata",
            "migration_info",
        }

        for field in theme_data.keys():
            if field not in known_fields:
                warnings.append(f"Unknown field (possible typo): {field}")

        return ThemeValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    @classmethod
    def _validate_properties(cls, properties: Any) -> List[str]:
        """Validate properties structure."""
        errors = []

        if not isinstance(properties, dict):
            errors.append("Properties must be a dictionary")
            return errors

        # Validate property keys and values
        for key, value in properties.items():
            if not isinstance(key, str):
                errors.append(f"Property key must be string: {key}")

            # Basic value validation
            if value is None:
                warnings = []  # Allow None values
            elif isinstance(value, (str, int, float, bool)):
                pass  # Valid primitive types
            elif isinstance(value, dict):
                # Nested property objects are allowed
                pass
            else:
                errors.append(f"Invalid property value type for {key}: {type(value)}")

        return errors

    @classmethod
    def _validate_version(cls, version: Any) -> List[str]:
        """Validate version field."""
        errors = []

        if not isinstance(version, str):
            errors.append("Version must be a string")
        else:
            # Basic semantic version validation
            if (
                not version.replace(".", "")
                .replace("-", "")
                .replace("+", "")
                .replace("_", "")
                .isalnum()
            ):
                errors.append(f"Invalid version format: {version}")

        return errors


class ThemePersistence:
    """Save and load themes with validation and migration."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._backup_dir = self.storage_dir / ".backups"
        self.backup_manager = BackupManager(self._backup_dir)
        self.migrator = ThemeMigrator()
        self.validator = ThemeValidator()

    def save_theme(
        self, theme: Theme, filename: Optional[str] = None, compress: bool = False
    ) -> Path:
        """Save theme to disk with validation and backup.

        Args:
            theme: Theme to save
            filename: Optional filename, defaults to theme name
            compress: Whether to compress the file

        Returns:
            Path to saved file

        """
        if filename is None:
            filename = f"{theme.name.replace(' ', '_').lower()}.json"

        if compress and not filename.endswith(".gz"):
            filename += ".gz"

        file_path = self.storage_dir / filename

        try:
            # Create backup if file exists
            backup_path = None
            if file_path.exists():
                backup_path = self.backup_manager.create_backup(file_path)

            # Serialize theme data
            theme_data = self._serialize_theme(theme)

            # Validate before saving
            validation = self.validator.validate_theme(theme_data)
            if validation.has_errors:
                raise ThemeFormatError(f"Theme validation failed: {', '.join(validation.errors)}")

            # Save theme data
            if compress:
                with gzip.open(file_path, "wt", encoding="utf-8") as f:
                    json.dump(theme_data, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(theme_data, f, indent=2, ensure_ascii=False)

            return file_path

        except Exception as e:
            # Try to restore backup if save failed
            if backup_path and backup_path.exists():
                self.backup_manager.restore_backup(backup_path, file_path)

            raise PersistenceError(f"Failed to save theme: {e}") from e

    def load_theme(self, path: Path, validate: bool = True) -> Theme:
        """Load theme from disk with migration and validation.

        Args:
            path: Path to theme file
            validate: Whether to validate theme data

        Returns:
            Loaded Theme object

        """
        file_path = Path(path)

        if not file_path.exists():
            raise PersistenceError(f"Theme file not found: {file_path}")

        try:
            # Load theme data
            if file_path.suffix == ".gz":
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    theme_data = json.load(f)
            else:
                with open(file_path, encoding="utf-8") as f:
                    theme_data = json.load(f)

            # Migrate if needed
            theme_data = self.migrator.migrate_theme(theme_data)

            # Validate if requested
            if validate:
                validation = self.validator.validate_theme(theme_data)
                if validation.has_errors:
                    raise ThemeFormatError(
                        f"Theme validation failed: {', '.join(validation.errors)}"
                    )

            # Create Theme object
            return self._deserialize_theme(theme_data)

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ThemeFormatError(f"Invalid theme file format: {e}") from e
        except Exception as e:
            raise PersistenceError(f"Failed to load theme: {e}") from e

    def list_themes(self) -> List[Path]:
        """List available theme files."""
        patterns = ["*.json", "*.json.gz"]
        theme_files = []

        for pattern in patterns:
            theme_files.extend(self.storage_dir.glob(pattern))

        return sorted(theme_files)

    def get_theme_info(self, path: Path) -> Dict[str, Any]:
        """Get theme metadata without full loading."""
        try:
            file_path = Path(path)

            if file_path.suffix == ".gz":
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    theme_data = json.load(f)
            else:
                with open(file_path, encoding="utf-8") as f:
                    theme_data = json.load(f)

            # Return metadata only
            return {
                "name": theme_data.get("name", "Unknown"),
                "version": theme_data.get("version", "Unknown"),
                "description": theme_data.get("description", ""),
                "author": theme_data.get("author", "Unknown"),
                "created_at": theme_data.get("created_at", ""),
                "updated_at": theme_data.get("updated_at", ""),
                "file_size": file_path.stat().st_size,
                "compressed": file_path.suffix == ".gz",
            }
        except Exception as e:
            return {"error": str(e)}

    def _serialize_theme(self, theme: Theme) -> Dict[str, Any]:
        """Serialize Theme object to dictionary."""
        # Use the theme's built-in to_dict method and enhance with persistence fields
        theme_dict = theme.to_dict()

        # Add persistence-specific metadata
        persistence_data = {
            "version": ThemeMigrator.CURRENT_VERSION,
            "description": theme.metadata.get("description", ""),
            "author": theme.metadata.get("author", "Unknown"),
            "created_at": theme.metadata.get("created_at", datetime.datetime.now().isoformat()),
            "updated_at": datetime.datetime.now().isoformat(),
        }

        # Merge colors and styles into a properties dict for compatibility
        properties = {}
        properties.update(theme.colors)
        properties.update(theme.styles)

        # Create final serialization format
        return {
            **theme_dict,
            **persistence_data,
            "properties": properties,  # Unified properties for easier validation
        }

    def _deserialize_theme(self, theme_data: Dict[str, Any]) -> Theme:
        """Deserialize dictionary to Theme object."""
        from ..core.theme import Theme as ThemeClass

        # Extract colors and styles from properties if available
        properties = theme_data.get("properties", {})
        colors = theme_data.get("colors", {})
        styles = theme_data.get("styles", {})

        # If no colors/styles but we have properties, try to split them
        if not colors and not styles and properties:
            # Simple heuristic: color-related keys go to colors, others to styles
            for key, value in properties.items():
                if any(
                    color_word in key.lower()
                    for color_word in ["color", "background", "foreground", "border"]
                ):
                    colors[key] = value
                else:
                    styles[key] = value

        # Build metadata including persistence fields
        metadata = theme_data.get("metadata", {}).copy()
        if "description" in theme_data:
            metadata["description"] = theme_data["description"]
        if "author" in theme_data:
            metadata["author"] = theme_data["author"]
        if "created_at" in theme_data:
            metadata["created_at"] = theme_data["created_at"]
        if "updated_at" in theme_data:
            metadata["updated_at"] = theme_data["updated_at"]

        # Create Theme object with proper parameters
        return ThemeClass(
            name=theme_data.get("name", "Unnamed Theme"),
            version=theme_data.get("version", "1.0.0"),
            type=theme_data.get("type", "light"),
            colors=colors,
            styles=styles,
            metadata=metadata,
            token_colors=theme_data.get("tokenColors", []),
        )
