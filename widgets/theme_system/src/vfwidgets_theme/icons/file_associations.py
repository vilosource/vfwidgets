"""File association manager for mapping files to icons.

Provides mapping between file extensions, filenames, and icon names
for the icon theme system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..logging import get_logger

logger = get_logger(__name__)


class FileAssociationManager:
    """Manages file associations for icon themes.

    Maps file extensions and filenames to icon names, supporting
    pattern matching and priority-based resolution.
    """

    def __init__(self):
        """Initialize file association manager."""
        # Extension mappings (extension -> icon_name)
        self.extension_mappings: Dict[str, str] = {}

        # Filename mappings (filename -> icon_name)
        self.filename_mappings: Dict[str, str] = {}

        # Pattern mappings (regex_pattern -> icon_name)
        self.pattern_mappings: List[tuple] = []  # [(compiled_regex, icon_name), ...]

        # Language mappings (language -> icon_name)
        self.language_mappings: Dict[str, str] = {}

        # Priority order for resolution
        self.resolution_order = ["exact_filename", "pattern_match", "extension", "language"]

        # Initialize with common defaults
        self._load_default_associations()

    def _load_default_associations(self):
        """Load default file associations."""
        # Common file type associations
        default_extensions = {
            # Programming languages
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "react",
            "tsx": "react",
            "vue": "vue",
            "java": "java",
            "kt": "kotlin",
            "scala": "scala",
            "go": "go",
            "rs": "rust",
            "cpp": "cpp",
            "cxx": "cpp",
            "cc": "cpp",
            "c": "c",
            "h": "c-header",
            "hpp": "cpp-header",
            "cs": "csharp",
            "php": "php",
            "rb": "ruby",
            "swift": "swift",
            # Web technologies
            "html": "html",
            "htm": "html",
            "css": "css",
            "scss": "sass",
            "sass": "sass",
            "less": "less",
            "styl": "stylus",
            # Data formats
            "json": "json",
            "xml": "xml",
            "yaml": "yaml",
            "yml": "yaml",
            "toml": "toml",
            "ini": "settings",
            "cfg": "settings",
            "conf": "settings",
            "properties": "settings",
            # Documentation
            "md": "markdown",
            "rst": "text",
            "txt": "text",
            "rtf": "text",
            "tex": "latex",
            # Scripts
            "sh": "shell",
            "bash": "shell",
            "zsh": "shell",
            "fish": "shell",
            "ps1": "powershell",
            "bat": "batch",
            "cmd": "batch",
            # Databases
            "sql": "database",
            "db": "database",
            "sqlite": "database",
            # Images
            "png": "image",
            "jpg": "image",
            "jpeg": "image",
            "gif": "image",
            "svg": "svg",
            "bmp": "image",
            "webp": "image",
            "ico": "image",
            # Archives
            "zip": "archive",
            "rar": "archive",
            "7z": "archive",
            "tar": "archive",
            "gz": "archive",
            "bz2": "archive",
            # Documents
            "pdf": "pdf",
            "doc": "word",
            "docx": "word",
            "xls": "excel",
            "xlsx": "excel",
            "ppt": "powerpoint",
            "pptx": "powerpoint",
            # Audio/Video
            "mp3": "audio",
            "wav": "audio",
            "ogg": "audio",
            "mp4": "video",
            "avi": "video",
            "mkv": "video",
            # Other
            "log": "log",
            "tmp": "temp",
            "bak": "backup",
        }

        self.extension_mappings.update(default_extensions)

        # Common filename associations
        default_filenames = {
            # Config files
            "package.json": "npm",
            "package-lock.json": "npm",
            "yarn.lock": "yarn",
            "Gemfile": "ruby",
            "Gemfile.lock": "ruby",
            "requirements.txt": "python",
            "setup.py": "python",
            "pyproject.toml": "python",
            "Cargo.toml": "rust",
            "Cargo.lock": "rust",
            "go.mod": "go",
            "go.sum": "go",
            "build.gradle": "gradle",
            "pom.xml": "maven",
            "CMakeLists.txt": "cmake",
            "Makefile": "makefile",
            "makefile": "makefile",
            # Git files
            ".gitignore": "git",
            ".gitattributes": "git",
            ".gitmodules": "git",
            # Docker files
            "Dockerfile": "docker",
            "docker-compose.yml": "docker",
            "docker-compose.yaml": "docker",
            # CI/CD
            ".travis.yml": "travis",
            ".github": "github",
            "appveyor.yml": "appveyor",
            # IDE files
            ".vscode": "vscode",
            ".idea": "intellij",
            # Other
            "README.md": "readme",
            "README.txt": "readme",
            "README.rst": "readme",
            "LICENSE": "license",
            "CHANGELOG.md": "changelog",
            "TODO.md": "todo",
        }

        self.filename_mappings.update(default_filenames)

        # Language mappings
        default_languages = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java": "java",
            "cpp": "cpp",
            "csharp": "csharp",
            "go": "go",
            "rust": "rust",
            "php": "php",
            "ruby": "ruby",
            "swift": "swift",
            "kotlin": "kotlin",
            "scala": "scala",
            "html": "html",
            "css": "css",
            "json": "json",
            "xml": "xml",
            "yaml": "yaml",
            "markdown": "markdown",
            "shell": "shell",
            "sql": "database",
        }

        self.language_mappings.update(default_languages)

    def add_extension_mapping(self, extension: str, icon_name: str) -> None:
        """Add file extension to icon mapping.

        Args:
            extension: File extension (without dot)
            icon_name: Icon name to map to

        """
        ext = extension.lower().lstrip(".")
        self.extension_mappings[ext] = icon_name
        logger.debug(f"Added extension mapping: .{ext} -> {icon_name}")

    def add_filename_mapping(self, filename: str, icon_name: str) -> None:
        """Add filename to icon mapping.

        Args:
            filename: Exact filename
            icon_name: Icon name to map to

        """
        self.filename_mappings[filename] = icon_name
        logger.debug(f"Added filename mapping: {filename} -> {icon_name}")

    def add_pattern_mapping(self, pattern: str, icon_name: str) -> None:
        """Add regex pattern to icon mapping.

        Args:
            pattern: Regular expression pattern
            icon_name: Icon name to map to

        """
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.pattern_mappings.append((compiled_pattern, icon_name))
            logger.debug(f"Added pattern mapping: {pattern} -> {icon_name}")
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")

    def add_language_mapping(self, language: str, icon_name: str) -> None:
        """Add programming language to icon mapping.

        Args:
            language: Programming language name
            icon_name: Icon name to map to

        """
        self.language_mappings[language.lower()] = icon_name
        logger.debug(f"Added language mapping: {language} -> {icon_name}")

    def get_icon_for_file(self, file_path: Path) -> Optional[str]:
        """Get icon name for file path using resolution order.

        Args:
            file_path: Path to file

        Returns:
            Icon name or None if no mapping found

        """
        filename = file_path.name
        extension = file_path.suffix.lstrip(".").lower()

        for method in self.resolution_order:
            icon_name = None

            if method == "exact_filename":
                icon_name = self.get_icon_for_filename(filename)
            elif method == "pattern_match":
                icon_name = self.get_icon_for_pattern(filename)
            elif method == "extension":
                icon_name = self.get_icon_for_extension(extension)
            elif method == "language":
                language = self.detect_language(file_path)
                if language:
                    icon_name = self.language_mappings.get(language.lower())

            if icon_name:
                return icon_name

        return None

    def get_icon_for_filename(self, filename: str) -> Optional[str]:
        """Get icon name for exact filename.

        Args:
            filename: Filename to check

        Returns:
            Icon name or None

        """
        return self.filename_mappings.get(filename)

    def get_icon_for_extension(self, extension: str) -> Optional[str]:
        """Get icon name for file extension.

        Args:
            extension: File extension (without dot)

        Returns:
            Icon name or None

        """
        ext = extension.lower().lstrip(".")
        return self.extension_mappings.get(ext)

    def get_icon_for_pattern(self, filename: str) -> Optional[str]:
        """Get icon name using pattern matching.

        Args:
            filename: Filename to match

        Returns:
            Icon name or None

        """
        for pattern, icon_name in self.pattern_mappings:
            if pattern.match(filename):
                return icon_name
        return None

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file.

        Args:
            file_path: Path to file

        Returns:
            Language name or None

        """
        extension = file_path.suffix.lstrip(".").lower()

        # Extension to language mapping
        ext_to_lang = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascript",
            "tsx": "typescript",
            "vue": "vue",
            "java": "java",
            "kt": "kotlin",
            "scala": "scala",
            "go": "go",
            "rs": "rust",
            "cpp": "cpp",
            "cxx": "cpp",
            "cc": "cpp",
            "c": "c",
            "h": "c",
            "hpp": "cpp",
            "cs": "csharp",
            "php": "php",
            "rb": "ruby",
            "swift": "swift",
            "html": "html",
            "css": "css",
            "scss": "sass",
            "sass": "sass",
            "less": "less",
            "json": "json",
            "xml": "xml",
            "yaml": "yaml",
            "yml": "yaml",
            "md": "markdown",
            "sh": "shell",
            "bash": "shell",
            "zsh": "shell",
            "fish": "shell",
            "ps1": "powershell",
            "sql": "sql",
        }

        return ext_to_lang.get(extension)

    def load_associations_from_file(self, file_path: Path) -> None:
        """Load associations from JSON file.

        Args:
            file_path: Path to JSON file

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file has invalid JSON

        """
        logger.info(f"Loading file associations from: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Load extension mappings
        if "extensions" in data:
            for ext, icon_name in data["extensions"].items():
                self.add_extension_mapping(ext, icon_name)

        # Load filename mappings
        if "filenames" in data:
            for filename, icon_name in data["filenames"].items():
                self.add_filename_mapping(filename, icon_name)

        # Load pattern mappings
        if "patterns" in data:
            for pattern, icon_name in data["patterns"].items():
                self.add_pattern_mapping(pattern, icon_name)

        # Load language mappings
        if "languages" in data:
            for language, icon_name in data["languages"].items():
                self.add_language_mapping(language, icon_name)

        logger.info(f"Loaded associations from {file_path}")

    def save_associations_to_file(self, file_path: Path) -> None:
        """Save associations to JSON file.

        Args:
            file_path: Path to save JSON file

        """
        data = {
            "extensions": self.extension_mappings,
            "filenames": self.filename_mappings,
            "patterns": {
                pattern.pattern: icon_name for pattern, icon_name in self.pattern_mappings
            },
            "languages": self.language_mappings,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved associations to {file_path}")

    def get_all_extensions(self) -> Set[str]:
        """Get all mapped extensions."""
        return set(self.extension_mappings.keys())

    def get_all_filenames(self) -> Set[str]:
        """Get all mapped filenames."""
        return set(self.filename_mappings.keys())

    def get_all_languages(self) -> Set[str]:
        """Get all mapped languages."""
        return set(self.language_mappings.keys())

    def get_all_icon_names(self) -> Set[str]:
        """Get all unique icon names used in mappings."""
        icon_names = set()
        icon_names.update(self.extension_mappings.values())
        icon_names.update(self.filename_mappings.values())
        icon_names.update(self.language_mappings.values())
        icon_names.update(icon_name for _, icon_name in self.pattern_mappings)
        return icon_names

    def remove_extension_mapping(self, extension: str) -> bool:
        """Remove extension mapping.

        Args:
            extension: Extension to remove

        Returns:
            True if removed, False if not found

        """
        ext = extension.lower().lstrip(".")
        if ext in self.extension_mappings:
            del self.extension_mappings[ext]
            logger.debug(f"Removed extension mapping: .{ext}")
            return True
        return False

    def remove_filename_mapping(self, filename: str) -> bool:
        """Remove filename mapping.

        Args:
            filename: Filename to remove

        Returns:
            True if removed, False if not found

        """
        if filename in self.filename_mappings:
            del self.filename_mappings[filename]
            logger.debug(f"Removed filename mapping: {filename}")
            return True
        return False

    def clear_all_mappings(self) -> None:
        """Clear all mappings."""
        self.extension_mappings.clear()
        self.filename_mappings.clear()
        self.pattern_mappings.clear()
        self.language_mappings.clear()
        logger.info("Cleared all file associations")

    def get_statistics(self) -> Dict[str, int]:
        """Get mapping statistics."""
        return {
            "extension_mappings": len(self.extension_mappings),
            "filename_mappings": len(self.filename_mappings),
            "pattern_mappings": len(self.pattern_mappings),
            "language_mappings": len(self.language_mappings),
            "total_unique_icons": len(self.get_all_icon_names()),
        }
