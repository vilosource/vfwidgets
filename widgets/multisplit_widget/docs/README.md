# MultiSplit Widget Documentation

## Overview

MultiSplit is a **pure layout container widget** for PySide6/PyQt that manages recursive split-pane interfaces. It follows strict MVC architecture with a widget provider pattern, ensuring complete separation between layout management and widget creation.

### Core Principles

1. **Layout Container, Not Widget Factory** - MultiSplit arranges widgets but never creates them
2. **Strict MVC Architecture** - Model knows no Qt, View never mutates Model, Controller is sole writer
3. **Extensible Without Modification** - Complete skeleton with minimal meat, all interfaces defined upfront
4. **Documentation-First Development** - Write → Document → Execute workflow

---

## Documentation Structure

This documentation is organized into six main sections, each building upon the previous:

### 📚 [01-overview/](01-overview/)
Foundation concepts and getting started.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [introduction.md](01-overview/introduction.md) | What is MultiSplit? | Core value proposition, what it is/isn't, comparisons |
| [core-concepts.md](01-overview/core-concepts.md) | Essential concepts | Tree structure, widget provider, MVC pattern |
| [quick-start.md](01-overview/quick-start.md) | Get running quickly | Basic usage, minimal example, common patterns |

### 🏗️ [02-architecture/](02-architecture/)
System architecture and design patterns.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [mvc-architecture.md](02-architecture/mvc-architecture.md) | MVC implementation | Layer separation, responsibilities, signal flow |
| [widget-provider.md](02-architecture/widget-provider.md) | Widget management | Provider pattern, lifecycle, application duties |
| [tree-structure.md](02-architecture/tree-structure.md) | Layout system | Tree nodes, ratios, geometry calculation |

### 💻 [03-implementation/](03-implementation/)
Development process and implementation plan.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [mvp-plan.md](03-implementation/mvp-plan.md) | Complete MVP roadmap | Phase 0-3, all components, success criteria |
| [development-protocol.md](03-implementation/development-protocol.md) | How we build | Write→Document→Execute, task structure |
| [development-rules.md](03-implementation/development-rules.md) | Coding standards | Critical rules, patterns, validation |

### 🎨 [04-design/](04-design/)
Detailed design of each system layer.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [model-design.md](04-design/model-design.md) | Model layer | Pure Python, tree nodes, signals |
| [controller-design.md](04-design/controller-design.md) | Controller layer | Commands, undo/redo, transactions |
| [view-design.md](04-design/view-design.md) | View layer | Reconciliation, rendering, events |
| [focus-management.md](04-design/focus-management.md) | Focus system | Tracking, navigation, spatial movement |

### 🔌 [05-api/](05-api/)
API reference and contracts.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [public-api.md](05-api/public-api.md) | Widget API | Methods, properties, usage |
| [protocols.md](05-api/protocols.md) | Interfaces | Provider, visitor, renderer protocols |
| [signals.md](05-api/signals.md) | Signal reference | All signals, parameters, usage |

### 📖 [06-guides/](06-guides/)
Practical guides for users and developers.

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [usage-guide.md](06-guides/usage-guide.md) | Using the widget | Common patterns, examples, tips |
| [integration-guide.md](06-guides/integration-guide.md) | App integration | Provider implementation, persistence |
| [extension-guide.md](06-guides/extension-guide.md) | Adding features | New commands, renderers, handlers |

---

## Reading Order

### For First-Time Readers
1. Start with [introduction.md](01-overview/introduction.md)
2. Read [core-concepts.md](01-overview/core-concepts.md)
3. Review [quick-start.md](01-overview/quick-start.md)
4. Explore other sections as needed

### For Implementers
1. Read [mvp-plan.md](03-implementation/mvp-plan.md) for the roadmap
2. Study [development-rules.md](03-implementation/development-rules.md) for standards
3. Follow [development-protocol.md](03-implementation/development-protocol.md) for workflow
4. Reference design documents as you implement each layer

### For Application Developers
1. Start with [quick-start.md](01-overview/quick-start.md)
2. Read [widget-provider.md](02-architecture/widget-provider.md)
3. Study [public-api.md](05-api/public-api.md)
4. Follow [integration-guide.md](06-guides/integration-guide.md)

---

## Key Concepts Summary

### The Widget Provider Pattern
```python
# MultiSplit asks for widgets
widget_needed.emit(widget_id, pane_id)

# Application provides widgets
def provide_widget(widget_id: str, pane_id: str) -> QWidget:
    return create_appropriate_widget(widget_id)
```

### MVC Layer Separation
```
Model:      Pure Python, no Qt imports, owns structure
Controller: Commands only, sole mutation point
View:       Qt widgets, reconciliation, never mutates model
```

### Development Workflow
```
1. WRITE     → Create comprehensive documentation
2. DOCUMENT  → Break into detailed tasks
3. EXECUTE   → Agent implements following rules
```

---

## Document Standards

All documents in this collection follow these standards:

### Structure
- **Clear sections** with headers
- **Code examples** in Python
- **Tables** for quick reference
- **Diagrams** where helpful

### LLM/Agent Optimization
- **Explicit rules** (DO/DON'T)
- **Code templates** for common patterns
- **Validation checklists**
- **Decision trees** for choices
- **Cross-references** with relative links

### Consistency
- **Terminology** used consistently
- **Examples** build on each other
- **No contradictions** between documents
- **Single source of truth** for each concept

---

## Quick Reference

### File Organization
```
src/
├── core/           # Model layer (NO Qt)
├── controller/     # Controller layer
├── view/           # View layer (Qt allowed)
└── multisplit.py   # Public API
```

### Import Rules
```python
# ✅ ALLOWED
core/model.py:      # No imports from other layers
controller/cmd.py:  from core import ...
view/widget.py:     from core import ... (read-only)

# ❌ FORBIDDEN
core/model.py:      from PySide6 import ...
controller/cmd.py:  from view import ...
```

### Critical Rules
1. **No Qt in Model** - Pure Python only
2. **Commands for mutations** - No direct model changes
3. **Reconcile, don't rebuild** - Preserve widgets
4. **Provider creates widgets** - MultiSplit only arranges

---

## Version

**Documentation Version**: 1.0.0
**Widget Version**: MVP (0.1.0)
**Last Updated**: 2024

---

## Contributing

When updating documentation:
1. Maintain consistency with existing documents
2. Update cross-references if needed
3. Ensure no contradictions introduced
4. Follow the document standards above
5. Update version and date

---

This documentation represents the complete, reconciled understanding of the MultiSplit widget architecture and implementation plan.