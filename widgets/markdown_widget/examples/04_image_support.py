#!/usr/bin/env python3
"""
Example: Image Support

This example demonstrates:
1. Base64 embedded images
2. Relative image paths with set_base_path()
3. Absolute file paths
4. HTTP/HTTPS URLs
5. Custom image resolver for special protocols
"""

import sys
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from vfwidgets_markdown import MarkdownViewer


def create_sample_images(temp_dir: Path) -> None:
    """Create sample images for testing."""
    try:
        from PIL import Image, ImageDraw

        # Create main image
        img = Image.new("RGB", (200, 100), color="#4CAF50")
        draw = ImageDraw.Draw(img)
        draw.text((70, 40), "Sample", fill="white")
        img.save(temp_dir / "sample.png")

        # Create subdirectory with logo
        assets_dir = temp_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        logo = Image.new("RGB", (150, 75), color="#2196F3")
        draw_logo = ImageDraw.Draw(logo)
        draw_logo.text((50, 30), "Logo", fill="white")
        logo.save(assets_dir / "logo.png")

        print(f"[Demo] Created sample images in {temp_dir}")
    except ImportError:
        print("[Demo] PIL not available - using placeholder images")


class ImageDemo(QWidget):
    """Demo widget showing image support."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Image Support Demo")
        self.resize(1000, 700)

        # Create temp directory for sample images
        self.temp_dir = Path(tempfile.mkdtemp(prefix="markdown_demo_"))
        create_sample_images(self.temp_dir)

        # Create layout
        layout = QVBoxLayout(self)

        # Create button panel
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel, stretch=0)

        # Create markdown viewer
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer, stretch=1)

        # Set base path for relative images
        self.viewer.set_base_path(str(self.temp_dir))

        # Load content when ready
        self.viewer.viewer_ready.connect(self._on_viewer_ready)

    def _create_button_panel(self) -> QWidget:
        """Create panel with demo mode buttons."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        btn_basic = QPushButton("1. Basic Images")
        btn_resolver = QPushButton("2. Custom Resolver")
        btn_mixed = QPushButton("3. Mixed Sources")

        btn_basic.clicked.connect(self._show_basic)
        btn_resolver.clicked.connect(self._show_custom_resolver)
        btn_mixed.clicked.connect(self._show_mixed)

        layout.addWidget(btn_basic)
        layout.addWidget(btn_resolver)
        layout.addWidget(btn_mixed)

        return panel

    def _show_basic(self):
        """Show basic image types."""
        # Base64 1x1 red pixel
        base64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

        markdown = f"""# Basic Image Types

## 1. Base64 Embedded Images

Images can be embedded directly as base64 data URIs:

![Red Pixel]({base64_img})

**Pros**: No external dependencies, works offline
**Cons**: Increases markdown file size

## 2. Relative Paths

Using `set_base_path()`, relative paths are resolved automatically:

![Sample Image](sample.png)

![Logo in Subdirectory](assets/logo.png)

**Pros**: Clean markdown, organized file structure
**Cons**: Requires base path configuration

## 3. Absolute Paths

Direct file system paths:

![Absolute Path]({self.temp_dir}/sample.png)

**Pros**: No ambiguity
**Cons**: Not portable across machines

## 4. Web URLs

External images from the internet:

![Python Logo](https://www.python.org/static/community_logos/python-logo-generic.svg)

**Pros**: No local storage needed
**Cons**: Requires internet connection
"""
        self.viewer.set_markdown(markdown)
        print("[Demo] Showing basic image types")

    def _show_custom_resolver(self):
        """Show custom image resolver."""

        # Define custom resolver
        def asset_resolver(src: str) -> str:
            """Resolve custom asset:// protocol."""
            if src.startswith("asset://"):
                # Remove asset:// prefix and resolve
                asset_name = src[8:]
                resolved = str(self.temp_dir / "assets" / asset_name)
                print(f"[Demo] Custom resolver: {src} -> {resolved}")
                return resolved
            return src

        # Set the resolver
        self.viewer.set_image_resolver(asset_resolver)

        markdown = """# Custom Image Resolver

You can define custom image resolution logic using `set_image_resolver()`.

## Example: Custom Protocol

This example uses an `asset://` protocol:

![Custom Protocol Logo](asset://logo.png)

## Implementation

```python
def asset_resolver(src: str) -> str:
    if src.startswith("asset://"):
        asset_name = src[8:]
        return f"/path/to/assets/{asset_name}"
    return src

viewer.set_image_resolver(asset_resolver)
```

## Use Cases

- Custom CDN URLs
- Asset management systems
- Virtual file systems
- Dynamic image generation
- Database-stored images

The resolver receives the source string and returns the resolved path or URL.
"""
        self.viewer.set_markdown(markdown)
        print("[Demo] Showing custom resolver")

    def _show_mixed(self):
        """Show mixed image sources."""
        # Clear custom resolver
        self.viewer.set_image_resolver(None)

        base64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

        markdown = f"""# Mixed Image Sources

Real-world documents often contain images from multiple sources.

## Documentation with Mixed Sources

### Local Screenshots

Project screenshots stored locally:

![Local Sample](sample.png)

### Brand Assets

Company logo from subdirectory:

![Brand Logo](assets/logo.png)

### Embedded Diagrams

Small diagrams embedded as base64:

![Indicator]({base64_img}) Status: Active

### External References

Third-party logos from the web:

![External Logo](https://www.python.org/static/community_logos/python-logo-generic.svg)

## Best Practices

1. **Use relative paths** for project-local images
2. **Embed small icons** (<5KB) as base64
3. **Reference web URLs** for external branding
4. **Avoid absolute paths** for portability

The viewer handles all types seamlessly with proper configuration.
"""
        self.viewer.set_markdown(markdown)
        print("[Demo] Showing mixed sources")

    def _on_viewer_ready(self):
        """Called when viewer is ready - load initial content."""
        print("[Demo] Viewer ready")
        self._show_basic()

    def closeEvent(self, event):
        """Clean up temp directory on close."""
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
            print(f"[Demo] Cleaned up {self.temp_dir}")
        except Exception as e:
            print(f"[Demo] Failed to clean up temp dir: {e}")
        event.accept()


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    demo = ImageDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
