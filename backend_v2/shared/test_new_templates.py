"""
Test script for new infographic templates
"""

from infographic_generator import InfographicGenerator
import json

print("🎨 Testing New Infographic Templates")
print("=" * 70)
print()

generator = InfographicGenerator(output_dir="artifacts")

# Test data for each template
test_cases = [
    {
        "name": "Dashboard Template",
        "template": "dashboard",
        "data": {
            "title": "US Political Sentiment Dashboard",
            "subtitle": "Positive momentum observed across key demographics with increasing approval ratings",
            "stats": [
                {"label": "Approval", "value": "68%", "color": "primary"},
                {"label": "Sources", "value": "1,247", "color": "accent"},
                {"label": "Sentiment", "value": "+0.82", "color": "primary"},
                {"label": "Trend", "value": "↑12%", "color": "accent"}
            ],
            "footer": "Analysis: Oct 2, 2025 | Confidence: 94%"
        }
    },
    {
        "name": "Comparison Template",
        "template": "comparison",
        "data": {
            "title": "Policy Comparison: Climate Action",
            "comparison": {
                "option_a": {
                    "title": "Proposal A",
                    "stats": [
                        {"label": "Cost", "value": "$500B"},
                        {"label": "Timeline", "value": "5 years"},
                        {"label": "Emissions Cut", "value": "40%"}
                    ]
                },
                "option_b": {
                    "title": "Proposal B",
                    "stats": [
                        {"label": "Cost", "value": "$750B"},
                        {"label": "Timeline", "value": "3 years"},
                        {"label": "Emissions Cut", "value": "60%"}
                    ]
                },
                "conclusion": "Proposal B offers faster emissions reduction at higher cost"
            },
            "footer": "Policy Analysis | Oct 2025"
        }
    },
    {
        "name": "Timeline Template",
        "template": "timeline",
        "data": {
            "title": "Climate Policy Evolution",
            "timeline": [
                {"date": "Jan 2024", "event": "Policy Announced"},
                {"date": "Mar 2024", "event": "Public Consultation"},
                {"date": "Jul 2024", "event": "Legislation Passed"},
                {"date": "Oct 2024", "event": "Implementation"},
                {"date": "Jan 2025", "event": "First Review"}
            ],
            "footer": "Timeline | Climate Action Initiative"
        }
    },
    {
        "name": "Icon Grid Template",
        "template": "icon_grid",
        "data": {
            "title": "Political Landscape 2025",
            "stats": [
                {"label": "States", "value": "45", "color": "primary"},
                {"label": "Voters", "value": "155M", "color": "accent"},
                {"label": "Districts", "value": "435", "color": "secondary"},
                {"label": "Bills", "value": "328", "color": "primary"},
                {"label": "Approval", "value": "62%", "color": "accent"},
                {"label": "Turnout", "value": "67%", "color": "secondary"}
            ],
            "footer": "Key Statistics | 2025 Analysis"
        }
    }
]

results = []

for test_case in test_cases:
    print(f"📊 Generating: {test_case['name']}")
    print(f"   Template: {test_case['template']}")
    
    try:
        result = generator.create_social_post(
            data=test_case['data'],
            platform="instagram_post",
            template=test_case['template']
        )
        
        results.append({
            "name": test_case['name'],
            "template": test_case['template'],
            "path": result['path'],
            "size_kb": result['size_bytes'] / 1024
        })
        
        print(f"   ✅ Created: {result['path']}")
        print(f"   Size: {result['size_bytes'] / 1024:.1f} KB")
        print()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()

print(f"\n🎉 Generated {len(results)} new template examples!")
print()

# Save results
summary_path = "artifacts/new_templates_results.json"
with open(summary_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"📄 Results saved to: {summary_path}")
print()

# Print summary table
print("Summary:")
print("-" * 70)
for r in results:
    print(f"  {r['name']:30} | {r['template']:15} | {r['size_kb']:.1f} KB")
print("-" * 70)
print()
print("📁 View all files at: backend_v2/shared/artifacts/")

