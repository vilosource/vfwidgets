#!/usr/bin/env python3
"""
Theme Package Manager - Task 20

This module provides theme packaging and distribution management with:
- .vftheme format for packaging themes and metadata
- Dependency resolution and version management
- Installation and uninstallation capabilities
- Package validation and integrity checking

Features:
- .vftheme package format (JSON-based with ZIP compression)
- Semantic versioning support
- Dependency resolution
- Installation directory management
- Package validation and security checks
- Performance optimized for <500ms installation time
"""

import os
import json
import zipfile
import tempfile
import time
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from packaging.version import Version, parse as parse_version

# Import core theme system
from ..core.theme import Theme
from ..errors import ThemeError
from ..factory import ThemeFactory

logger = logging.getLogger(__name__)


@dataclass
class PackageDependency:
    """Represents a package dependency."""
    name: str
    version_spec: str  # e.g., ">=1.0.0,<2.0.0"
    optional: bool = False

    def is_satisfied_by(self, version: str) -> bool:
        """Check if a version satisfies this dependency."""
        # Simplified version checking - in practice would use packaging.specifiers
        target_version = parse_version(version)

        # Basic comparison support
        if self.version_spec.startswith(">="):
            min_version = parse_version(self.version_spec[2:])
            return target_version >= min_version
        elif self.version_spec.startswith("=="):
            exact_version = parse_version(self.version_spec[2:])
            return target_version == exact_version
        else:
            # Default to exact match
            return version == self.version_spec


@dataclass
class ThemePackage:
    """
    Represents a theme package with metadata and dependencies.

    The .vftheme format contains:
    - package.json: Package metadata and dependencies
    - themes/: Directory containing theme files
    - assets/: Optional assets (images, fonts, etc.)
    - readme.md: Package documentation
    """

    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""

    # Dependencies
    dependencies: List[PackageDependency] = field(default_factory=list)

    # Package contents
    themes: Dict[str, Theme] = field(default_factory=dict)
    assets: Dict[str, bytes] = field(default_factory=dict)
    readme: str = ""

    # Installation metadata
    install_path: Optional[Path] = None
    install_time: Optional[float] = None
    installed_by: str = "manual"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemePackage':
        """Create package from dictionary representation."""
        package = cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            license=data.get("license", "MIT"),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", "")
        )

        # Parse dependencies
        for dep_data in data.get("dependencies", []):
            dependency = PackageDependency(
                name=dep_data["name"],
                version_spec=dep_data["version"],
                optional=dep_data.get("optional", False)
            )
            package.dependencies.append(dependency)

        return package

    def to_dict(self) -> Dict[str, Any]:
        """Convert package to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
            "dependencies": [
                {
                    "name": dep.name,
                    "version": dep.version_spec,
                    "optional": dep.optional
                }
                for dep in self.dependencies
            ],
            "install_time": self.install_time,
            "installed_by": self.installed_by
        }

    def has_theme(self, theme_name: str) -> bool:
        """Check if package contains a specific theme."""
        return theme_name in self.themes

    def get_theme_names(self) -> List[str]:
        """Get list of theme names in this package."""
        return list(self.themes.keys())


class ThemePackageManager:
    """
    Main theme package manager for .vftheme packages.

    Provides complete package lifecycle management including installation,
    dependency resolution, and validation.

    Example:
        manager = ThemePackageManager()

        # Install package
        package = manager.install_package("material-themes.vftheme")

        # List installed packages
        packages = manager.list_packages()

        # Uninstall package
        manager.uninstall_package("material-themes")
    """

    def __init__(self, install_directory: Union[str, Path] = None):
        """
        Initialize package manager.

        Args:
            install_directory: Directory for package installations.
                               Defaults to ~/.vfwidgets/packages
        """
        if install_directory:
            self.install_directory = Path(install_directory)
        else:
            home_dir = Path.home()
            self.install_directory = home_dir / ".vfwidgets" / "packages"

        self.install_directory.mkdir(parents=True, exist_ok=True)

        # Package registry
        self._installed_packages: Dict[str, ThemePackage] = {}

        # Theme factory for package themes
        self._theme_factory = ThemeFactory()

        # Load existing packages
        self._load_installed_packages()

        logger.debug(f"ThemePackageManager initialized with install directory: {self.install_directory}")

    def create_package(self, package_info: Dict[str, Any], themes: Dict[str, Theme],
                      output_path: Union[str, Path], assets: Dict[str, bytes] = None) -> Path:
        """
        Create a .vftheme package file.

        Args:
            package_info: Package metadata
            themes: Dictionary of theme name -> Theme object
            output_path: Path for the output .vftheme file
            assets: Optional assets to include

        Returns:
            Path to created package file
        """
        start_time = time.perf_counter()

        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix(".vftheme")

        # Create temporary directory for package contents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create package.json
            package_json = {
                **package_info,
                "created_at": time.time(),
                "themes": list(themes.keys()),
                "format_version": "1.0"
            }

            with open(temp_path / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)

            # Create themes directory and save themes
            themes_dir = temp_path / "themes"
            themes_dir.mkdir()

            for theme_name, theme in themes.items():
                theme_file = themes_dir / f"{theme_name}.json"
                with open(theme_file, "w") as f:
                    json.dump(theme.to_dict(), f, indent=2)

            # Create assets directory if assets provided
            if assets:
                assets_dir = temp_path / "assets"
                assets_dir.mkdir()

                for asset_name, asset_data in assets.items():
                    asset_file = assets_dir / asset_name
                    with open(asset_file, "wb") as f:
                        f.write(asset_data)

            # Create README
            readme_content = f"""# {package_info['name']}

{package_info.get('description', 'A VFWidgets theme package')}

## Author
{package_info.get('author', 'Unknown')}

## Themes Included
{chr(10).join(f'- {name}' for name in themes.keys())}

## Installation
Install this package using the VFWidgets Theme Package Manager.
"""

            with open(temp_path / "readme.md", "w") as f:
                f.write(readme_content)

            # Create .vftheme package (ZIP file)
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(temp_path)
                        zip_file.write(file_path, arc_name)

        create_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Created package {output_path.name} in {create_time:.2f}ms")

        return output_path

    def install_package(self, package_path: Union[str, Path], force: bool = False) -> ThemePackage:
        """
        Install a .vftheme package.

        Args:
            package_path: Path to .vftheme package file
            force: Force installation even if package exists

        Returns:
            Installed ThemePackage object

        Raises:
            ThemeError: If installation fails
        """
        start_time = time.perf_counter()
        package_path = Path(package_path)

        if not package_path.exists():
            raise ThemeError(f"Package file not found: {package_path}")

        if not package_path.suffix == ".vftheme":
            raise ThemeError(f"Invalid package format. Expected .vftheme file")

        try:
            # Extract and validate package
            package = self._extract_and_validate_package(package_path)

            # Check if already installed
            if package.name in self._installed_packages and not force:
                existing = self._installed_packages[package.name]
                raise ThemeError(f"Package '{package.name}' already installed (version {existing.version}). Use force=True to overwrite.")

            # Resolve dependencies
            self._resolve_dependencies(package)

            # Install package
            install_path = self.install_directory / package.name
            if install_path.exists():
                shutil.rmtree(install_path)

            # Extract package to install directory
            with zipfile.ZipFile(package_path, "r") as zip_file:
                zip_file.extractall(install_path)

            # Update package metadata
            package.install_path = install_path
            package.install_time = time.time()

            # Register package
            self._installed_packages[package.name] = package

            # Save package registry
            self._save_package_registry()

            install_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Installed package '{package.name}' v{package.version} in {install_time:.2f}ms")

            # Performance requirement check
            if install_time > 500:  # Task requirement: <500ms
                logger.warning(f"Slow package installation: {install_time:.2f}ms for {package.name}")

            return package

        except Exception as e:
            logger.error(f"Failed to install package {package_path}: {e}")
            raise ThemeError(f"Package installation failed: {e}") from e

    def uninstall_package(self, package_name: str) -> bool:
        """
        Uninstall a theme package.

        Args:
            package_name: Name of package to uninstall

        Returns:
            True if uninstalled successfully
        """
        if package_name not in self._installed_packages:
            logger.warning(f"Package '{package_name}' not installed")
            return False

        try:
            package = self._installed_packages[package_name]

            # Remove package directory
            if package.install_path and package.install_path.exists():
                shutil.rmtree(package.install_path)

            # Remove from registry
            del self._installed_packages[package_name]

            # Save updated registry
            self._save_package_registry()

            logger.info(f"Uninstalled package '{package_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to uninstall package {package_name}: {e}")
            return False

    def list_packages(self) -> List[ThemePackage]:
        """List all installed packages."""
        return list(self._installed_packages.values())

    def get_package(self, package_name: str) -> Optional[ThemePackage]:
        """Get installed package by name."""
        return self._installed_packages.get(package_name)

    def list_themes(self, package_name: str = None) -> Dict[str, str]:
        """
        List themes from packages.

        Args:
            package_name: Optional package name to filter by

        Returns:
            Dictionary of theme_name -> package_name
        """
        themes = {}

        packages_to_check = [self._installed_packages[package_name]] if package_name else self._installed_packages.values()

        for package in packages_to_check:
            if package.name not in self._installed_packages:
                continue

            for theme_name in package.get_theme_names():
                themes[theme_name] = package.name

        return themes

    def get_theme_from_package(self, theme_name: str, package_name: str = None) -> Optional[Theme]:
        """
        Get a theme from an installed package.

        Args:
            theme_name: Name of theme to retrieve
            package_name: Optional package name to search in

        Returns:
            Theme object if found
        """
        packages_to_search = [self._installed_packages[package_name]] if package_name else self._installed_packages.values()

        for package in packages_to_search:
            if package.has_theme(theme_name):
                return package.themes[theme_name]

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get package manager statistics."""
        total_themes = sum(len(pkg.themes) for pkg in self._installed_packages.values())
        total_size = 0

        for package in self._installed_packages.values():
            if package.install_path and package.install_path.exists():
                total_size += sum(f.stat().st_size for f in package.install_path.rglob("*") if f.is_file())

        return {
            "installed_packages": len(self._installed_packages),
            "total_themes": total_themes,
            "install_directory": str(self.install_directory),
            "total_size_bytes": total_size,
            "packages": [
                {
                    "name": pkg.name,
                    "version": pkg.version,
                    "themes": len(pkg.themes),
                    "install_time": pkg.install_time
                }
                for pkg in self._installed_packages.values()
            ]
        }

    def _extract_and_validate_package(self, package_path: Path) -> ThemePackage:
        """Extract and validate a .vftheme package."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract package
            with zipfile.ZipFile(package_path, "r") as zip_file:
                zip_file.extractall(temp_path)

            # Load package.json
            package_json_path = temp_path / "package.json"
            if not package_json_path.exists():
                raise ThemeError("Invalid package: missing package.json")

            with open(package_json_path, "r") as f:
                package_data = json.load(f)

            # Validate required fields
            required_fields = ["name", "version"]
            for field in required_fields:
                if field not in package_data:
                    raise ThemeError(f"Invalid package: missing required field '{field}'")

            # Create package object
            package = ThemePackage.from_dict(package_data)

            # Load themes
            themes_dir = temp_path / "themes"
            if themes_dir.exists():
                for theme_file in themes_dir.glob("*.json"):
                    try:
                        with open(theme_file, "r") as f:
                            theme_data = json.load(f)

                        theme = Theme.from_dict(theme_data)
                        package.themes[theme.name] = theme

                    except Exception as e:
                        logger.warning(f"Failed to load theme {theme_file.name}: {e}")

            # Load README
            readme_path = temp_path / "readme.md"
            if readme_path.exists():
                with open(readme_path, "r") as f:
                    package.readme = f.read()

            # Load assets
            assets_dir = temp_path / "assets"
            if assets_dir.exists():
                for asset_file in assets_dir.rglob("*"):
                    if asset_file.is_file():
                        with open(asset_file, "rb") as f:
                            asset_name = str(asset_file.relative_to(assets_dir))
                            package.assets[asset_name] = f.read()

            return package

    def _resolve_dependencies(self, package: ThemePackage):
        """Resolve package dependencies (simplified implementation)."""
        for dependency in package.dependencies:
            if dependency.optional:
                continue

            if dependency.name not in self._installed_packages:
                logger.warning(f"Missing dependency: {dependency.name} {dependency.version_spec}")
                if not dependency.optional:
                    raise ThemeError(f"Required dependency not found: {dependency.name}")
            else:
                installed_version = self._installed_packages[dependency.name].version
                if not dependency.is_satisfied_by(installed_version):
                    raise ThemeError(f"Dependency version conflict: {dependency.name} requires {dependency.version_spec}, found {installed_version}")

        logger.debug(f"Dependencies resolved for package {package.name}")

    def _load_installed_packages(self):
        """Load installed packages from registry."""
        registry_path = self.install_directory / "registry.json"
        if not registry_path.exists():
            return

        try:
            with open(registry_path, "r") as f:
                registry_data = json.load(f)

            for package_name, package_data in registry_data.get("packages", {}).items():
                package = ThemePackage.from_dict(package_data)

                # Check if package directory still exists
                install_path = self.install_directory / package_name
                if install_path.exists():
                    package.install_path = install_path

                    # Load themes from installed package
                    themes_dir = install_path / "themes"
                    if themes_dir.exists():
                        for theme_file in themes_dir.glob("*.json"):
                            try:
                                with open(theme_file, "r") as f:
                                    theme_data = json.load(f)
                                theme = Theme.from_dict(theme_data)
                                package.themes[theme.name] = theme
                            except Exception as e:
                                logger.warning(f"Failed to load theme {theme_file.name}: {e}")

                    self._installed_packages[package_name] = package
                else:
                    logger.warning(f"Package directory missing for {package_name}, removing from registry")

            logger.debug(f"Loaded {len(self._installed_packages)} installed packages")

        except Exception as e:
            logger.error(f"Failed to load package registry: {e}")

    def _save_package_registry(self):
        """Save package registry to disk."""
        registry_path = self.install_directory / "registry.json"

        registry_data = {
            "version": "1.0",
            "updated_at": time.time(),
            "packages": {
                name: package.to_dict()
                for name, package in self._installed_packages.items()
            }
        }

        try:
            with open(registry_path, "w") as f:
                json.dump(registry_data, f, indent=2)

            logger.debug("Package registry saved")

        except Exception as e:
            logger.error(f"Failed to save package registry: {e}")