# 📥 How to Use Professional Templates from Popular Platforms

**System**: Template Overlay System  
**Purpose**: Use actual templates from Venngage, Canva, Freepik, etc.  
**No coding required**: Just download and place templates!

---

## 🎯 **How It Works**

```
Step 1: Download professional templates (PNG/JPG)
        ↓
Step 2: Place in templates/downloaded/ folder
        ↓
Step 3: System overlays your data on the template
        ↓
Step 4: Get professional infographics!
```

---

## 📥 **Where to Download Templates**

### **1. Freepik** (Best - Direct Downloads!)
**URL**: https://www.freepik.com/free-photos-vectors/infographic

**Pros**:
- ✅ Direct PNG/JPG downloads
- ✅ High resolution (up to 5000px)
- ✅ Free with attribution
- ✅ Huge variety

**How to Download**:
1. Go to Freepik
2. Search "infographic template" or "political infographic"
3. Click on a template
4. Click "Free Download" → Select "Premium PNG" (free account)
5. Save to `backend_v2/shared/templates/downloaded/`

**Recommended Searches**:
- "statistical infographic template"
- "dashboard infographic"
- "comparison infographic"
- "timeline infographic"
- "data visualization template"

---

### **2. Venngage** (Online Editor - Export as Image)
**URL**: https://venngage.com/templates/infographics

**Pros**:
- ✅ Professional designs
- ✅ Statistical templates
- ✅ Can export as PNG

**How to Use**:
1. Sign up (free account)
2. Choose a template
3. Customize with placeholder text
4. Export as PNG (free plan allows this)
5. Save to templates folder

---

### **3. Canva** (Online Editor - Export)
**URL**: https://www.canva.com/templates/search/infographics/

**Pros**:
- ✅ Most popular platform
- ✅ Modern designs
- ✅ Easy export

**How to Use**:
1. Sign up (free)
2. Search "infographic" or "dashboard"
3. Click "Customize this template"
4. Download as PNG (Free: 1280x720 or Pro: 4K)
5. Save to templates folder

---

### **4. Pngtree** (Direct Downloads)
**URL**: https://pngtree.com/free-infographic-templates

**Pros**:
- ✅ Direct PNG downloads
- ✅ Free templates available
- ✅ Commercial use allowed

---

### **5. Vecteezy** (Vector Downloads)
**URL**: https://www.vecteezy.com/free-vector/infographic

**Pros**:
- ✅ High quality vectors
- ✅ Can convert to PNG
- ✅ Free license options

---

## 📂 **Folder Structure**

```
backend_v2/shared/
├── templates/
│   ├── downloaded/              📥 PUT TEMPLATES HERE
│   │   ├── dashboard_1.png
│   │   ├── comparison_template.jpg
│   │   ├── timeline_modern.png
│   │   └── stats_infographic.png
│   └── samples/                 📁 Example templates
└── artifacts/                   📁 Output folder
```

---

## 🎨 **Recommended Templates to Download**

### **For Political Analysis**:

1. **Dashboard Templates**
   - Search: "statistical dashboard infographic"
   - Use for: Sentiment scores, poll results

2. **Comparison Templates**
   - Search: "vs comparison infographic"
   - Use for: Policy comparison, party platforms

3. **Timeline Templates**
   - Search: "timeline infographic horizontal"
   - Use for: Policy evolution, event sequences

4. **Statistics Templates**
   - Search: "data infographic template"
   - Use for: Survey results, demographics

5. **Map Templates**
   - Search: "world map infographic"
   - Use for: Geographic sentiment analysis

---

## 💻 **How to Use the System**

### **Step 1: Download Templates**
```bash
# Download 3-5 templates from Freepik/Canva
# Save them to: backend_v2/shared/templates/downloaded/
```

### **Step 2: Run the System**
```bash
cd backend_v2/shared
source ../.venv/bin/activate
python template_overlay_system.py
```

### **Step 3: System Shows You Template Info**
```
✅ Found 3 template(s):
   1. dashboard_template.png
   2. comparison_template.png
   3. timeline_template.png

📊 Analyzing template: dashboard_template.png

Template loaded: 1080x1920

Common positions:
- Top left: (50, 50)
- Top center: (540, 50)
- Center: (540, 960)
- Bottom: (540, 1820)
```

### **Step 4: Apply Your Data**
```python
from template_overlay_system import TemplateOverlaySystem

system = TemplateOverlaySystem()

# Your data
overlay_config = {
    "zones": [
        {
            "type": "text",
            "position": (100, 100),
            "text": "US Climate Policy Sentiment",
            "font_size": 60,
            "color": "#FFFFFF"
        },
        {
            "type": "number",
            "position": (400, 500),
            "value": "75%",
            "font_size": 100,
            "color": "#00FF00"
        },
        {
            "type": "label",
            "position": (400, 620),
            "label": "Approval Rating",
            "font_size": 36,
            "color": "#FFFFFF"
        }
    ]
}

# Apply to template
result = system.apply_data_to_template(
    "templates/downloaded/dashboard_template.png",
    overlay_config
)

print(f"Created: {result['path']}")
```

---

## 🎯 **Quick Start (5 Minutes)**

1. **Go to Freepik**: https://www.freepik.com/search?format=search&query=infographic%20template
2. **Download 3 templates** (PNG format):
   - One dashboard/statistics template
   - One comparison template  
   - One timeline template
3. **Save them** to: `backend_v2/shared/templates/downloaded/`
4. **Run test**:
   ```bash
   cd backend_v2/shared
   python template_overlay_system.py
   ```
5. **Done!** System will overlay sample data on your templates

---

## 📋 **Template Overlay Zones**

### **Available Zone Types**:

| Type | Purpose | Required Fields |
|------|---------|----------------|
| `text` | Titles, paragraphs | position, text, font_size, color |
| `number` | Large stats (75%, 1M) | position, value, font_size, color |
| `label` | Small labels | position, label, font_size, color |
| `box` | Colored boxes | position, size, color |

### **Color Formats**:
- Hex: `"#FFFFFF"` (white)
- Hex: `"#00FF00"` (green)
- Hex: `"#FF0000"` (red)

### **Position Guide**:
```
Template: 1080x1920 (Instagram Story)

Top Left        Top Center         Top Right
(50, 50)        (540, 50)          (1030, 50)

Mid Left        Center             Mid Right
(50, 960)       (540, 960)         (1030, 960)

Bottom Left     Bottom Center      Bottom Right
(50, 1870)      (540, 1870)        (1030, 1870)
```

---

## 🔧 **Integration with Agents**

### **Use in Agent Visualizer**:
```python
# In your agent's visualizer node
from template_overlay_system import TemplateOverlaySystem

def visualize(state):
    system = TemplateOverlaySystem()
    
    # Your agent data
    sentiment_score = state["sentiment_scores"]["US"]
    
    # Apply to professional template
    config = {
        "zones": [
            {"type": "text", "position": (100, 100), 
             "text": "US Sentiment Analysis", "font_size": 60, "color": "#FFFFFF"},
            {"type": "number", "position": (400, 500), 
             "value": f"{sentiment_score:.1%}", "font_size": 100, "color": "#00FF00"}
        ]
    }
    
    result = system.apply_data_to_template(
        "templates/downloaded/dashboard_template.png",
        config
    )
    
    return {"artifacts": [result]}
```

---

## ⚡ **Advantages of This Approach**

✅ **Use Professional Designs** - From top platforms  
✅ **No Design Skills Needed** - Just download and use  
✅ **Consistent Quality** - Professional templates  
✅ **Fast** - No need to design from scratch  
✅ **Flexible** - Use any template you download  
✅ **No Color Theme Limits** - Each template has its own style

---

## 🎯 **Recommended Workflow**

### **For Each Agent Type**:

1. **Sentiment Analyzer**
   - Download: Dashboard template with large numbers
   - Use for: Displaying sentiment scores

2. **Bias Detector**
   - Download: Comparison template (split screen)
   - Use for: Source comparison

3. **Fact Checker**
   - Download: Timeline template
   - Use for: Verification process

4. **Entity Extractor**
   - Download: Network/connection template
   - Use for: Relationship maps

---

## 📞 **Support**

**No templates found?**
- Make sure files are PNG or JPG
- Place in: `backend_v2/shared/templates/downloaded/`
- Check file permissions

**Template not working?**
- Verify image is not corrupted
- Check file size (recommended < 5MB)
- Use PNG format for best results

**Need different positions?**
- Run system analyzer first
- Use template dimensions to calculate positions
- Test with sample data

---

## 🎉 **Get Started Now!**

1. Open Freepik: https://www.freepik.com/search?query=infographic%20template
2. Download 3 templates
3. Save to: `backend_v2/shared/templates/downloaded/`
4. Run: `python template_overlay_system.py`

**That's it!** You're now using professional templates from popular platforms! 🚀

---

**System**: ✅ Ready to use  
**Templates Needed**: 📥 Download from platforms  
**Time to Setup**: ⏱️ 5 minutes

