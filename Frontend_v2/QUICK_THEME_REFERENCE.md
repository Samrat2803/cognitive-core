# 🎯 Quick Theme Reference - Cheat Sheet

**File:** `Frontend_v2/src/theme.css`

---

## 🚨 Most Common Fixes

### Fix Invisible Links
```css
Line 175: --link-color: #d9f378;           /* Change to brighter color */
Line 176: --link-color-hover: #c5e065;    /* Change hover color */
```

### Fix Invisible Icons
```css
Line 184: --icon-stroke-width: 2;          /* Increase to 3 or 4 */
Line 185: --icon-color-default: rgba(...); /* Make brighter */
```

### Make Text Larger
```css
Line 60: --font-size-base: 0.95rem;        /* Change to 1rem or 1.1rem */
```

### Change Button Size
```css
Line 149: --button-height-md: 40px;        /* Increase to 48px */
```

### More Spacing Between Elements
```css
Line 78: --space-lg: 16px;                 /* Increase to 20px or 24px */
```

### Brighter Background
```css
Line 24: --color-background-darkest: #1c1e20;  /* Change to #2a2a2a */
```

---

## 🎨 Color Variables Quick Access

| Variable | Value | Usage |
|----------|-------|-------|
| `--color-primary` | `#d9f378` | Buttons, links, highlights |
| `--color-secondary` | `#5d535c` | Supporting elements |
| `--color-background-darkest` | `#1c1e20` | Main background |
| `--color-text-primary` | `rgba(255,255,255,0.95)` | Headings |
| `--color-error` | `#ff6b6b` | Stop button, errors |

---

## 📏 Spacing Quick Access

| Variable | Value | Common Use |
|----------|-------|------------|
| `--space-xs` | `4px` | Tiny gaps |
| `--space-sm` | `8px` | Small gaps |
| `--space-md` | `12px` | Default gap |
| `--space-lg` | `16px` | Component padding |
| `--space-xl` | `24px` | Section spacing |

---

## 🔤 Font Size Quick Access

| Variable | Value | Usage |
|----------|-------|-------|
| `--font-size-xs` | `0.75rem` | 12px - Hints, labels |
| `--font-size-sm` | `0.875rem` | 14px - Secondary text |
| `--font-size-base` | `0.95rem` | 15.2px - Body text |
| `--font-size-xl` | `1.25rem` | 20px - Headings |

---

## ⚡ How to Test Changes

1. **Edit:** Open `Frontend_v2/src/theme.css`
2. **Change:** Modify any variable (e.g., `--color-primary: #ff0000;`)
3. **Save:** Press Ctrl+S / Cmd+S
4. **Check:** Browser auto-reloads (if dev server running)
5. **Verify:** Look at the UI to see changes

---

## 🧪 Test in Browser Console

```javascript
// Check if theme loaded
getComputedStyle(document.documentElement).getPropertyValue('--color-primary')

// Should return: " #d9f378"
```

---

## 📍 Where Each Variable Is Used

### `--color-primary` used in:
- Send button background (`MessageInput.css`)
- Header title color (`Header.css`)
- User message icon background (`Message.css`)
- All hyperlinks (`Markdown.css`)
- Logo icon (`Header.css`)

### `--font-primary` used in:
- All text elements across the app
- Message textarea (`MessageInput.css`)
- Header title (`Header.css`)

### `--space-lg` used in:
- Message padding (`Message.css`)
- Input container padding (`MessageInput.css`)
- Header padding (`Header.css`)

---

## 💡 Pro Tips

1. **Start Small:** Change one thing, test, then change another
2. **Use Browser Inspect:** Right-click → Inspect to see which variable affects what
3. **Keep a Backup:** Copy `theme.css` before making big changes
4. **Test Contrast:** Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

## 🆘 Emergency Reset

If something breaks, restore defaults:

```bash
cd Frontend_v2
git checkout src/theme.css
```

Or manually change back to these safe defaults:
- `--color-primary: #d9f378`
- `--font-size-base: 0.95rem`
- `--space-lg: 16px`
- `--button-height-md: 40px`

---

**Quick Access Line Numbers in theme.css:**
- Colors: Lines 19-43
- Fonts: Lines 54-72
- Spacing: Lines 75-82
- Buttons: Lines 147-153
- Links: Lines 175-178
- Icons: Lines 184-187

---

**Last Updated:** October 2, 2025

