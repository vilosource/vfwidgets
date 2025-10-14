# Font Support Implementation Tasks

**Status: 🚀 Ready for Implementation**

This document contains the detailed phase-by-phase implementation plan for font support in VFWidgets Theme System v2.1.0.

Each phase ends with a working demo that can be run and tested.

---

## Implementation Phases

### Phase 1: Core Font Infrastructure (Week 1)
**Goal**: Basic font token storage and validation
**Duration**: 2-3 days
**Demo**: `examples/11_font_theme_basics.py`

#### Tasks

- [ ] **Add fonts field to Theme** (`src/vfwidgets_theme/core/theme.py`)
  - Add `fonts: FontPalette = field(default_factory=dict)` to Theme dataclass
  - Define `FontPalette = dict[str, Union[FontFamily, FontSize, FontWeight, str, float]]`
  - Update `__post_init__()` to validate fonts

- [ ] **Create font exceptions** (`src/vfwidgets_theme/core/exceptions.py`)
  - Add `FontError(Exception)` base class
  - Add `FontValidationError(FontError)`
  - Add `FontPropertyError(FontError)`
  - Add `FontTokenNotFoundError(FontError)`
  - Add `FontNotAvailableError(FontError)`

- [ ] **Add font validation logic** (`src/vfwidgets_theme/core/theme.py`)
  - Validate fontFamily (string or list of strings)
  - Validate fontSize (positive number, max 144pt)
  - Validate fontWeight (100-900 or valid string)
  - Validate lineHeight (>= 0.5)
  - Validate letterSpacing (any number)
  - Validate required fallbacks (mono → "monospace", ui → "sans-serif")

- [ ] **Update package themes with font tokens**
  - `themes/dark-default.json` - Add fonts section with all categories
  - `themes/light-default.json` - Add fonts section
  - `themes/high-contrast.json` - Add fonts section

- [ ] **Write validation tests** (`tests/unit/test_font_validation.py`)
  - test_theme_with_fonts_validates()
  - test_invalid_font_family_type_raises()
  - test_invalid_font_size_raises()
  - test_invalid_font_weight_raises()
  - test_negative_font_size_raises()
  - test_font_size_too_large_raises()
  - test_missing_mono_fallback_raises()
  - test_fonts_mono_must_end_with_monospace()
  - test_fonts_ui_must_end_with_sans_serif()
  - test_font_weight_string_conversion()
  - test_fractional_font_sizes_allowed()
  - test_empty_font_family_list()
  - test_theme_without_fonts_uses_defaults()
  - test_font_property_error_message()
  - test_font_validation_error_message()

- [ ] **Create demo** (`examples/11_font_theme_basics.py`)
  - Load theme with font tokens
  - Print font values to console
  - Show validation in action
  - Display theme structure

#### Exit Criteria
- ✅ Theme can load fonts from JSON
- ✅ Invalid fonts raise clear errors with helpful messages
- ✅ All 15 validation tests pass
- ✅ Demo runs and displays font tokens
- ✅ Package themes have complete font definitions

---

### Phase 2: Font Token Resolution (Week 1-2)
**Goal**: Hierarchical font resolution with FontTokenRegistry
**Duration**: 3-4 days
**Demo**: `examples/12_font_resolution.py`

#### Tasks

- [ ] **Create FontTokenRegistry** (`src/vfwidgets_theme/core/font_tokens.py` - NEW FILE)
  - Define HIERARCHY_MAP with resolution chains
  - Implement get_font_family(token, theme) → list[str]
  - Implement get_font_size(token, theme) → float
  - Implement get_font_weight(token, theme) → int
  - Implement get_line_height(token, theme) → float
  - Implement get_letter_spacing(token, theme) → float
  - Implement get_qfont(token_prefix, theme) → QFont
  - Implement get_available_font(families) → Optional[str]
  - Add @lru_cache decorators for performance
  - Add clear_cache() static method

- [ ] **Export FontTokenRegistry** (`src/vfwidgets_theme/core/__init__.py`)
  - Add FontTokenRegistry to __all__
  - Add to public API

- [ ] **Write resolution tests** (`tests/unit/test_font_tokens.py`)
  - test_font_family_hierarchical_resolution()
  - test_font_size_fallback_to_base()
  - test_font_weight_conversion_to_int()
  - test_line_height_fallback()
  - test_letter_spacing_fallback()
  - test_terminal_inherits_from_mono()
  - test_tabs_inherits_from_ui()
  - test_category_guarantees_monospace()
  - test_category_guarantees_sans_serif()
  - test_lru_cache_performance()
  - test_cache_clear()
  - test_get_qfont_creates_valid_font()
  - test_get_available_font_case_insensitive()
  - test_get_available_font_none_found()
  - test_get_available_font_generic_fallback()

- [ ] **Write platform tests** (`tests/integration/test_font_fallbacks.py`)
  - test_monospace_fonts_available()
  - test_ui_fonts_available()
  - test_serif_fonts_available()
  - test_platform_specific_fonts()
  - test_font_family_normalization()
  - test_fallback_chain_order()
  - test_missing_fonts_use_generic()
  - test_font_database_integration()
  - test_cross_platform_compatibility()
  - test_font_availability_caching()

- [ ] **Create demo** (`examples/12_font_resolution.py`)
  - Show hierarchical resolution in action
  - Display fallback chains
  - List available vs unavailable fonts
  - Show platform-specific behavior
  - Visual table of resolution results

#### Exit Criteria
- ✅ FontTokenRegistry resolves hierarchically
- ✅ Fallback chains work correctly
- ✅ Platform fonts detected (Windows/Linux/macOS)
- ✅ All 25 resolution tests pass
- ✅ LRU cache improves performance
- ✅ Demo shows resolution working

---

### Phase 3: ThemedWidget Font Integration (Week 2-3)
**Goal**: Automatic font application to widgets
**Duration**: 3-4 days
**Demos**: `examples/13_font_showcase.py`, `examples/14_terminal_fonts.py`

#### Tasks

- [ ] **Add font support to ThemedWidget** (`src/vfwidgets_theme/widgets/base.py`)
  - Add _apply_fonts(theme) method
  - Support "font" bundle property (e.g., "font": "terminal")
  - Support individual properties (fontFamily, fontSize, fontWeight)
  - Add supported_font_properties list
  - Add _apply_line_height(theme) method (override in subclasses)
  - Call _apply_fonts() in on_theme_changed()

- [ ] **Update TerminalWidget** (`widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`)
  - Add font tokens to theme_config
  - Implement font resolution for xterm.js
  - Convert font families to xterm.js format
  - Apply fontSize, lineHeight, letterSpacing
  - Add supported_font_properties list

- [ ] **Create font support matrix** (`docs/font-support-matrix.md` - NEW FILE)
  - Document which widgets support which properties
  - List Qt limitations (line height on UI widgets)
  - Provide workarounds where available

- [ ] **Write integration tests** (`tests/integration/test_themed_fonts.py`)
  - test_terminal_receives_monospace()
  - test_tab_bar_receives_ui_fonts()
  - test_theme_change_updates_fonts()
  - test_font_bundle_property()
  - test_individual_font_properties()
  - test_font_size_float_support()
  - test_letter_spacing_applied()
  - test_line_height_terminal_only()
  - test_line_height_ignored_on_tabs()
  - test_font_cascading_disabled()
  - test_missing_font_uses_fallback()
  - test_widget_font_inheritance()
  - test_qfont_creation_from_token()
  - test_font_weight_conversion()
  - test_supported_font_properties_list()

- [ ] **Create font showcase demo** (`examples/13_font_showcase.py`)
  - Window with samples of each font category
  - Display fonts.mono, fonts.ui, fonts.serif
  - Show font info (family, size, weight)
  - Theme switcher to see live updates
  - Visual comparison of categories

- [ ] **Create terminal fonts demo** (`examples/14_terminal_fonts.py`)
  - TerminalWidget with themed fonts
  - Show monospace font in action
  - Demonstrate line height and letter spacing
  - Theme selector for font changes

#### Exit Criteria
- ✅ ThemedWidget applies fonts automatically
- ✅ Terminal uses monospace fonts from theme
- ✅ Font changes update live
- ✅ All 15 integration tests pass
- ✅ Both demos show working fonts
- ✅ Font support matrix documented

---

### Phase 4: Theme Studio Font Editor (Week 3-4)
**Goal**: UI for editing fonts in Theme Studio
**Duration**: 3-4 days
**Demo**: Full Theme Studio with font editing

#### Tasks

- [ ] **Create FontPropertyEditor widget** (`apps/theme-studio/src/theme_studio/widgets/font_property_editor.py` - NEW FILE)
  - Font family list editor (QListWidget with drag-drop)
  - Add/Remove font family buttons
  - Reorder font families
  - Font size spin box (float support, 1-144pt)
  - Font weight combo box (normal, bold, semibold, etc.)
  - Line height spin box (0.5-3.0)
  - Letter spacing spin box (-5 to 5)
  - Live preview label
  - Font availability indicators (✅/❌)

- [ ] **Add Fonts section to Token Browser** (`apps/theme-studio/src/theme_studio/panels/token_browser.py`)
  - Add "Fonts" top-level section
  - Show hierarchical tokens (categories + overrides)
  - Display fonts.mono, fonts.ui, fonts.serif
  - Display widget-specific fonts (terminal.*, tabs.*, etc.)
  - Show inheritance arrows

- [ ] **Integrate font editor into Theme Studio** (`apps/theme-studio/src/theme_studio/window.py`)
  - Add font preview panel
  - Connect FontPropertyEditor to token selection
  - Implement save/load fonts from theme JSON
  - Update theme on font changes
  - Live preview updates

- [ ] **Write Theme Studio tests** (`apps/theme-studio/tests/test_font_editor.py`)
  - test_font_property_editor_create()
  - test_set_font_family_list()
  - test_add_remove_font_family()
  - test_reorder_font_family()
  - test_font_size_spinner()
  - test_font_weight_combo()
  - test_font_preview_updates()
  - test_availability_indicators()
  - test_save_theme_with_fonts()
  - test_load_theme_with_fonts()

- [ ] **Update Theme Studio documentation** (`docs/theme-studio-font-editor.md` - NEW FILE)
  - User guide for font editing
  - Screenshots of font editor
  - Best practices
  - Troubleshooting

#### Exit Criteria
- ✅ Theme Studio has Fonts section in token browser
- ✅ Can edit all font properties
- ✅ Live preview shows font changes
- ✅ Save/load preserves fonts correctly
- ✅ All 10 Theme Studio tests pass
- ✅ Full demo works in Theme Studio
- ✅ User documentation complete

---

## Testing Summary

**Total Tests Across All Phases**: 65 tests

### Phase 1: 15 tests
- Unit tests for font validation

### Phase 2: 25 tests
- Unit tests for token resolution (15)
- Integration tests for platform fallbacks (10)

### Phase 3: 15 tests
- Integration tests for widget font application

### Phase 4: 10 tests
- UI tests for Theme Studio font editor

---

## Documentation Deliverables

### Phase 1
- Updated fonts-DESIGN.md with implementation status
- CHANGELOG entry for v2.1.0-alpha
- Updated theme JSON schema

### Phase 2
- font-tokens-API.md (API reference for FontTokenRegistry)
- Resolution examples and best practices

### Phase 3
- font-support-matrix.md (widget compatibility table)
- ThemedWidget font usage guide
- Migration guide for existing themes

### Phase 4
- theme-studio-font-editor.md (user guide)
- Updated Theme Studio documentation
- Video walkthrough (optional)

---

## Timeline

- **Phase 1**: 2-3 days
- **Phase 2**: 3-4 days
- **Phase 3**: 3-4 days
- **Phase 4**: 3-4 days

**Total Estimated Time**: 2-3 weeks

---

## Success Criteria for v2.1.0 Release

After all phases complete:

- ✅ Theme system supports fonts (fonts.mono, fonts.ui, fonts.serif)
- ✅ Hierarchical font resolution works
- ✅ ThemedWidget applies fonts automatically
- ✅ Terminal widget uses monospace fonts
- ✅ Theme Studio can edit fonts with live preview
- ✅ All 65 tests passing
- ✅ Cross-platform tested (Windows, Linux, macOS)
- ✅ Documentation complete
- ✅ Migration guide for existing themes
- ✅ Ready for production use

**Release**: VFWidgets Theme System v2.1.0 🎉
