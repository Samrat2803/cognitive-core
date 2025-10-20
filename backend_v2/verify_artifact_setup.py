#!/usr/bin/env python3
"""
Quick verification script to check artifact setup
"""

import os
from pathlib import Path

print("🔍 Checking Investigative Journalist Artifact Setup...")
print("="*80)

# Check file structure
backend_root = Path(__file__).parent
investigator_dir = backend_root / "langgraph_master_agent" / "sub_agents" / "investigative_journalist"
artifacts_dir = investigator_dir / "artifacts"
tools_dir = investigator_dir / "tools"

print("\n1. Directory Structure:")
print(f"   Backend root: {backend_root}")
print(f"   ✓ Investigator exists: {investigator_dir.exists()}")
print(f"   ✓ Tools dir exists: {tools_dir.exists()}")
print(f"   ✓ Artifacts dir exists: {artifacts_dir.exists()}")

# Check artifact generator
artifact_gen = tools_dir / "artifact_generator.py"
print(f"\n2. Artifact Generator:")
print(f"   ✓ artifact_generator.py exists: {artifact_gen.exists()}")

# Check modifications
lean_inv = investigator_dir / "lean_investigator.py"
print(f"\n3. lean_investigator.py:")
print(f"   ✓ File exists: {lean_inv.exists()}")
if lean_inv.exists():
    content = lean_inv.read_text()
    has_artifact_gen = "generate_all_artifacts" in content
    has_event_callback = "self.event_callback('artifact'" in content
    print(f"   ✓ Has artifact generation: {has_artifact_gen}")
    print(f"   ✓ Has WebSocket callback: {has_event_callback}")

# Check app.py modifications
app_py = backend_root / "app.py"
print(f"\n4. app.py (backend):")
print(f"   ✓ File exists: {app_py.exists()}")
if app_py.exists():
    content = app_py.read_text()
    has_static_files = "StaticFiles" in content
    has_mount = "app.mount" in content and "artifacts" in content
    print(f"   ✓ Has StaticFiles import: {has_static_files}")
    print(f"   ✓ Has artifacts mount: {has_mount}")

# Check libraries
print(f"\n5. Required Libraries:")
try:
    import pyvis
    print(f"   ✓ pyvis installed")
except ImportError:
    print(f"   ✗ pyvis NOT installed (run: uv pip install pyvis)")

try:
    import networkx
    print(f"   ✓ networkx installed")
except ImportError:
    print(f"   ✗ networkx NOT installed (run: uv pip install networkx)")

try:
    import plotly
    print(f"   ✓ plotly installed")
except ImportError:
    print(f"   ✗ plotly NOT installed (should already be there)")

print("\n" + "="*80)
print("✅ Setup verification complete!")
print("\n📋 Next Steps:")
print("   1. Start backend: python app.py")
print("   2. Start frontend: cd ../Frontend_v2 && npm run dev")
print("   3. Navigate to Investigative Journalist page")
print("   4. Run investigation: 'Investigate X for 3 iterations'")
print("   5. Check Artifacts tab when complete")
print("="*80)

