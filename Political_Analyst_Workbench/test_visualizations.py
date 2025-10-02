"""
Test Visualization Tools
Quick test of bar chart, line chart, and mind map creation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from langgraph_master_agent.tools.visualization_tools import (
    create_bar_chart,
    create_line_chart,
    create_mind_map
)


def test_bar_chart():
    """Test bar chart creation"""
    print("\n📊 Testing Bar Chart...")
    
    data = {
        "categories": ["US", "EU", "China", "India", "Brazil"],
        "values": [85, 72, 45, 60, 55]
    }
    
    result = create_bar_chart(data, title="Global Sentiment Analysis")
    
    print(f"✅ Created: {result['artifact_id']}")
    print(f"   HTML: {result['html_path']}")
    print(f"   PNG: {result['png_path']}")
    
    return result


def test_line_chart():
    """Test line chart creation"""
    print("\n📈 Testing Line Chart...")
    
    data = {
        "x": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "y": [10, 15, 13, 17, 20, 18]
    }
    
    result = create_line_chart(data, title="Trend Over Time")
    
    print(f"✅ Created: {result['artifact_id']}")
    print(f"   HTML: {result['html_path']}")
    print(f"   PNG: {result['png_path']}")
    
    return result


def test_mind_map():
    """Test mind map creation"""
    print("\n🧠 Testing Mind Map...")
    
    data = {
        "root": "Political Analysis",
        "children": [
            {
                "name": "Data Collection",
                "value": 10,
                "children": [
                    {"name": "Web Search", "value": 5},
                    {"name": "Source Verification", "value": 5}
                ]
            },
            {
                "name": "Analysis",
                "value": 15,
                "children": [
                    {"name": "Sentiment", "value": 8},
                    {"name": "Bias Detection", "value": 7}
                ]
            },
            {
                "name": "Reporting",
                "value": 8
            }
        ]
    }
    
    result = create_mind_map(data, title="Analysis Framework")
    
    print(f"✅ Created: {result['artifact_id']}")
    print(f"   HTML: {result['html_path']}")
    print(f"   PNG: {result['png_path']}")
    
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 VISUALIZATION TOOLS TEST")
    print("=" * 60)
    
    try:
        # Test each visualization type
        bar_result = test_bar_chart()
        line_result = test_line_chart()
        mindmap_result = test_mind_map()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nCreated artifacts:")
        print(f"  1. Bar Chart:  {bar_result['html_path']}")
        print(f"  2. Line Chart: {line_result['html_path']}")
        print(f"  3. Mind Map:   {mindmap_result['html_path']}")
        print("\nOpen these HTML files in your browser to view!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

