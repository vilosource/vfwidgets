"""Extension loader for importing and validating extensions.

Handles loading extension modules, parsing metadata, and validating
extension structure and compatibility.
"""

import ast
import importlib
import importlib.util
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

from ..errors import ExtensionError
from ..logging import get_logger
from .system import Extension

logger = get_logger(__name__)


class ExtensionMetadata:
    """Extension metadata parser and validator."""

    REQUIRED_FIELDS = ["name", "version", "description", "author"]
    OPTIONAL_FIELDS = ["dependencies", "provides", "homepage", "license", "tags"]

    @classmethod
    def parse_from_module(cls, module) -> dict[str, Any]:
        """Parse extension metadata from module.

        Args:
            module: Loaded extension module

        Returns:
            Extension metadata dictionary

        Raises:
            ExtensionError: If metadata is invalid

        """
        metadata = {}

        # Try to get metadata from __extension_info__
        if hasattr(module, "__extension_info__"):
            info = module.__extension_info__
            if isinstance(info, dict):
                metadata.update(info)

        # Try to get metadata from individual attributes
        for field in cls.REQUIRED_FIELDS + cls.OPTIONAL_FIELDS:
            attr_name = f"__extension_{field}__"
            if hasattr(module, attr_name):
                metadata[field] = getattr(module, attr_name)

        # Validate required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                raise ExtensionError(f"Extension missing required field: {field}")

        # Set defaults for optional fields
        metadata.setdefault("dependencies", [])
        metadata.setdefault("provides", [])
        metadata.setdefault("tags", [])

        # Validate version format
        cls._validate_version(metadata["version"])

        return metadata

    @classmethod
    def _validate_version(cls, version: str) -> None:
        """Validate version string format."""
        # Simple semantic version validation
        pattern = r"^\d+\.\d+\.\d+(?:-[\w\d-]+)?(?:\+[\w\d-]+)?$"
        if not re.match(pattern, version):
            raise ExtensionError(f"Invalid version format: {version}")

    @classmethod
    def parse_from_file(cls, metadata_file: Path) -> dict[str, Any]:
        """Parse extension metadata from JSON file.

        Args:
            metadata_file: Path to metadata file

        Returns:
            Extension metadata dictionary

        """
        try:
            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.load(f)

            # Validate required fields
            for field in cls.REQUIRED_FIELDS:
                if field not in metadata:
                    raise ExtensionError(f"Extension missing required field: {field}")

            cls._validate_version(metadata["version"])
            return metadata

        except json.JSONDecodeError as e:
            raise ExtensionError(f"Invalid JSON in metadata file: {e}")
        except Exception as e:
            raise ExtensionError(f"Error reading metadata file: {e}")


class ExtensionHookDiscovery:
    """Discovers and validates extension hooks."""

    HOOK_PATTERNS = {
        "on_theme_loaded": r"^on_theme_loaded$",
        "on_theme_applied": r"^on_theme_applied$",
        "on_theme_changed": r"^on_theme_changed$",
        "transform_theme": r"^transform_theme$",
        "provide_widgets": r"^provide_widgets$",
        "customize_colors": r"^customize_colors$",
        "add_properties": r"^add_properties$",
        "validate_theme": r"^validate_theme$",
        "on_extension_loaded": r"^on_extension_loaded$",
        "on_extension_unloaded": r"^on_extension_unloaded$",
    }

    @classmethod
    def discover_hooks(cls, module) -> dict[str, Callable]:
        """Discover hook functions in extension module.

        Args:
            module: Extension module

        Returns:
            Dictionary of hook names to functions

        """
        hooks = {}

        # Get all callable attributes
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                # Check if it matches a hook pattern
                for hook_name, pattern in cls.HOOK_PATTERNS.items():
                    if re.match(pattern, name):
                        hooks[hook_name] = obj
                        logger.debug(f"Found hook: {hook_name} -> {name}")

        return hooks

    @classmethod
    def validate_hook_signature(cls, hook_name: str, hook_func: Callable) -> None:
        """Validate hook function signature.

        Args:
            hook_name: Name of hook
            hook_func: Hook function

        Raises:
            ExtensionError: If signature is invalid

        """
        try:
            signature = inspect.signature(hook_func)
            params = list(signature.parameters.keys())

            # Define expected signatures for each hook
            expected_signatures = {
                "on_theme_loaded": ["theme"],
                "on_theme_applied": ["theme", "widget"],
                "on_theme_changed": ["old_theme", "new_theme"],
                "transform_theme": ["theme"],
                "provide_widgets": [],
                "customize_colors": ["theme"],
                "add_properties": ["theme"],
                "validate_theme": ["theme"],
                "on_extension_loaded": [],
                "on_extension_unloaded": [],
            }

            expected = expected_signatures.get(hook_name, [])

            # Allow additional **kwargs parameter
            if len(params) >= len(expected):
                # Check required parameters
                for i, expected_param in enumerate(expected):
                    if i >= len(params):
                        raise ExtensionError(
                            f"Hook {hook_name} missing parameter: {expected_param}"
                        )

                    # Parameter names don't need to match exactly,
                    # but count should be correct
                    param = signature.parameters[params[i]]
                    if param.kind == inspect.Parameter.VAR_KEYWORD:
                        # **kwargs is allowed
                        break

            else:
                raise ExtensionError(
                    f"Hook {hook_name} has wrong number of parameters. "
                    f"Expected at least {len(expected)}, got {len(params)}"
                )

        except Exception as e:
            raise ExtensionError(f"Invalid hook signature for {hook_name}: {e}")


class ExtensionLoader:
    """Loads and validates extensions from files.

    Handles Python module loading, metadata parsing, and hook discovery.
    """

    def __init__(self):
        """Initialize extension loader."""
        self.metadata_parser = ExtensionMetadata()
        self.hook_discovery = ExtensionHookDiscovery()

    def load_from_file(self, extension_path: Path) -> Extension:
        """Load extension from file.

        Args:
            extension_path: Path to extension file

        Returns:
            Loaded extension

        Raises:
            ExtensionError: If loading fails

        """
        logger.info(f"Loading extension from: {extension_path}")

        if not extension_path.exists():
            raise ExtensionError(f"Extension file not found: {extension_path}")

        try:
            # Load the module
            module = self._load_module(extension_path)

            # Parse metadata
            metadata = self._parse_metadata(extension_path, module)

            # Discover hooks
            hooks = self._discover_hooks(module)

            # Create extension object
            extension = Extension(
                name=metadata["name"],
                version=metadata["version"],
                description=metadata["description"],
                author=metadata["author"],
                path=extension_path,
                module=module,
                dependencies=metadata.get("dependencies", []),
                provides=metadata.get("provides", []),
                hooks=hooks,
                metadata=metadata,
            )

            logger.info(f"Successfully loaded extension: {extension.name}")
            return extension

        except Exception as e:
            logger.error(f"Failed to load extension {extension_path}: {e}")
            raise ExtensionError(f"Extension loading failed: {e}")

    def _load_module(self, extension_path: Path):
        """Load Python module from file."""
        try:
            # Generate module name
            module_name = f"extension_{extension_path.stem}_{hash(str(extension_path)) % 10000}"

            # Load module
            if extension_path.is_dir():
                # Directory-based extension
                init_file = extension_path / "__init__.py"
                if not init_file.exists():
                    raise ExtensionError(
                        f"Extension directory missing __init__.py: {extension_path}"
                    )

                spec = importlib.util.spec_from_file_location(module_name, init_file)
            else:
                # Single file extension
                spec = importlib.util.spec_from_file_location(module_name, extension_path)

            if spec is None or spec.loader is None:
                raise ExtensionError(f"Cannot create module spec for: {extension_path}")

            module = importlib.util.module_from_spec(spec)

            # Add to sys.modules temporarily for imports to work
            sys.modules[module_name] = module

            try:
                spec.loader.exec_module(module)
            except Exception:
                # Remove from sys.modules if loading failed
                if module_name in sys.modules:
                    del sys.modules[module_name]
                raise

            return module

        except Exception as e:
            raise ExtensionError(f"Failed to load module {extension_path}: {e}")

    def _parse_metadata(self, extension_path: Path, module) -> dict[str, Any]:
        """Parse extension metadata."""
        # Try metadata file first
        metadata_file = extension_path.parent / f"{extension_path.stem}.json"
        if extension_path.is_dir():
            metadata_file = extension_path / "extension.json"

        if metadata_file.exists():
            return self.metadata_parser.parse_from_file(metadata_file)

        # Fall back to module metadata
        return self.metadata_parser.parse_from_module(module)

    def _discover_hooks(self, module) -> dict[str, Callable]:
        """Discover and validate hooks in module."""
        hooks = self.hook_discovery.discover_hooks(module)

        # Validate hook signatures
        for hook_name, hook_func in hooks.items():
            try:
                self.hook_discovery.validate_hook_signature(hook_name, hook_func)
            except ExtensionError as e:
                logger.warning(f"Hook validation warning: {e}")
                # Continue with invalid hooks but log warning

        return hooks

    def validate_extension_file(self, extension_path: Path) -> list[str]:
        """Validate extension file and return list of issues.

        Args:
            extension_path: Path to extension file

        Returns:
            List of validation issues (empty if valid)

        """
        issues = []

        if not extension_path.exists():
            issues.append("Extension file does not exist")
            return issues

        try:
            # Try to parse as Python
            if extension_path.suffix == ".py":
                with open(extension_path, encoding="utf-8") as f:
                    source = f.read()

                try:
                    ast.parse(source)
                except SyntaxError as e:
                    issues.append(f"Python syntax error: {e}")

            # Try to load metadata
            try:
                module = self._load_module(extension_path)
                self._parse_metadata(extension_path, module)
            except ExtensionError as e:
                issues.append(f"Metadata error: {e}")

            # Try to discover hooks
            try:
                if "module" in locals():
                    self._discover_hooks(module)
            except ExtensionError as e:
                issues.append(f"Hook error: {e}")

        except Exception as e:
            issues.append(f"General validation error: {e}")

        return issues

    def create_extension_template(self, output_path: Path, extension_name: str) -> None:
        """Create extension template file.

        Args:
            output_path: Where to create template
            extension_name: Name of extension

        """
        template = f'''"""
{extension_name} Extension

This is a template extension for the VFWidgets theme system.
"""

# Extension metadata
__extension_info__ = {{
    "name": "{extension_name}",
    "version": "1.0.0",
    "description": "A sample extension for the theme system",
    "author": "Your Name",
    "dependencies": [],
    "provides": [],
    "tags": ["sample", "template"]
}}


def on_theme_loaded(theme):
    """Called when a theme is loaded."""
    api.log_info(f"Theme loaded: {{theme.name}}")


def transform_theme(theme):
    """Transform theme data before application."""
    # Example: Add custom property
    if hasattr(theme, 'metadata'):
        theme.metadata = theme.metadata or {{}}
        theme.metadata['{extension_name}_processed'] = True

    return theme


def customize_colors(theme):
    """Customize theme colors."""
    # Example: Slightly darken background
    if theme.colors and theme.colors.background:
        theme.colors.background = api.darken_color(theme.colors.background, 0.1)

    return theme


def validate_theme(theme):
    """Validate theme data."""
    issues = []

    if not theme.name:
        issues.append("Theme must have a name")

    return issues


def on_extension_loaded():
    """Called when extension is loaded."""
    api.log_info("{extension_name} extension loaded successfully")


def on_extension_unloaded():
    """Called when extension is unloaded."""
    api.log_info("{extension_name} extension unloaded")


# Extension can access the API through the 'api' global variable
# Available after extension is loaded by the system
'''

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template)

        logger.info(f"Created extension template: {output_path}")
