# Testing Default Values and Reset Feature

## How to Test

1. **Launch theme-studio**:
   ```bash
   cd /home/kuja/GitHub/vfwidgets/apps/theme-studio
   python -m src.theme_studio
   ```

2. **Test Color Token Defaults**:
   - Click "Colors" tab
   - Select any color token (e.g., `button.background`)
   - Look at the Token Information section in the inspector panel
   - You should see:
     - **Name**: token name (with ✓ badge if customized)
     - **Value**: current color value (clickable)
     - **Category**: token category
     - **Description**: token description
     - **Default**: default value for current theme type
   - If the current value differs from default:
     - The name shows a ✓ badge
     - The "Reset to Default" button is enabled
   - Click "Reset to Default" to restore the default value

3. **Test Font Token Defaults**:
   - Click "Fonts" tab
   - Select any font token (e.g., `fonts.size`)
   - Look at the Token Information section
   - You should see:
     - **Name**: token name (with ✓ badge if customized)
     - **Category**: font category
     - **Description**: token description
     - **Default**: default value or "(uses hierarchical fallback)"
   - Font editor widget appears below
   - If the current value differs from default:
     - The name shows a ✓ badge
     - The "Reset to Default" button is enabled
   - Click "Reset to Default" to restore the default value

## Expected Behavior

### Default Values:
- **Color tokens**: Show theme-specific defaults (dark vs light)
- **Font tokens**: Show single default value
- **Hierarchical fonts**: Show "(uses hierarchical fallback)" if default is None

### Reset Button:
- **Enabled**: When current value ≠ default value
- **Disabled**: When current value = default value
- **Action**: Restores token to its default value

### Visual Indicators:
- **✓ Badge**: Appears next to token name when value is customized (differs from default)
- No badge: Token uses default value

## Examples

### Color Token Examples:
```
button.background:
  - Dark default: #0e639c
  - Light default: #0078d4

editor.background:
  - Dark default: #1e1e1e
  - Light default: #ffffff
```

### Font Token Examples:
```
fonts.mono:
  - Default: ['Cascadia Code', 'Consolas', 'Courier New', 'monospace']

fonts.size:
  - Default: 13

terminal.fontSize:
  - Default: None (uses hierarchical fallback → fonts.size)
```

## Features Implemented

✅ Default value display for all tokens
✅ Reset to Default button (enabled only when value differs)
✅ Visual indicator (✓ badge) for customized tokens
✅ Theme-aware defaults for color tokens
✅ Hierarchical fallback indication for font tokens
