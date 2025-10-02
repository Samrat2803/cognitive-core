"""
Test Map Visualization - Visual Debugging

Creates a test map and opens it in browser to verify it's visible
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langgraph_master_agent.tools.visualization_tools import MapChartTool

# Test data - US and Israel with clear values
test_data = {
    "countries": ["United States", "Israel"],
    "values": [-0.6, -0.4],  # Both negative to show clearly
    "labels": ["US: -0.6", "Israel: -0.4"]
}

print("🗺️  Creating test map...")
print(f"   Countries: {test_data['countries']}")
print(f"   Values: {test_data['values']}")

try:
    artifact = MapChartTool.create(
        data=test_data,
        title="TEST MAP - Should Show US and Israel in Color",
        legend_title="Test Score"
    )
    
    print(f"\n✅ Map created!")
    print(f"   File: {artifact['html_path']}")
    print(f"   Artifact ID: {artifact['artifact_id']}")
    
    # Try to open in browser
    import webbrowser
    print(f"\n🌐 Opening map in browser...")
    webbrowser.open(f"file://{os.path.abspath(artifact['html_path'])}")
    
    print(f"\n📝 What to look for:")
    print(f"   ✅ United States should be colored (large, easy to see)")
    print(f"   ✅ Israel should be colored (small, in Middle East)")
    print(f"   ✅ Both should have text labels with values")
    print(f"   ✅ Legend on right side")
    
    print(f"\n❓ Is the map empty/white?")
    print(f"   - Check browser console for JavaScript errors")
    print(f"   - Look for US (large country) - should be clearly visible")
    print(f"   - Israel is tiny, zoom in to Middle East to see it")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

