# Policy / Issue Brief Generator Agent

## 🎯 Purpose

Generate **analytical policy/issue briefs** that explain what a development means—not just what happened. These briefs provide deep context, implications, and actionable intelligence for decision-makers.

**Policy Briefs answer:** "What does this mean? Why does it matter? What should we do?"

---

## 📦 What This Agent Does

**Input:**
- Specific event, policy, or issue to analyze
- Optional: Stakeholder perspective (government, business, NGO, etc.)
- Optional: Decision deadline/timeframe

**Output:**
- **Executive Summary** (The key takeaway in 2-3 sentences)
- **Background** (Historical context, how we got here)
- **Key Players** (Who's involved, their interests/motivations)
- **Analysis** (What this means, implications)
- **Scenarios** (Possible outcomes: best/worst/likely case)
- **Recommendations** (What decision-makers should consider)
- **Related Developments** (Connected events to monitor)
- **Artifacts:** PDF brief, HTML version, PowerPoint slides

---

## 🏗️ Architecture

### Workflow
```
START → Issue Analysis → Background Research (Historical Context) → 
Stakeholder Mapping → Impact Assessment → Scenario Modeling → 
Recommendation Generation → Citation Collection → 
Artifact Generation (PDF/PPT/HTML) → END
```

### Key Difference from SitRep
- **SitRep:** "What happened?" (breadth, many events)
- **Policy Brief:** "What does it mean?" (depth, one issue)

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner
2. **`state.py`** - State schema
3. **`config.py`** - Brief templates, analysis frameworks
4. **`graph.py`** - LangGraph workflow
5. **`nodes/issue_analyzer.py`** - Deep dive into the issue
6. **`nodes/background_researcher.py`** - Historical context
7. **`nodes/stakeholder_mapper.py`** - Identify key players
8. **`nodes/impact_assessor.py`** - Analyze implications
9. **`nodes/scenario_modeler.py`** - Model possible outcomes
10. **`nodes/recommendation_generator.py`** - Generate action items
11. **`nodes/artifact_generator.py`** - Create PDF/PPT/HTML
12. **`templates/` - Brief templates (PDF/PPT)
13. **`tests/test_agent.py`**

---

## 📝 Policy Brief Structure

### Standard Issue Brief Format

```markdown
# POLICY BRIEF
## [Issue Title]

**Date:** [Date]
**Classification:** [Public / Confidential / Internal]
**Prepared For:** [Stakeholder/Department]

---

## EXECUTIVE SUMMARY

[2-3 sentences that answer:]
- What is the issue?
- Why does it matter?
- What's the recommended approach?

---

## ISSUE OVERVIEW

### What Happened
[Factual description of the event/policy/development]

### Significance
[Why this matters - political, economic, social, security implications]

### Urgency
[Timeline for decision/action, any deadlines]

---

## BACKGROUND & CONTEXT

### Historical Context
[How did we get here? What led to this?]

### Previous Attempts
[Have there been similar situations? What happened?]

### Legal/Regulatory Framework
[Relevant laws, treaties, regulations]

---

## KEY STAKEHOLDERS

### Primary Actors
- **[Entity Name]**
  - Position: [What they want]
  - Leverage: [What power/influence they have]
  - Motivation: [Why they care]

### Secondary Players
- **[Entity Name]** - [Brief role]

### Opposition/Supporters
[Who supports, who opposes, and why]

---

## ANALYSIS

### Political Implications
[Impact on power dynamics, elections, coalitions]

### Economic Impact
[Financial effects, market reactions, trade implications]

### Social Considerations
[Public opinion, civil society, humanitarian aspects]

### Security Concerns
[Military, intelligence, cyber, terrorism angles]

### Diplomatic Dimensions
[International relations, alliances, bilateral ties]

---

## SCENARIO ANALYSIS

### BEST CASE Scenario (Probability: X%)
[What happens if everything goes well]
- Indicators to watch: [...]
- Timeline: [...]

### MOST LIKELY Scenario (Probability: Y%)
[What will probably happen]
- Indicators: [...]
- Timeline: [...]

### WORST CASE Scenario (Probability: Z%)
[What happens if things go wrong]
- Indicators: [...]
- Timeline: [...]

---

## RECOMMENDATIONS

### Immediate Actions (0-7 days)
1. [Specific actionable step]
2. [Another step]

### Short-term (1-4 weeks)
1. [Action item]

### Long-term (1-3 months)
1. [Strategic consideration]

### Contingency Planning
[If scenario X occurs, do Y]

---

## MONITORING & INDICATORS

### Key Indicators to Watch
- [ ] [Specific metric or event]
- [ ] [Another indicator]

### Decision Points
- **[Date]** - [Event that may require decision]
- **[Date]** - [Another critical moment]

---

## RELATED DEVELOPMENTS

[Links to related events, bills, policies that are relevant]

---

## SOURCES & REFERENCES

1. [Source 1 - URL]
2. [Source 2 - URL]
[... citations ...]

---

**Classification:** [Public]
**Prepared By:** Political Analyst Workbench
**Date:** [Timestamp]
**Version:** 1.0
```

---

## 🔑 Key Node: Scenario Modeler (`nodes/scenario_modeler.py`)

```python
"""
Model possible outcomes for policy/issue
"""

from typing import Dict, List, Any
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

async def model_scenarios(
    issue: str,
    background: str,
    stakeholders: List[Dict],
    current_situation: str
) -> Dict[str, Any]:
    """
    Generate three scenarios: best case, most likely, worst case
    
    Each scenario includes:
    - Description of outcome
    - Probability (0-1)
    - Timeline (when it could happen)
    - Key indicators to watch
    - Triggers (what would cause this scenario)
    - Implications
    """
    
    prompt = f"""You are a political analyst creating scenario projections for a policy brief.

ISSUE: {issue}

BACKGROUND: {background}

KEY STAKEHOLDERS:
{json.dumps([{
    "name": s["name"],
    "position": s.get("position", ""),
    "leverage": s.get("leverage", "")
} for s in stakeholders], indent=2)}

CURRENT SITUATION: {current_situation}

Create three scenarios:

1. BEST CASE: Most favorable outcome
   - What happens
   - Probability (0-1)
   - Timeline to realization
   - Key indicators that this is unfolding
   - What triggers this scenario
   - Implications

2. MOST LIKELY: Realistic middle-ground outcome
   [Same fields]

3. WORST CASE: Most unfavorable outcome
   [Same fields]

Be specific and realistic. Base probabilities on historical precedent and current momentum.
Probabilities must sum to ~1.0 (allow some for "other" scenarios).

Return JSON with: {{"best_case": {{...}}, "most_likely": {{...}}, "worst_case": {{...}}}}"""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    scenarios = json.loads(response.choices[0].message.content)
    
    # Validate probabilities
    total_prob = (
        scenarios["best_case"]["probability"] +
        scenarios["most_likely"]["probability"] +
        scenarios["worst_case"]["probability"]
    )
    
    # Normalize if needed
    if total_prob > 1.1 or total_prob < 0.9:
        for scenario_type in ["best_case", "most_likely", "worst_case"]:
            scenarios[scenario_type]["probability"] /= total_prob
    
    return scenarios
```

---

## 🔑 Key Node: Recommendation Generator (`nodes/recommendation_generator.py`)

```python
"""
Generate actionable recommendations for decision-makers
"""

from typing import Dict, List, Any
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

async def generate_recommendations(
    issue: str,
    analysis: Dict[str, str],
    scenarios: Dict[str, Any],
    stakeholder_perspective: str = "government"
) -> Dict[str, List[str]]:
    """
    Generate recommendations based on analysis and scenarios
    
    Categories:
    - immediate: 0-7 days
    - short_term: 1-4 weeks
    - long_term: 1-3 months
    - contingency: If X happens, do Y
    """
    
    prompt = f"""You are advising a {stakeholder_perspective} decision-maker on this issue:

ISSUE: {issue}

KEY ANALYSIS:
- Political implications: {analysis.get('political', '')}
- Economic impact: {analysis.get('economic', '')}
- Security concerns: {analysis.get('security', '')}

MOST LIKELY SCENARIO (Probability: {scenarios['most_likely']['probability']:.0%}):
{scenarios['most_likely']['description']}

WORST CASE SCENARIO (Probability: {scenarios['worst_case']['probability']:.0%}):
{scenarios['worst_case']['description']}

Generate SPECIFIC, ACTIONABLE recommendations:

1. IMMEDIATE ACTIONS (0-7 days) - What must be done now
   - Specific steps, not vague suggestions
   - Assign to specific entities when possible

2. SHORT-TERM ACTIONS (1-4 weeks)
   - Building on immediate actions
   - Positioning for most likely scenario

3. LONG-TERM STRATEGIC MOVES (1-3 months)
   - Structural changes or policy shifts needed

4. CONTINGENCY PLANS
   - IF [specific trigger] THEN [specific action]
   - Prepare for worst case scenario

Style: Direct, actionable, specific. No vague suggestions like "monitor the situation."

Return JSON: {{
  "immediate": ["action 1", "action 2"],
  "short_term": ["..."],
  "long_term": ["..."],
  "contingency": ["IF X THEN Y", ...]
}}"""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## 🎨 Artifact Generation

### 1. PDF Brief (Detailed Report)

```python
# nodes/artifact_generator.py

async def generate_pdf_brief(brief_data: Dict[str, Any]) -> str:
    """
    Generate professional PDF using template + pdfkit
    """
    
    from jinja2 import Template
    import pdfkit
    
    template = load_policy_brief_template()
    html_content = template.render(brief=brief_data)
    
    # PDF options for professional look
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'enable-local-file-access': None
    }
    
    pdf_path = f"artifacts/policy_brief_{brief_data['issue_id']}.pdf"
    pdfkit.from_string(html_content, pdf_path, options=options)
    
    return pdf_path
```

### 2. PowerPoint Slides (Executive Presentation)

```python
from pptx import Presentation
from pptx.util import Inches, Pt

async def generate_ppt_slides(brief_data: Dict[str, Any]) -> str:
    """
    Generate PowerPoint slides for executive presentation
    
    Slides:
    1. Title slide
    2. Executive summary
    3. Background & context
    4. Stakeholder map (visual)
    5. Scenario comparison (table)
    6. Recommendations (bullets)
    7. Next steps & monitoring
    """
    
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Title
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = title_slide.shapes.title
    title.text = brief_data["title"]
    subtitle = title_slide.placeholders[1]
    subtitle.text = f"Policy Brief | {brief_data['date']}"
    
    # Slide 2: Executive Summary
    summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
    summary_slide.shapes.title.text = "Executive Summary"
    body = summary_slide.placeholders[1]
    tf = body.text_frame
    tf.text = brief_data["executive_summary"]
    
    # Slide 3: Background
    # ... (similar pattern)
    
    # Slide 5: Scenarios (Table)
    scenario_slide = prs.slides.add_slide(prs.slide_layouts[5])
    scenario_slide.shapes.title.text = "Scenario Analysis"
    
    # Add table with scenarios
    rows, cols = 4, 4
    left = Inches(1.0)
    top = Inches(2.0)
    width = Inches(8.0)
    height = Inches(3.0)
    
    table = scenario_slide.shapes.add_table(rows, cols, left, top, width, height).table
    
    # Headers
    table.cell(0, 0).text = "Scenario"
    table.cell(0, 1).text = "Probability"
    table.cell(0, 2).text = "Timeline"
    table.cell(0, 3).text = "Key Indicators"
    
    # Fill with scenario data
    scenarios = ["Best Case", "Most Likely", "Worst Case"]
    for i, scenario_type in enumerate(["best_case", "most_likely", "worst_case"]):
        scenario = brief_data["scenarios"][scenario_type]
        table.cell(i+1, 0).text = scenarios[i]
        table.cell(i+1, 1).text = f"{scenario['probability']:.0%}"
        table.cell(i+1, 2).text = scenario["timeline"]
        table.cell(i+1, 3).text = scenario["indicators"][0]  # First indicator
    
    # Save
    ppt_path = f"artifacts/policy_brief_{brief_data['issue_id']}.pptx"
    prs.save(ppt_path)
    
    return ppt_path
```

---

## 📊 Example Output

### Query:
```
"Generate policy brief on new infrastructure bill in US"
```

### Response Structure:
```json
{
  "type": "policy_brief",
  "issue_id": "us_infrastructure_bill_2025",
  "title": "Analysis: U.S. Infrastructure Investment and Jobs Act",
  "date": "2025-10-02",
  "classification": "Public",
  "prepared_for": "Policy Team",
  
  "executive_summary": "Senate passage of $1.2T infrastructure bill represents major bipartisan legislative achievement with broad economic implications. Bill addresses critical infrastructure gaps but faces implementation challenges and political risks in House. Recommend positioning for implementation phase while monitoring House dynamics.",
  
  "background": {
    "historical_context": "Previous infrastructure efforts failed in 2018, 2019...",
    "previous_attempts": "...",
    "legal_framework": "..."
  },
  
  "stakeholders": [
    {
      "name": "Biden Administration",
      "type": "government",
      "position": "Strong support, signature policy achievement",
      "leverage": "Executive authority, bully pulpit",
      "motivation": "Political legacy, economic stimulus"
    },
    {
      "name": "Progressive Democrats",
      "type": "political_faction",
      "position": "Conditional support, want larger social spending",
      "leverage": "Can block in House",
      "motivation": "Climate action, social programs"
    }
  ],
  
  "analysis": {
    "political": "Demonstrates capacity for bipartisan action...",
    "economic": "$550B in new spending over 5 years...",
    "social": "Job creation in construction, manufacturing...",
    "implementation": "State-level execution presents challenges..."
  },
  
  "scenarios": {
    "best_case": {
      "description": "Swift House passage, efficient rollout, economic boost",
      "probability": 0.35,
      "timeline": "2-3 months to House passage",
      "indicators": ["Quick committee action", "Positive public polling"],
      "triggers": ["Progressive-moderate compromise reached"],
      "implications": "Major policy win, economic stimulus"
    },
    "most_likely": {
      "description": "Delayed House passage after negotiations, gradual implementation",
      "probability": 0.50,
      "timeline": "3-6 months",
      "indicators": ["Ongoing negotiations", "Amendment proposals"],
      "implications": "Modest policy achievement, some economic impact"
    },
    "worst_case": {
      "description": "House blocks bill, coalition fractures",
      "probability": 0.15,
      "timeline": "6+ months of gridlock",
      "indicators": ["Progressive threats to block", "Republican defections"],
      "implications": "Legislative failure, political damage"
    }
  },
  
  "recommendations": {
    "immediate": [
      "Monitor House progressive caucus position on linking bills",
      "Engage state governments on implementation readiness",
      "Brief stakeholders on economic impact projections"
    ],
    "short_term": [
      "Develop implementation framework for 60-day post-passage",
      "Coordinate with DOT on fund allocation priorities",
      "Prepare public messaging for construction phase"
    ],
    "long_term": [
      "Establish oversight mechanisms for $550B spending",
      "Plan for supplemental infrastructure needs beyond this bill",
      "Assess lessons learned for future legislative efforts"
    ],
    "contingency": [
      "IF progressive Democrats block → shift to scaled-down version",
      "IF implementation lags → activate federal-state coordination task force",
      "IF economic conditions worsen → accelerate spending timeline"
    ]
  },
  
  "monitoring": {
    "key_indicators": [
      "House Rules Committee scheduling",
      "Progressive caucus statements",
      "State DOT readiness reports",
      "Construction industry forecasts"
    ],
    "decision_points": [
      {"date": "2025-10-15", "event": "House committee markup expected"},
      {"date": "2025-11-01", "event": "Potential House floor vote"}
    ]
  },
  
  "artifacts": {
    "pdf": "artifacts/policy_brief_us_infrastructure_bill_2025.pdf",
    "pptx": "artifacts/policy_brief_us_infrastructure_bill_2025.pptx",
    "html": "artifacts/policy_brief_us_infrastructure_bill_2025.html",
    "json": "artifacts/policy_brief_us_infrastructure_bill_2025.json"
  },
  
  "citations": [
    {"source": "Senate.gov - Bill Text", "url": "..."},
    {"source": "CBO Economic Analysis", "url": "..."}
  ]
}
```

---

## 🔌 Integration

### Depends On:
- **Live Political Monitor** (for related events)
- **Tavily Search** (for deep research)
- **Sentiment Analyzer** (optional, for public opinion)
- **Entity Extractor** (optional, for stakeholder mapping)

### Can Call Other Agents:
```python
# In nodes/background_researcher.py
from sub_agents.entity_relationship_extractor import extract_entities
from sub_agents.sentiment_analyzer import analyze_sentiment

# Get stakeholder network
entities = await extract_entities(issue_description)

# Get public sentiment
sentiment = await analyze_sentiment(issue_description, countries)
```

---

## 🧪 Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/policy_brief_generator

# Test with sample issue
python main.py --issue "US infrastructure bill" --perspective "government"

# Test with specific event from Live Monitor
python main.py --event-id "evt_1696284600_abc123"
```

---

## 📦 Required Packages

```bash
uv pip install jinja2           # Template rendering
uv pip install pdfkit           # PDF generation
uv pip install python-pptx      # PowerPoint generation
uv pip install pymongo          # MongoDB (already installed)
```

---

## ⚙️ On-Demand vs Scheduled

### On-Demand (Default)
User requests: "Analyze this policy/event"

### Automated Triggers
```python
# In Live Political Monitor
if event["significance_score"] >= 12:
    # Auto-generate policy brief for critical events
    trigger_policy_brief_generation(event)
```

---

## ✅ Definition of Done

- [ ] Performs deep analysis of single issue
- [ ] Generates historical background/context
- [ ] Maps stakeholders with positions/motivations
- [ ] Creates 3 scenarios (best/likely/worst) with probabilities
- [ ] Generates actionable recommendations (immediate/short/long-term)
- [ ] Produces PDF artifact (professional brief)
- [ ] Produces PowerPoint slides (executive presentation)
- [ ] Produces HTML version (web-readable)
- [ ] Includes citations and sources
- [ ] Works standalone
- [ ] Response time <30s
- [ ] Tests passing

**Effort:** 5-6 days (2 developers)  
**Impact:** ⭐⭐⭐⭐⭐ **HIGHEST VALUE** - Core analyst deliverable  
**Priority:** 🔴 HIGH - Build after Live Monitor and SitRep

