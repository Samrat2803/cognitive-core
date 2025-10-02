# Situation Report (SitRep) Generator Agent

## 🎯 Purpose

Generate **daily or weekly situation reports** (SitReps) that provide timely, concise updates on the political climate for policymakers, executives, investors, and diplomats.

**SitReps answer:** "What happened in the last 24 hours / 7 days that I need to know?"

---

## 📦 What This Agent Does

**Input:**
- Time period (daily/weekly)
- Geographic focus (optional: specific region/country)
- Topic focus (optional: elections, diplomacy, conflicts, etc.)

**Output:**
- **Executive Summary** (3-4 sentences, most important developments)
- **Key Developments** (5-10 major events with bullets)
- **Regional Breakdown** (grouped by region)
- **Trending Topics** (what's emerging)
- **Watch List** (what to monitor next)
- **Artifacts:** PDF report, HTML dashboard, email-ready summary

---

## 🏗️ Architecture

### Workflow
```
START → Retrieve Events (from Live Monitor) → Filter by Region/Topic → 
Priority Ranking → Grouping & Clustering → Executive Summary Generation → 
Regional Breakdown → Trending Analysis → Watch List → 
Artifact Generation (PDF/HTML) → END
```

### Dependencies
- **Live Political Monitor** (consumes event stream)
- **Event Storage** (MongoDB)

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner
2. **`state.py`** - State schema
3. **`config.py`** - SitRep formatting, templates
4. **`graph.py`** - LangGraph workflow
5. **`nodes/event_retriever.py`** - Pull events from Live Monitor storage
6. **`nodes/priority_ranker.py`** - Rank events by importance
7. **`nodes/event_grouper.py`** - Group by region/topic
8. **`nodes/executive_summarizer.py`** - Generate executive summary
9. **`nodes/section_generator.py`** - Generate each report section
10. **`nodes/watch_list_generator.py`** - Identify what to monitor next
11. **`nodes/artifact_generator.py`** - Create PDF/HTML/email versions
12. **`templates/` - Report templates (HTML/PDF)
13. **`tests/test_agent.py`**

---

## 📝 SitRep Structure

### Standard Daily SitRep Format

```markdown
# POLITICAL SITUATION REPORT
## [Date Range]

---

### EXECUTIVE SUMMARY
[3-4 sentences highlighting the most critical developments]

---

### KEY DEVELOPMENTS

#### 🔴 URGENT (Significance: 12-15)
- **[Region]** Event title
  - Impact: Who/what is affected
  - Status: Ongoing / Resolved / Escalating
  - Next: What to watch for

#### 🟠 HIGH PRIORITY (Significance: 9-11)
- **[Region]** Event title
  - Brief description
  - Key players involved

#### 🟡 NOTABLE (Significance: 6-8)
- **[Region]** Event title (brief)

---

### REGIONAL BREAKDOWN

#### United States
- Legislative: [Key bills, votes]
- Executive: [Policy announcements]
- Elections: [Campaign developments]

#### Europe
- [Events grouped by significance]

#### Middle East
- [Events grouped by significance]

[... other regions ...]

---

### TRENDING TOPICS
1. **[Topic Name]** - [Why it's trending, # of related events]
2. **[Topic Name]** - [Brief context]

---

### WATCH LIST - Next 24-48 Hours
- [ ] **[Event/Development]** - Why it matters, when expected
- [ ] **[Upcoming vote/meeting]** - Significance
- [ ] **[Developing situation]** - Current status, what could happen

---

### SOURCES & METHODOLOGY
- Events tracked: [N] from [M] sources
- Time period: [Start] to [End]
- Credibility threshold: [X]
- Last updated: [Timestamp]
```

---

## 🔑 Key Node: Executive Summarizer (`nodes/executive_summarizer.py`)

```python
"""
Generate executive summary for SitRep
"""

from typing import List, Dict, Any
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

async def generate_executive_summary(
    high_priority_events: List[Dict],
    trending_topics: List[str],
    time_period: str
) -> str:
    """
    Create 3-4 sentence executive summary
    
    Must answer:
    - What were the most significant developments?
    - What's the overall trend/pattern?
    - What's the strategic implication?
    """
    
    # Prepare context
    top_events = "\n".join([
        f"- [{e['regions'][0]}] {e['title']} (score: {e['significance_score']})"
        for e in high_priority_events[:10]
    ])
    
    prompt = f"""You are writing an executive summary for a political situation report covering {time_period}.

TOP DEVELOPMENTS:
{top_events}

TRENDING TOPICS: {', '.join(trending_topics[:5])}

Write a 3-4 sentence executive summary that:
1. Highlights the most critical development (first sentence)
2. Identifies the overarching pattern or theme (second sentence)
3. Notes strategic implications or what decision-makers should focus on (third sentence)
4. Optional: Flags any rapidly developing situations (fourth sentence)

Style: Direct, factual, no speculation. Written for senior policymakers/executives.
No phrases like "In conclusion" or "This report covers". Start with the most important fact.

Return JSON: {{"summary": "text here"}}"""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return result["summary"]
```

---

## 🎨 Key Node: Artifact Generator (`nodes/artifact_generator.py`)

```python
"""
Generate SitRep artifacts (PDF, HTML, Email)
"""

from typing import Dict, Any
import os
from datetime import datetime
from jinja2 import Template
import pdfkit  # For PDF generation

async def generate_sitrep_artifacts(
    sitrep_data: Dict[str, Any],
    output_dir: str = "artifacts"
) -> Dict[str, str]:
    """
    Generate multiple artifact formats:
    - HTML (interactive, for web)
    - PDF (printable, for distribution)
    - TXT (email-ready plaintext)
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts = {}
    
    # 1. HTML Version (Interactive Dashboard)
    html_template = load_html_template()
    html_content = html_template.render(
        sitrep=sitrep_data,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    html_path = os.path.join(output_dir, f"sitrep_{timestamp}.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    artifacts["html"] = html_path
    
    # 2. PDF Version (Printable)
    pdf_path = os.path.join(output_dir, f"sitrep_{timestamp}.pdf")
    pdfkit.from_string(html_content, pdf_path)
    artifacts["pdf"] = pdf_path
    
    # 3. Plain Text Version (Email-ready)
    txt_content = format_as_plaintext(sitrep_data)
    txt_path = os.path.join(output_dir, f"sitrep_{timestamp}.txt")
    with open(txt_path, 'w') as f:
        f.write(txt_content)
    artifacts["txt"] = txt_path
    
    # 4. JSON Version (Machine-readable)
    json_path = os.path.join(output_dir, f"sitrep_{timestamp}.json")
    import json
    with open(json_path, 'w') as f:
        json.dump(sitrep_data, f, indent=2)
    artifacts["json"] = json_path
    
    return artifacts


def load_html_template() -> Template:
    """Load HTML template with Aistra styling"""
    
    template_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Political Situation Report - {{ sitrep.date_range }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Roboto Flex', Arial, sans-serif;
            background: #1c1e20;
            color: #333333;
            line-height: 1.6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
        }
        header {
            border-bottom: 4px solid #d9f378;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: #1c1e20;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .date-range {
            color: #5d535c;
            font-size: 18px;
        }
        .executive-summary {
            background: #d9f378;
            padding: 20px;
            margin: 30px 0;
            border-left: 5px solid #5d535c;
        }
        .executive-summary h2 {
            color: #1c1e20;
            margin-bottom: 10px;
        }
        .section {
            margin: 30px 0;
        }
        .section h2 {
            color: #1c1e20;
            border-bottom: 2px solid #5d535c;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .event {
            margin: 15px 0;
            padding-left: 20px;
        }
        .event-title {
            font-weight: bold;
            color: #333333;
        }
        .event-meta {
            color: #5d535c;
            font-size: 14px;
        }
        .priority-urgent { border-left: 4px solid #e74c3c; }
        .priority-high { border-left: 4px solid #f39c12; }
        .priority-notable { border-left: 4px solid #3498db; }
        .watch-list {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #d9f378;
        }
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #5d535c;
            color: #5d535c;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>POLITICAL SITUATION REPORT</h1>
            <div class="date-range">{{ sitrep.date_range }}</div>
        </header>
        
        <div class="executive-summary">
            <h2>EXECUTIVE SUMMARY</h2>
            <p>{{ sitrep.executive_summary }}</p>
        </div>
        
        <div class="section">
            <h2>KEY DEVELOPMENTS</h2>
            
            {% if sitrep.urgent_events %}
            <h3 style="color: #e74c3c;">🔴 URGENT</h3>
            {% for event in sitrep.urgent_events %}
            <div class="event priority-urgent">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-meta">{{ event.regions|join(", ") }} | Score: {{ event.significance_score }}</div>
                <p>{{ event.summary }}</p>
            </div>
            {% endfor %}
            {% endif %}
            
            {% if sitrep.high_priority_events %}
            <h3 style="color: #f39c12;">🟠 HIGH PRIORITY</h3>
            {% for event in sitrep.high_priority_events %}
            <div class="event priority-high">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-meta">{{ event.regions|join(", ") }}</div>
                <p>{{ event.summary }}</p>
            </div>
            {% endfor %}
            {% endif %}
        </div>
        
        <div class="section">
            <h2>REGIONAL BREAKDOWN</h2>
            {% for region, events in sitrep.regional_breakdown.items() %}
            <h3>{{ region }}</h3>
            <ul>
            {% for event in events %}
                <li><strong>{{ event.title }}</strong> - {{ event.summary[:100] }}...</li>
            {% endfor %}
            </ul>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>TRENDING TOPICS</h2>
            <ul>
            {% for topic in sitrep.trending_topics %}
                <li><strong>{{ topic }}</strong></li>
            {% endfor %}
            </ul>
        </div>
        
        <div class="watch-list">
            <h2>WATCH LIST - Next 24-48 Hours</h2>
            <ul>
            {% for item in sitrep.watch_list %}
                <li>{{ item }}</li>
            {% endfor %}
            </ul>
        </div>
        
        <footer>
            <p>Sources: {{ sitrep.source_count }} events tracked | Generated: {{ generated_at }}</p>
            <p>Powered by Political Analyst Workbench</p>
        </footer>
    </div>
</body>
</html>
    """
    
    return Template(template_html)
```

---

## 📊 Example Output

### Query:
```
"Generate daily SitRep for Middle East"
```

### Response:
```json
{
  "type": "sitrep",
  "period": "daily",
  "date_range": "October 1-2, 2025",
  "region_focus": "Middle East",
  "executive_summary": "Diplomatic tensions escalated following unexpected sanctions announcement, while ongoing negotiations showed signs of progress. Regional actors remain cautiously engaged despite heightened rhetoric. Situation requires close monitoring over next 48 hours as key summit approaches.",
  "urgent_events": [
    {
      "title": "Major Sanctions Announced",
      "regions": ["Middle East", "United States"],
      "significance_score": 13,
      "summary": "...",
      "impact": "Economic pressure, potential retaliation",
      "status": "Developing"
    }
  ],
  "high_priority_events": [...],
  "notable_events": [...],
  "regional_breakdown": {
    "Middle East": [...],
    "North Africa": [...]
  },
  "trending_topics": [
    "sanctions",
    "diplomatic negotiations",
    "energy policy"
  ],
  "watch_list": [
    "Summit scheduled for October 5 - outcome could shift regional dynamics",
    "Parliament vote on defense budget expected this week",
    "Ongoing protests - monitor for escalation"
  ],
  "artifacts": {
    "html": "artifacts/sitrep_20251002_143000.html",
    "pdf": "artifacts/sitrep_20251002_143000.pdf",
    "txt": "artifacts/sitrep_20251002_143000.txt"
  },
  "metadata": {
    "events_analyzed": 127,
    "high_priority_count": 8,
    "regions_covered": 3,
    "generated_at": "2025-10-02T14:30:00Z"
  }
}
```

---

## 🔌 Integration

### Depends On:
- **Live Political Monitor** (event stream source)
- **Event Storage** (MongoDB)

### Used By:
- **Master Agent** (user requests SitRep)
- **Scheduled Jobs** (automated daily/weekly reports)

### API Endpoint:
```python
# In app.py
@app.post("/api/generate-sitrep")
async def generate_sitrep(
    period: str = "daily",  # daily, weekly, custom
    region: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Generate situation report"""
    # Call SitRep agent
    ...
```

---

## 🧪 Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/sitrep_generator

# Standalone test (requires Live Monitor data)
python main.py --period daily --region "Middle East"

# Weekly report
python main.py --period weekly --region "Global"

# Custom date range
python main.py --start "2025-10-01" --end "2025-10-02"
```

---

## 📦 Required Packages

```bash
uv pip install jinja2         # Template rendering
uv pip install pdfkit         # PDF generation
uv pip install pymongo        # MongoDB access (already installed)

# System dependency for pdfkit
# macOS: brew install wkhtmltopdf
# Linux: apt-get install wkhtmltopdf
```

---

## ⚙️ Automation

### Scheduled Daily SitReps

```python
# schedule_sitreps.py
import schedule
import asyncio
from sitrep_generator.graph import create_sitrep_graph

async def generate_daily_sitrep():
    """Automated daily SitRep at 7 AM"""
    graph = create_sitrep_graph()
    result = await graph.ainvoke({
        "period": "daily",
        "region": None,  # All regions
        # ...
    })
    # Email to distribution list
    send_email(result["artifacts"]["pdf"])

# Schedule
schedule.every().day.at("07:00").do(lambda: asyncio.run(generate_daily_sitrep()))

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## ✅ Definition of Done

- [ ] Retrieves events from Live Monitor storage
- [ ] Generates executive summary (3-4 sentences)
- [ ] Groups events by priority and region
- [ ] Identifies trending topics
- [ ] Creates watch list for next 24-48 hours
- [ ] Generates HTML artifact (styled with Aistra palette)
- [ ] Generates PDF artifact (printable)
- [ ] Generates plain text (email-ready)
- [ ] Works standalone (with mock Live Monitor data)
- [ ] Response time <10s
- [ ] Tests passing

**Effort:** 4-5 days (2 developers)  
**Impact:** ⭐⭐⭐⭐⭐ **CORE DELIVERABLE** - What political analysts actually produce  
**Priority:** 🔴 HIGH - Build after Live Monitor

