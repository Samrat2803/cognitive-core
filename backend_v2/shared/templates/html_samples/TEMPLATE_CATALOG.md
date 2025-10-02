# 🎨 HTML Infographic Template Catalog

**Created from memory** - 6 diverse, creative templates for political analysis infographics

---

## 📋 **Quick Overview**

| # | Template Name | Style | Best For | Colors |
|---|---------------|-------|----------|--------|
| 1 | **Modern Gradient** | Glassmorphism, Bold | Sentiment scores, KPIs | Purple gradient |
| 2 | **Minimalist Monochrome** | Typography-focused | Professional reports | Black & white |
| 3 | **Vibrant Cards** | Colorful, Playful | Multi-metric dashboards | Rainbow gradients |
| 4 | **Neon Dark** | Cyberpunk, Tech | Live monitoring, Alerts | Cyan/Magenta |
| 5 | **Clean Corporate** | Professional, Business | Executive reports | Blue/Gray |
| 6 | **Playful Rounded** | Fun, Friendly | Social media, Youth | Warm pastels |

---

## 🎯 **Template Details**

### **1. Modern Gradient Dashboard**
**File**: `template_1_gradient_modern.html`

**Style**:
- Glassmorphism effect (frosted glass)
- Purple-to-violet gradient background
- Backdrop blur
- 4 stat cards in 2x2 grid
- Floating, translucent cards

**Perfect For**:
- Sentiment analysis results
- Real-time KPI dashboards
- Modern, tech-forward presentations

**Visual Feel**: Premium, modern, Apple-like aesthetic

---

### **2. Minimalist Monochrome**
**File**: `template_2_minimalist_mono.html`

**Style**:
- Pure black and white
- Bold vertical accent line
- Huge typography (96px numbers)
- Horizontal stat rows
- Maximum readability

**Perfect For**:
- Executive summaries
- Bias analysis reports
- Print-ready documents
- Professional presentations

**Visual Feel**: Swiss design, editorial, sophisticated

---

### **3. Vibrant Card Layout**
**File**: `template_3_vibrant_cards.html`

**Style**:
- 6 gradient-filled cards (3x2 grid)
- Animated gradient background
- Each card has unique color
- Hover animations (lift & tilt)
- Highlight insight box

**Perfect For**:
- Multi-source analysis
- Comparison metrics
- Social media posts
- Engaging presentations

**Visual Feel**: Energetic, youthful, dynamic

---

### **4. Neon Dark Mode**
**File**: `template_4_neon_dark.html`

**Style**:
- Dark background (#1a1a2e)
- Cyan (#00ffff) and magenta (#ff00ff) neon
- Animated scan line
- Glowing borders and text
- Corner decorations
- Shimmer effects

**Perfect For**:
- Live monitoring dashboards
- Real-time alerts
- Tech/security themes
- "War room" style displays

**Visual Feel**: Cyberpunk, Matrix, high-tech

---

### **5. Clean Corporate**
**File**: `template_5_clean_corporate.html`

**Style**:
- White background
- Blue accent color (#1e3c72)
- Top colored bar
- 4 metric cards
- Chart placeholder area
- Gradient insight section

**Perfect For**:
- Business reports
- Stakeholder presentations
- Policy analysis
- Formal documentation

**Visual Feel**: Professional, trustworthy, business-standard

---

### **6. Playful Rounded**
**File**: `template_6_playful_rounded.html`

**Style**:
- Circular "bubble" cards
- Blob decorations
- Rounded corners everywhere
- Warm peach/orange background
- 6 gradient bubbles (3x2)
- Glossy highlights on bubbles

**Perfect For**:
- Social media engagement
- Youth-focused campaigns
- Friendly, approachable content
- Instagram/TikTok style

**Visual Feel**: Fun, bubbly, friendly, playful

---

## 🔧 **How to Use These Templates**

### **Method 1: Direct HTML Replacement**
```python
# Read template
with open('template_1_gradient_modern.html', 'r') as f:
    html = f.read()

# Replace placeholders
html = html.replace('{{TITLE}}', 'US Climate Policy')
html = html.replace('{{SUBTITLE}}', 'Sentiment Analysis')
html = html.replace('{{STAT1_VALUE}}', '72%')
html = html.replace('{{STAT1_LABEL}}', 'Approval')

# Save or convert to image
with open('output.html', 'w') as f:
    f.write(html)
```

### **Method 2: Convert to PNG/JPG**
```python
# Use Playwright or Selenium
from playwright.sync_api import sync_playwright

def html_to_image(html_file, output_png):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1080})
        page.goto(f'file://{html_file}')
        page.screenshot(path=output_png)
        browser.close()

html_to_image('template_1_gradient_modern.html', 'output.png')
```

### **Method 3: Integrate with Python**
```python
from jinja2 import Template

# Load template
with open('template_1_gradient_modern.html', 'r') as f:
    template = Template(f.read())

# Render with data
html = template.render(
    TITLE='US Climate Policy',
    SUBTITLE='Sentiment Analysis',
    STAT1_VALUE='72%',
    STAT1_LABEL='Approval',
    # ... more data
)
```

---

## 📦 **Template Placeholders**

### **Common Variables (All Templates)**:
- `{{TITLE}}` - Main headline
- `{{SUBTITLE}}` - Secondary text
- `{{FOOTER_TEXT}}` - Bottom attribution
- `{{INSIGHT_TEXT}}` - Key insight paragraph

### **Stat Variables**:
- `{{STAT1_VALUE}}` - First metric value
- `{{STAT1_LABEL}}` - First metric label
- `{{STAT2_VALUE}}` - Second metric value
- `{{STAT2_LABEL}}` - Second metric label
- ... and so on

### **Template-Specific**:
- **Template 5**: `{{DATE}}` - Report date
- **Template 3 & 6**: Up to 6 stats
- **Template 2**: Only 3 stats

---

## 🎨 **Design Philosophy**

Each template was created with a specific **mood** and **use case**:

1. **Modern Gradient** = Premium & Modern
2. **Minimalist Mono** = Professional & Editorial
3. **Vibrant Cards** = Energetic & Engaging
4. **Neon Dark** = Technical & Dramatic
5. **Clean Corporate** = Business & Trust
6. **Playful Rounded** = Fun & Friendly

---

## 📊 **Recommended Template for Each Agent**

| Agent | Best Template | Why |
|-------|---------------|-----|
| **Sentiment Analyzer** | Template 1 (Gradient) | Modern feel for sentiment scores |
| **Bias Detector** | Template 2 (Mono) | Professional, objective appearance |
| **Fact Checker** | Template 5 (Corporate) | Trustworthy, authoritative |
| **Live Monitor** | Template 4 (Neon) | Real-time, alert-focused |
| **Comparative Analysis** | Template 3 (Vibrant) | Multi-metric comparison |
| **Entity Extractor** | Template 6 (Playful) | Relationship visualization |

---

## 🚀 **Next Steps**

### **To Use These Templates**:

1. **Choose your template** based on mood/purpose
2. **Fill in placeholder variables** with your data
3. **Convert to image** using Playwright/Selenium
4. **Use in your agents** as artifacts

### **To Customize Further**:

- Colors: Search and replace hex codes
- Fonts: Change `font-family` in CSS
- Layout: Adjust grid columns/spacing
- Animations: Modify `@keyframes` rules

---

## 📁 **File Structure**

```
templates/html_samples/
├── template_1_gradient_modern.html     (Template)
├── template_2_minimalist_mono.html     (Template)
├── template_3_vibrant_cards.html       (Template)
├── template_4_neon_dark.html           (Template)
├── template_5_clean_corporate.html     (Template)
├── template_6_playful_rounded.html     (Template)
├── DEMO_gradient_modern.html           (With data)
├── DEMO_minimalist_mono.html           (With data)
├── DEMO_neon_dark.html                 (With data)
└── TEMPLATE_CATALOG.md                 (This file)
```

---

## 💡 **Tips**

1. **For social media**: Use templates 1, 3, or 6
2. **For business reports**: Use templates 2 or 5
3. **For live dashboards**: Use template 4
4. **For variety**: Rotate through all 6
5. **For branding**: Pick 2-3 and stick with them

---

## ✅ **All Templates Are**:

- ✅ Fully standalone (no external dependencies)
- ✅ Responsive to 1080x1080 size
- ✅ Ready for screenshot conversion
- ✅ Placeholder-based for easy data insertion
- ✅ CSS animations included
- ✅ Cross-browser compatible

---

**Created**: October 2, 2025  
**Templates**: 6 unique designs  
**Purpose**: Political analysis infographics  
**Format**: HTML + Inline CSS

