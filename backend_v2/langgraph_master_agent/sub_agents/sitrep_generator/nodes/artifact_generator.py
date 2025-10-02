"""
Artifact Generator Node

Generates HTML, PDF, TXT, and JSON outputs for SitRep.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template
from state import SitRepState
from config import ARTIFACT_DIR, COLORS, FONT_FAMILY, CONTAINER_MAX_WIDTH


def generate_artifacts(state: SitRepState) -> Dict[str, Any]:
    """
    Generate multiple artifact formats:
    - HTML (interactive dashboard)
    - PDF (printable - requires wkhtmltopdf, skip if not available)
    - TXT (email-ready plaintext)
    - JSON (machine-readable)
    
    Args:
        state: Current state with all analysis complete
        
    Returns:
        Updated state with artifacts list
    """
    
    print("\n" + "="*80)
    print("📄 NODE: Artifact Generator")
    print("="*80)
    
    # Create timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts = []
    
    # Ensure artifacts directory exists
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    
    print(f"Generating artifacts in: {ARTIFACT_DIR}/")
    
    # ============================================================================
    # 1. HTML VERSION (Interactive Dashboard)
    # ============================================================================
    
    try:
        html_content = generate_html(state)
        html_path = os.path.join(ARTIFACT_DIR, f"sitrep_{timestamp}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        artifacts.append({
            "type": "html",
            "path": html_path,
            "size_kb": os.path.getsize(html_path) / 1024
        })
        
        print(f"   ✅ HTML: {html_path} ({artifacts[-1]['size_kb']:.1f} KB)")
        
    except Exception as e:
        print(f"   ❌ HTML generation failed: {e}")
        state["error_log"].append(f"HTML generation failed: {e}")
    
    # ============================================================================
    # 2. PLAIN TEXT VERSION (Email-ready)
    # ============================================================================
    
    try:
        txt_content = generate_plaintext(state)
        txt_path = os.path.join(ARTIFACT_DIR, f"sitrep_{timestamp}.txt")
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        artifacts.append({
            "type": "txt",
            "path": txt_path,
            "size_kb": os.path.getsize(txt_path) / 1024
        })
        
        print(f"   ✅ TXT: {txt_path} ({artifacts[-1]['size_kb']:.1f} KB)")
        
    except Exception as e:
        print(f"   ❌ TXT generation failed: {e}")
        state["error_log"].append(f"TXT generation failed: {e}")
    
    # ============================================================================
    # 3. JSON VERSION (Machine-readable)
    # ============================================================================
    
    try:
        json_data = {
            "type": "sitrep",
            "period": state.get("period", "daily"),
            "date_range": state.get("date_range", ""),
            "region_focus": state.get("region_focus"),
            "executive_summary": state.get("executive_summary", ""),
            "urgent_events": state.get("urgent_events", []),
            "high_priority_events": state.get("high_priority_events", []),
            "notable_events": state.get("notable_events", []),
            "regional_breakdown": state.get("regional_breakdown", {}),
            "trending_topics": state.get("trending_topics", []),
            "watch_list": state.get("watch_list", []),
            "metadata": {
                "events_analyzed": state.get("event_count", 0),
                "regions_covered": state.get("regions_covered", []),
                "source_count": state.get("source_count", 0),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        json_path = os.path.join(ARTIFACT_DIR, f"sitrep_{timestamp}.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        artifacts.append({
            "type": "json",
            "path": json_path,
            "size_kb": os.path.getsize(json_path) / 1024
        })
        
        print(f"   ✅ JSON: {json_path} ({artifacts[-1]['size_kb']:.1f} KB)")
        
    except Exception as e:
        print(f"   ❌ JSON generation failed: {e}")
        state["error_log"].append(f"JSON generation failed: {e}")
    
    # ============================================================================
    # 4. PDF VERSION (Optional - requires wkhtmltopdf)
    # ============================================================================
    
    try:
        import pdfkit
        pdf_path = os.path.join(ARTIFACT_DIR, f"sitrep_{timestamp}.pdf")
        pdfkit.from_string(html_content, pdf_path)
        
        artifacts.append({
            "type": "pdf",
            "path": pdf_path,
            "size_kb": os.path.getsize(pdf_path) / 1024
        })
        
        print(f"   ✅ PDF: {pdf_path} ({artifacts[-1]['size_kb']:.1f} KB)")
        
    except ImportError:
        print(f"   ⚠️  PDF: Skipped (pdfkit not installed)")
    except Exception as e:
        print(f"   ⚠️  PDF: Skipped ({str(e)[:50]}...)")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    
    print(f"\n📊 Generated {len(artifacts)} artifacts:")
    for artifact in artifacts:
        print(f"   {artifact['type'].upper()}: {artifact['size_kb']:.1f} KB")
    
    state["artifacts"] = artifacts
    state["execution_log"].append(f"✅ Generated {len(artifacts)} artifacts")
    
    return state


def generate_html(state: SitRepState) -> str:
    """Generate HTML version of SitRep with Aistra styling"""
    
    template_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Political Situation Report - {{ date_range }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: {{ font_family }};
            background: {{ colors.darkest }};
            color: {{ colors.dark }};
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: {{ container_width }};
            margin: 0 auto;
            background: {{ colors.white }};
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        header {
            border-bottom: 4px solid {{ colors.primary }};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: {{ colors.darkest }};
            font-size: 32px;
            margin-bottom: 10px;
        }
        .date-range {
            color: {{ colors.secondary }};
            font-size: 18px;
        }
        .executive-summary {
            background: {{ colors.primary }};
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid {{ colors.secondary }};
            border-radius: 4px;
        }
        .executive-summary h2 {
            color: {{ colors.darkest }};
            margin-bottom: 15px;
            font-size: 24px;
        }
        .executive-summary p {
            font-size: 16px;
            line-height: 1.8;
        }
        .section {
            margin: 30px 0;
        }
        .section h2 {
            color: {{ colors.darkest }};
            border-bottom: 2px solid {{ colors.secondary }};
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .section h3 {
            color: {{ colors.dark }};
            margin: 20px 0 10px 0;
            font-size: 18px;
        }
        .event {
            margin: 15px 0;
            padding: 15px;
            padding-left: 20px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .event-title {
            font-weight: bold;
            color: {{ colors.darkest }};
            font-size: 16px;
            margin-bottom: 5px;
        }
        .event-meta {
            color: {{ colors.secondary }};
            font-size: 13px;
            margin-bottom: 8px;
        }
        .event-summary {
            color: {{ colors.dark }};
            font-size: 14px;
        }
        .priority-urgent {
            border-left: 5px solid {{ colors.urgent }};
        }
        .priority-high {
            border-left: 5px solid {{ colors.high }};
        }
        .priority-notable {
            border-left: 5px solid {{ colors.notable }};
        }
        .regional-section {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .trending-topics {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .topic-tag {
            background: {{ colors.primary }};
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            color: {{ colors.darkest }};
            font-weight: 500;
        }
        .watch-list {
            background: #fff3cd;
            padding: 20px;
            border-left: 5px solid {{ colors.high }};
            border-radius: 4px;
            margin: 20px 0;
        }
        .watch-list h2 {
            color: {{ colors.darkest }};
            margin-bottom: 15px;
        }
        .watch-list ul {
            list-style-type: none;
            padding: 0;
        }
        .watch-list li {
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .watch-list li:last-child {
            border-bottom: none;
        }
        .watch-list li:before {
            content: "👁️ ";
            margin-right: 8px;
        }
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid {{ colors.secondary }};
            color: {{ colors.secondary }};
            font-size: 12px;
            text-align: center;
        }
        .metadata {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 POLITICAL SITUATION REPORT</h1>
            <div class="date-range">{{ date_range }}</div>
            {% if region_focus %}
            <div class="date-range">Region Focus: {{ region_focus }}</div>
            {% endif %}
        </header>
        
        <div class="executive-summary">
            <h2>EXECUTIVE SUMMARY</h2>
            <p>{{ executive_summary }}</p>
        </div>
        
        <div class="section">
            <h2>KEY DEVELOPMENTS</h2>
            
            {% if urgent_events %}
            <h3 style="color: {{ colors.urgent }};">🔴 URGENT (Score ≥ 80)</h3>
            {% for event in urgent_events %}
            <div class="event priority-urgent">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-meta">
                    {{ event.regions|join(", ") }} | 
                    Explosiveness Score: {{ event.explosiveness_score }}/100 |
                    LLM Rating: {{ event.llm_rating }}/10
                </div>
                <div class="event-summary">{{ event.reasoning }}</div>
            </div>
            {% endfor %}
            {% endif %}
            
            {% if high_priority_events %}
            <h3 style="color: {{ colors.high }};">🟠 HIGH PRIORITY (Score 60-79)</h3>
            {% for event in high_priority_events %}
            <div class="event priority-high">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-meta">
                    {{ event.regions|join(", ") }} | Score: {{ event.explosiveness_score }}
                </div>
                <div class="event-summary">{{ event.reasoning[:300] }}...</div>
            </div>
            {% endfor %}
            {% endif %}
            
            {% if notable_events %}
            <h3 style="color: {{ colors.notable }};">🟡 NOTABLE (Score 40-59)</h3>
            {% for event in notable_events[:5] %}
            <div class="event priority-notable">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-meta">{{ event.regions|join(", ") }} | Score: {{ event.explosiveness_score }}</div>
            </div>
            {% endfor %}
            {% endif %}
        </div>
        
        {% if regional_breakdown %}
        <div class="section">
            <h2>REGIONAL BREAKDOWN</h2>
            {% for region, events in regional_breakdown.items() %}
            <div class="regional-section">
                <h3>{{ region }} ({{ events|length }} events)</h3>
                <ul style="margin-left: 20px;">
                {% for event in events[:5] %}
                    <li><strong>{{ event.title }}</strong> (Score: {{ event.explosiveness_score }})</li>
                {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if trending_topics %}
        <div class="section">
            <h2>TRENDING TOPICS</h2>
            <div class="trending-topics">
            {% for topic in trending_topics %}
                <span class="topic-tag">{{ topic|capitalize }}</span>
            {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if watch_list %}
        <div class="watch-list">
            <h2>👁️ WATCH LIST - Next 24-48 Hours</h2>
            <ul>
            {% for item in watch_list %}
                <li>{{ item }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <footer>
            <div class="metadata">
                <span>Events Analyzed: {{ event_count }}</span>
                <span>Regions: {{ regions_covered|length }}</span>
                <span>Sources: {{ source_count }}</span>
            </div>
            <p style="margin-top: 10px;">Generated: {{ generated_at }}</p>
            <p>Powered by Political Analyst Workbench</p>
        </footer>
    </div>
</body>
</html>"""
    
    template = Template(template_html)
    
    html = template.render(
        date_range=state.get("date_range", ""),
        region_focus=state.get("region_focus"),
        executive_summary=state.get("executive_summary", ""),
        urgent_events=state.get("urgent_events", []),
        high_priority_events=state.get("high_priority_events", []),
        notable_events=state.get("notable_events", []),
        regional_breakdown=state.get("regional_breakdown", {}),
        trending_topics=state.get("trending_topics", []),
        watch_list=state.get("watch_list", []),
        event_count=state.get("event_count", 0),
        regions_covered=state.get("regions_covered", []),
        source_count=state.get("source_count", 0),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        colors=COLORS,
        font_family=FONT_FAMILY,
        container_width=CONTAINER_MAX_WIDTH
    )
    
    return html


def generate_plaintext(state: SitRepState) -> str:
    """Generate plain text version (email-ready)"""
    
    lines = []
    lines.append("=" * 80)
    lines.append("POLITICAL SITUATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Date Range: {state.get('date_range', '')}")
    if state.get("region_focus"):
        lines.append(f"Region Focus: {state.get('region_focus')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Executive Summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 80)
    lines.append(state.get("executive_summary", ""))
    lines.append("")
    
    # Key Developments
    lines.append("KEY DEVELOPMENTS")
    lines.append("-" * 80)
    lines.append("")
    
    urgent = state.get("urgent_events", [])
    if urgent:
        lines.append("🔴 URGENT")
        for event in urgent:
            lines.append(f"\n• {event.get('title', 'Unknown')}")
            lines.append(f"  Regions: {', '.join(event.get('regions', ['Global']))}")
            lines.append(f"  Score: {event.get('explosiveness_score', 0)}/100")
            lines.append(f"  {event.get('reasoning', '')[:200]}...")
        lines.append("")
    
    high = state.get("high_priority_events", [])
    if high:
        lines.append("🟠 HIGH PRIORITY")
        for event in high:
            lines.append(f"\n• {event.get('title', 'Unknown')}")
            lines.append(f"  {', '.join(event.get('regions', ['Global']))} | Score: {event.get('explosiveness_score', 0)}")
        lines.append("")
    
    # Regional Breakdown
    regional = state.get("regional_breakdown", {})
    if regional:
        lines.append("REGIONAL BREAKDOWN")
        lines.append("-" * 80)
        for region, events in regional.items():
            lines.append(f"\n{region} ({len(events)} events):")
            for event in events[:5]:
                lines.append(f"  • {event.get('title', 'Unknown')}")
        lines.append("")
    
    # Trending Topics
    topics = state.get("trending_topics", [])
    if topics:
        lines.append("TRENDING TOPICS")
        lines.append("-" * 80)
        lines.append(", ".join([t.capitalize() for t in topics]))
        lines.append("")
    
    # Watch List
    watch = state.get("watch_list", [])
    if watch:
        lines.append("👁️ WATCH LIST - Next 24-48 Hours")
        lines.append("-" * 80)
        for i, item in enumerate(watch, 1):
            lines.append(f"{i}. {item}")
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append(f"Events Analyzed: {state.get('event_count', 0)} | Regions: {len(state.get('regions_covered', []))} | Sources: {state.get('source_count', 0)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("Powered by Political Analyst Workbench")
    lines.append("=" * 80)
    
    return "\n".join(lines)

