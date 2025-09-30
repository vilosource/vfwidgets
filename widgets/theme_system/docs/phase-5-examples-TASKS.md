# Phase 5: Examples - Implementation Tasks

## Overview
This phase creates comprehensive examples demonstrating all theme system capabilities with progressive complexity. All examples must use ONLY the public API (ThemedWidget/ThemedApplication).

## Critical Development Rules (from writing-dev-AGENTS.md)

1. **Public API Only**: Examples MUST only use ThemedWidget/ThemedApplication, never internal components
2. **Progressive Complexity**: Start simple, build up to complex applications
3. **Execute Every Example**: Each example must run successfully
4. **Real-World Scenarios**: Examples should solve actual problems
5. **Self-Contained**: Each example should be runnable independently
6. **Educational Value**: Examples teach best practices

## Phase 5 Tasks

### Task 26: Basic Widget Examples
**Objective**: Create simple examples for common Qt widgets

**Requirements**:
1. Create examples in `examples/basic/`
2. Button with theme support
3. Label with dynamic colors
4. Input field with validation styling
5. List widget with alternating rows
6. Simple dialog with theme

**Example Structure**:
```python
#!/usr/bin/env python3
"""
themed_button.py - Simple themed button example

Shows how to create a button that responds to theme changes.
"""

from vfwidgets_theme import ThemedWidget, ThemedApplication

class ThemedButton(ThemedWidget):
    theme_config = {
        'bg': 'button.background',
        'fg': 'button.foreground',
        'hover': 'button.hover'
    }

    def on_theme_changed(self):
        self.update_styling()
```

**Validation Criteria**:
- [ ] Each widget type has example
- [ ] Examples are under 50 lines
- [ ] Clear comments explain concepts
- [ ] All examples run independently
- [ ] Theme switching demonstrated
- [ ] Best practices shown

### Task 27: Layout Examples
**Objective**: Demonstrate themed layouts and containers

**Requirements**:
1. Create examples in `examples/layouts/`
2. Grid layout with themed cells
3. Tab widget with themed tabs
4. Splitter with themed handles
5. Dock widget with themes
6. Stacked widget with transitions

**Example Concepts**:
- Layout managers with themes
- Container widgets
- Dynamic layout changes
- Responsive design
- Theme-aware spacing

**Validation Criteria**:
- [ ] Common layouts covered
- [ ] Responsive to theme changes
- [ ] Clean separation of concerns
- [ ] Performance optimized
- [ ] Mobile-friendly examples
- [ ] Accessibility considered

### Task 28: Application Examples
**Objective**: Complete application examples with themes

**Requirements**:
1. Create examples in `examples/applications/`
2. Text editor with theme support
3. File browser with icons
4. Settings dialog
5. Dashboard with charts
6. Image viewer

**Application Features**:
- Menu bars with themes
- Status bars
- Tool bars
- Dialogs and popups
- Multi-window support
- Settings persistence

**Validation Criteria**:
- [ ] Real-world applications
- [ ] Professional appearance
- [ ] Theme consistency
- [ ] Settings integration
- [ ] Performance optimized
- [ ] Production-ready code

### Task 29: Custom Widget Examples
**Objective**: Show how to create custom themed widgets

**Requirements**:
1. Create examples in `examples/custom/`
2. Custom chart widget
3. Color picker with themes
4. Calendar widget
5. Progress indicator
6. Custom controls

**Custom Widget Patterns**:
```python
class CustomGauge(ThemedWidget):
    """Custom gauge widget with theme support."""

    theme_config = {
        'needle': 'accent.primary',
        'scale': 'text.secondary',
        'background': 'surface.primary'
    }

    def paintEvent(self, event):
        # Custom painting with theme colors
        pass
```

**Validation Criteria**:
- [ ] Painting with theme colors
- [ ] Custom properties exposed
- [ ] Animation support
- [ ] Accessibility features
- [ ] Reusable components
- [ ] Well-documented

### Task 30: Animation Examples
**Objective**: Demonstrate theme transitions and animations

**Requirements**:
1. Create examples in `examples/animations/`
2. Theme transition effects
3. Color animations
4. Widget morphing
5. Parallax scrolling
6. Loading animations

**Animation Patterns**:
- QPropertyAnimation usage
- Theme interpolation
- Easing curves
- Performance optimization
- GPU acceleration

**Validation Criteria**:
- [ ] Smooth animations (60fps)
- [ ] Theme-aware transitions
- [ ] Performance optimized
- [ ] Accessibility options
- [ ] Reduced motion support
- [ ] Cross-platform compatibility

### Task 31: VSCode Theme Examples
**Objective**: Show VSCode theme import and usage

**Requirements**:
1. Create examples in `examples/vscode/`
2. Import popular VSCode themes
3. Code editor with syntax highlighting
4. Terminal emulator themed
5. File tree with icons
6. Theme preview gallery

**VSCode Integration**:
```python
# Import and use VSCode theme
from vfwidgets_theme.importers import VSCodeImporter

importer = VSCodeImporter()
monokai = importer.import_theme('monokai-pro.json')
app.register_theme('monokai', monokai)
app.set_theme('monokai')
```

**Validation Criteria**:
- [ ] Real VSCode themes work
- [ ] Syntax highlighting accurate
- [ ] Icon themes supported
- [ ] Color mapping correct
- [ ] Performance maintained
- [ ] Theme switching smooth

### Task 32: Advanced Integration Examples
**Objective**: Integration with other libraries and frameworks

**Requirements**:
1. Create examples in `examples/integration/`
2. Matplotlib integration
3. Pandas table viewer
4. Web view with themes
5. OpenGL widget themed
6. Database viewer

**Integration Patterns**:
- Third-party library theming
- Data visualization
- Web content integration
- 3D graphics with themes
- Database UI components

**Validation Criteria**:
- [ ] Clean integration
- [ ] Theme consistency
- [ ] Performance maintained
- [ ] Error handling robust
- [ ] Documentation clear
- [ ] Dependencies minimal

### Task 33: Tutorial Series
**Objective**: Step-by-step tutorial examples

**Requirements**:
1. Create tutorials in `examples/tutorials/`
2. 01_hello_theme.py - First themed app
3. 02_custom_theme.py - Create custom theme
4. 03_theme_switching.py - Dynamic switching
5. 04_vscode_import.py - Import VSCode theme
6. 05_custom_widget.py - Build custom widget
7. 06_complete_app.py - Full application

**Tutorial Structure**:
```python
"""
Tutorial 01: Hello Theme
========================

This tutorial shows how to create your first themed application.

What you'll learn:
- Creating a ThemedApplication
- Making a ThemedWidget
- Switching themes
- Responding to theme changes

Let's start with the simplest possible themed app...
"""
```

**Validation Criteria**:
- [ ] Progressive learning curve
- [ ] Each tutorial builds on previous
- [ ] Clear explanations
- [ ] Common pitfalls addressed
- [ ] Best practices emphasized
- [ ] Complete by end

## Directory Structure

```
examples/
  basic/           # Task 26
    themed_button.py
    themed_label.py
    themed_input.py
    themed_list.py
    themed_dialog.py

  layouts/         # Task 27
    grid_layout.py
    tab_widget.py
    splitter.py
    dock_widget.py
    stacked_widget.py

  applications/    # Task 28
    text_editor.py
    file_browser.py
    settings_dialog.py
    dashboard.py
    image_viewer.py

  custom/          # Task 29
    chart_widget.py
    color_picker.py
    calendar.py
    progress_gauge.py
    custom_controls.py

  animations/      # Task 30
    theme_transition.py
    color_morph.py
    widget_animation.py
    parallax_scroll.py
    loading_spinner.py

  vscode/          # Task 31
    import_themes.py
    code_editor.py
    terminal.py
    file_tree.py
    theme_gallery.py

  integration/     # Task 32
    matplotlib_charts.py
    pandas_viewer.py
    web_view.py
    opengl_widget.py
    database_viewer.py

  tutorials/       # Task 33
    01_hello_theme.py
    02_custom_theme.py
    03_theme_switching.py
    04_vscode_import.py
    05_custom_widget.py
    06_complete_app.py

  phase_5_living_example.py  # Growing example
  README.md                  # Example index
```

## Living Example for Phase 5

The living example should demonstrate the breadth of examples:
```python
#!/usr/bin/env python3
"""
Phase 5 Living Example - Comprehensive Example Showcase
"""

# Import all example categories
from examples.basic import themed_button
from examples.layouts import grid_layout
from examples.applications import text_editor
from examples.custom import chart_widget
from examples.animations import theme_transition
from examples.vscode import import_themes
from examples.integration import matplotlib_charts
from examples.tutorials import hello_theme

# Showcase each category...
```

## Success Criteria for Phase 5

Phase 5 is complete when:
1. ✅ 33+ examples created
2. ✅ All examples run successfully
3. ✅ Progressive complexity demonstrated
4. ✅ Real-world scenarios covered
5. ✅ VSCode themes imported
6. ✅ Tutorial series complete
7. ✅ Best practices documented
8. ✅ README with example index

## Notes for Agent

- Examples are for END USERS - only use public API
- Each example must be self-contained
- Focus on clarity over cleverness
- Test every example before marking complete
- Provide clear documentation
- Show best practices by example