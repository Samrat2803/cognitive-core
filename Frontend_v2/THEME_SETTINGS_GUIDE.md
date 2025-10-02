# 🎨 Theme Settings Guide - Political Analyst Workbench

**File: Frontend_v2/THEME_SETTINGS_GUIDE.md**

This guide explains all the UI/UX parameters in the centralized theme system and how to modify them.

---

## 📍 Location of Settings

**Main Theme File:** `src/theme.css`

All design tokens are defined as CSS custom properties (variables) in this single file. Changes here automatically propagate throughout the entire application.

---

## 🎨 Color Palette (Aistra Brand)

### Primary Colors
```css
--color-primary: #d9f378          /* Main brand color - buttons, highlights */
--color-primary-hover: #c5e065    /* Hover state */
--color-primary-active: #b0cc52   /* Active/pressed state */
```

**What this controls:**
- Send button background
- Primary action buttons
- Hyperlinks
- Highlighted text
- Logo color
- Focus indicators

**To change:** Modify the hex codes in `theme.css` lines 19-21

---

### Secondary Colors
```css
--color-secondary: #5d535c        /* Supporting UI elements */
--color-secondary-hover: #6d636c  /* Hover state */
--color-secondary-active: #4d434c /* Active state */
```

**What this controls:**
- Assistant message icon backgrounds
- Secondary buttons
- Supporting UI elements

---

### Background Colors
```css
--color-background-darkest: #1c1e20  /* Main app background */
--color-background-dark: #2a2a2a     /* Input fields, elevated surfaces */
--color-background-medium: #333333   /* Cards, panels */
--color-background-light: #444444    /* Hover states */
```

**What this controls:**
- **darkest:** Main application background
- **dark:** Message input wrapper, elevated panels
- **medium:** Borders, separators
- **light:** Hover effects on buttons/cards

---

### Text Colors
```css
--color-text-primary: rgba(255, 255, 255, 0.95)    /* Headings */
--color-text-secondary: rgba(255, 255, 255, 0.85)  /* Body text */
--color-text-tertiary: rgba(255, 255, 255, 0.6)    /* Subtle text */
--color-text-muted: rgba(255, 255, 255, 0.4)       /* Hints, disabled */
```

**What this controls:**
- Text hierarchy throughout the app
- Icon colors
- Placeholder text

**Tip:** Adjust opacity values (0.0 to 1.0) to change contrast

---

### Border Colors
```css
--color-border-default: #333333
--color-border-hover: #444444
--color-border-active: #d9f378
```

**What this controls:**
- Input field borders
- Card outlines
- Separator lines
- Focus rings

---

### Status Colors
```css
--color-success: #5af78e  /* Success indicators */
--color-error: #ff6b6b    /* Errors, stop button */
--color-warning: #f3f99d  /* Warnings */
--color-info: #57c7ff     /* Info messages */
```

---

## 🔤 Typography

### Font Families
```css
--font-primary: 'Roboto Flex', -apple-system, ...
--font-mono: 'SF Mono', 'Monaco', ...
```

**What this controls:**
- All text in the application uses Roboto Flex
- Code blocks use monospace fonts

**To change font:** 
1. Update the font name in `theme.css`
2. Add Google Font link in `index.html` (see below)

---

### Font Sizes
```css
--font-size-xs: 0.75rem      /* 12px - Labels, badges */
--font-size-sm: 0.875rem     /* 14px - Secondary text */
--font-size-base: 0.95rem    /* 15.2px - Body text */
--font-size-md: 1rem         /* 16px - Default */
--font-size-lg: 1.125rem     /* 18px - Large text */
--font-size-xl: 1.25rem      /* 20px - Section headings */
--font-size-2xl: 1.5rem      /* 24px - Page titles */
--font-size-3xl: 1.75rem     /* 28px - Hero text */
```

**Usage Guide:**
- **xs:** Keyboard hints, timestamps, small labels
- **sm:** Table text, secondary info
- **base:** Main message text, body copy
- **xl:** Header title
- **2xl:** Modal titles

---

### Font Weights
```css
--font-weight-normal: 400    /* Regular text */
--font-weight-medium: 500    /* Slightly emphasized */
--font-weight-semibold: 600  /* Headings */
--font-weight-bold: 700      /* Strong emphasis */
```

---

## 📏 Spacing System (8px base grid)

```css
--space-xs: 4px
--space-sm: 8px
--space-md: 12px
--space-lg: 16px      /* Most common - message padding */
--space-xl: 24px
--space-2xl: 32px
--space-3xl: 48px
--space-4xl: 64px
```

**What this controls:**
- Padding inside components
- Gaps between elements
- Margins between sections

---

## 🔲 Border Radius

```css
--radius-sm: 4px      /* Small elements */
--radius-md: 6px      /* Default */
--radius-lg: 8px      /* Buttons, cards */
--radius-xl: 12px     /* Input fields, panels */
--radius-full: 9999px /* Circular buttons */
```

**To make UI more rounded:** Increase these values  
**To make UI more sharp:** Decrease these values

---

## 🖱️ Button Configurations

```css
--button-height-sm: 32px
--button-height-md: 40px      /* Standard button height */
--button-height-lg: 48px
--button-padding-x: 16px
--button-padding-y: 10px
```

---

## 🔗 Hyperlink Fixes

```css
--link-color: var(--color-primary)              /* #d9f378 */
--link-color-hover: var(--color-primary-hover)  /* #c5e065 */
--link-underline: none
--link-underline-hover: 1px solid var(--color-primary)
```

**Problem Fixed:** Links now use the bright Aistra yellow-green color (#d9f378) which is highly visible on dark backgrounds.

**To change link style:**
- `--link-underline: underline` → Always show underline
- `--link-underline: none` → No underline by default

---

## 🎯 Icon Visibility Fixes

```css
--icon-stroke-width: 2
--icon-color-default: var(--color-text-secondary)
--icon-color-hover: var(--color-text-primary)
--icon-color-primary: var(--color-primary)
```

**Problem Fixed:** 
- Icons now have proper stroke width (2px)
- Colors inherit from text colors
- SVG strokes are explicitly defined

---

## ⚡ Transitions

```css
--transition-fast: 0.15s ease
--transition-normal: 0.2s ease      /* Default */
--transition-slow: 0.3s ease
--transition-slowest: 0.5s ease
```

**To make UI feel snappier:** Use `--transition-fast`  
**To make UI feel smoother:** Use `--transition-slow`

---

## 📱 Layout Dimensions

```css
--header-height: 64px
--sidebar-width: 280px
--panel-min-width: 320px
--content-max-width: 1200px
```

---

## 🎭 Z-Index (Stacking Order)

```css
--z-dropdown: 1000
--z-sticky: 1020
--z-fixed: 1030
--z-modal-backdrop: 1040
--z-modal: 1050
--z-popover: 1060
--z-tooltip: 1070
```

**Higher numbers appear on top of lower numbers**

---

## 🌓 Theme Switching

The file includes both dark and light themes:

```css
[data-theme='dark'] { /* Dark theme variables */ }
[data-theme='light'] { /* Light theme variables */ }
```

**To switch theme:** Add `data-theme="light"` attribute to the `<html>` or `<body>` element.

---

## 🛠️ How to Apply Changes

### Step 1: Edit the Theme File
```bash
# Open the theme file
nano Frontend_v2/src/theme.css
# or use your preferred editor
```

### Step 2: Modify Variables
Change any CSS variable value:
```css
/* Before */
--color-primary: #d9f378;

/* After - Make it more blue */
--color-primary: #78d9f3;
```

### Step 3: Save & Reload
Changes apply immediately during development (hot reload).

---

## 🔧 Common Fixes

### Fix 1: Buttons Look Wrong
**Location:** Lines 147-153 in `theme.css`
```css
--button-height-md: 40px      /* Change height */
--button-padding-x: 16px      /* Change horizontal padding */
```

### Fix 2: Text Too Small/Large
**Location:** Lines 58-65 in `theme.css`
```css
--font-size-base: 0.95rem     /* Increase to 1rem or 1.1rem */
```

### Fix 3: Links Not Visible
**Location:** Lines 175-178 in `theme.css`
```css
--link-color: #ff0000;        /* Try bright red to test */
```

### Fix 4: Icons Not Showing
**Location:** Lines 184-187 in `theme.css`
```css
--icon-stroke-width: 3;       /* Increase for thicker icons */
--icon-color-default: #ffffff; /* Try pure white */
```

### Fix 5: Make UI More Colorful
Change background to less dark:
```css
--color-background-darkest: #2a2a2a;  /* Lighter than #1c1e20 */
```

### Fix 6: Spacing Too Tight/Loose
**Location:** Lines 75-82 in `theme.css`
```css
--space-lg: 24px;     /* Increase from 16px for more breathing room */
```

---

## 📋 Testing Your Changes

### Visual Checklist:
- [ ] Hyperlinks are visible and correct color
- [ ] Button icons display properly
- [ ] Text is readable (good contrast)
- [ ] Hover states work on all interactive elements
- [ ] Focus indicators visible when using keyboard
- [ ] Scrollbars visible but not intrusive
- [ ] Consistent spacing throughout

### Browser Console Check:
```javascript
// Test if variables are loaded
getComputedStyle(document.documentElement).getPropertyValue('--color-primary')
// Should return: " #d9f378"
```

---

## 🎨 Design Token Naming Convention

```
--[category]-[property]-[modifier]

Examples:
--color-text-primary
--space-lg
--button-height-md
--transition-normal
```

---

## 📚 Files That Use These Variables

All CSS files now reference `theme.css`:
- `App.css`
- `MessageInput.css`
- `Message.css`
- `Header.css`
- `Markdown.css`
- `ChatPanel.css`
- `ExecutionGraph.css`
- And all other component CSS files

---

## 💡 Pro Tips

1. **Test one change at a time** - Easier to identify what broke
2. **Use browser DevTools** - Inspect elements to see which variables they use
3. **Keep contrast ratios accessible** - Use tools like [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
4. **Document custom changes** - Add comments in `theme.css` if you modify values
5. **Create backups** - Copy `theme.css` before making major changes

---

## 🔍 Debugging Variables

### In Browser DevTools:
1. Right-click any element → Inspect
2. Look for `Computed` tab
3. Search for "var(--" to see all CSS variables

### In VS Code:
1. Install "CSS Variable Autocomplete" extension
2. Hover over any `var(--variable-name)` to see its value

---

## 📞 Need Help?

If something doesn't work:
1. Check browser console for CSS errors
2. Verify `theme.css` is imported in `main.tsx`
3. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
4. Check if the variable name is spelled correctly

---

**Last Updated:** October 2, 2025  
**Version:** 1.0  
**Maintained by:** UI/UX Team

