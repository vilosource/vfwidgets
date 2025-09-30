# VFWidgets Theme System Documentation

**Beautiful theming made simple.** The VFWidgets Theme System provides clean architecture as THE way - a simple API that's architecturally correct, with no compromises.

## 🚀 Start Here - 30 Seconds to Themed App

```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

class MyWidget(ThemedWidget):  # ✅ That's it! Clean architecture built-in!
    pass

widget = MyWidget()
widget.show()
app.exec()
```

**That's all!** You get:
- ✅ Automatic theming of all widgets
- ✅ Memory safety (WeakRefs)
- ✅ Thread safety (Qt signals)
- ✅ Clean architecture (dependency injection)
- ✅ VSCode theme compatibility
- ✅ Theme switching support

## 📚 Documentation Index

### For Widget Developers

#### 🎯 [START HERE!](START_HERE.md) **← Your First Stop**
Get themed widgets in 30 seconds. No complexity, just inherit ThemedWidget.

#### 🎯 [Quick Reference Card](quick-reference-CARD.md)
One-page cheat sheet with all the patterns you need.

#### 🍳 [Patterns Cookbook](patterns-cookbook.md)
Copy-paste patterns for common widget scenarios.

### Core Documentation

#### 🔧 [Widget Integration Guide](integration-GUIDE.md)
Deep dive into ThemedWidget and progressive enhancement.

#### 🚀 [Developer Getting Started Guide](developer-GUIDE.md)
Complete guide for building themed applications.

#### 📖 [API Reference](api-REFERENCE.md)
Full API documentation for ThemedWidget, ThemedApplication, and utilities.

#### 🏗️ [Architecture & Design](architecture-DESIGN.md)
How clean architecture is built into ThemedWidget (for the curious).

### Specifications

#### 🎨 [Theme Format Specification](theme-format-SPECIFICATION.md)
Detailed specification of our theme JSON format and property definitions.

#### 💻 [VSCode Compatibility Specification](vscode-compatibility-SPECIFICATION.md)
How we support VSCode themes and the mapping between VSCode and Qt properties.

### Guides

#### 🔄 [Migration Guide](migration-GUIDE.md)
Step-by-step guide for migrating existing widgets to use the theme system.

#### ⭐ [Best Practices Guide](best-practices-GUIDE.md)
Recommended patterns, tips, and common pitfalls to avoid.

### Examples

#### 📂 [Example Themes](examples/)
Collection of example theme files and usage patterns.

## 🎯 Quick Navigation by Role

### I Want to Theme My Widget (90% of users)
1. **Read**: [START HERE!](START_HERE.md) - 30 seconds to success
2. **Reference**: [Quick Reference Card](quick-reference-CARD.md) - Keep it handy
3. **Copy**: [Patterns Cookbook](patterns-cookbook.md) - Find your pattern

### I Want to Build a Themed App
1. **Start**: [Developer Guide](developer-GUIDE.md) - Complete applications
2. **Themes**: [Theme Format Spec](theme-format-SPECIFICATION.md) - Custom themes
3. **Examples**: [Example Themes](examples/) - Get inspired

### I Want to Understand the System
1. **Architecture**: [Architecture & Design](architecture-DESIGN.md) - Clean architecture explained
2. **API**: [API Reference](api-REFERENCE.md) - Complete documentation
3. **VSCode**: [VSCode Compatibility](vscode-compatibility-SPECIFICATION.md) - Theme importing

## 🌟 Why ThemedWidget?

### Simple API, Clean Architecture
- **One Base Class**: Just inherit from `ThemedWidget`
- **Clean Inside**: Proper dependency injection, memory management, thread safety
- **No Compromises**: Easy doesn't mean wrong - we hide complexity, not ignore it

### What You Get Automatically
- **Memory Safety**: WeakRef registry prevents leaks
- **Thread Safety**: Qt signals handle cross-thread updates
- **Error Recovery**: Graceful fallback to minimal theme
- **Child Theming**: All child widgets automatically themed
- **Cleanup**: Proper lifecycle management built-in

### 🎨 For Designers
- **VSCode Theme Support**: Import and use thousands of existing VSCode themes
- **Visual Theme Editor**: GUI for creating and editing themes
- **Live Preview**: See changes in real-time
- **Export Options**: Export to JSON, QSS, or resource files

### 🚀 For Applications
- **Performance Optimized**: Efficient theme application with caching
- **Accessibility**: Built-in high contrast and accessibility themes
- **Platform Adaptive**: Respects system dark/light mode preferences
- **Extensible**: Easy to add custom properties and components

## 📋 Common Tasks

### Complete Themed Application
```python
from vfwidgets_theme import ThemedApplication, ThemedWidget
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")

class MyWidget(ThemedWidget):  # Clean architecture built-in!
    pass

widget = MyWidget()
widget.show()
app.exec()
```

### Widget with Custom Colors
```python
class ColoredWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'accent': 'accent.primary'
    }

    def paintEvent(self, event):
        color = self.theme.bg  # Direct access!
```

### Import a VSCode Theme
```python
app = ThemedApplication(sys.argv)
app.import_vscode_theme("monokai.json")
app.set_theme("Monokai")
```

### React to Theme Changes
```python
class ReactiveWidget(ThemedWidget):
    def on_theme_changed(self):
        if self.is_dark_theme:
            self.load_dark_icons()
        self.update()
```

## 🔗 Related Resources

- [VFWidgets Main Documentation](../../../README.md)
- [Contributing Guide](../../../CONTRIBUTING.md)
- [VSCode Theme Documentation](https://code.visualstudio.com/api/extension-guides/color-theme)
- [Qt Style Sheets Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)

## 📝 Version History

See [CHANGELOG.md](../CHANGELOG.md) for version history and updates.

## 📄 License

The VFWidgets Theme System is released under the MIT License. See [LICENSE](../LICENSE) for details.

---

*For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/vfwidgets/theme-system).*