"""
Simple test for Reel Generator (without text animations)
"""

import glob
from reel_generator import ReelGenerator

print("🎬 Simple Reel Generator Test (No Text Animations)")
print("=" * 60)
print()

# Find test infographics
infographic_files = glob.glob("artifacts/infographic_*.png")

if not infographic_files:
    print("❌ No test infographics found!")
    print("Run: python infographic_generator.py")
    exit(1)

print(f"📸 Found {len(infographic_files)} infographics")
print()

generator = ReelGenerator(output_dir="artifacts")

# Test: Simple video with just the background image (no text overlays)
print("Test: Basic reel with background image only")
print("-" * 60)

test_img = infographic_files[0]
print(f"Using: {test_img}")

config = {
    "duration": 5,  # Short duration for quick test
    "style": "fade",
    "text_zones": [],  # NO TEXT - just test the video creation
    "fps": 15,  # Lower FPS for faster rendering
    "format": "instagram_post"  # Square format
}

try:
    result = generator.animate_infographic(test_img, config)
    
    print(f"\n✅ Test passed!")
    print(f"   Video: {result['path']}")
    print(f"   Duration: {result['duration_seconds']}s")
    print(f"   Size: {result['size_bytes'] / (1024*1024):.2f} MB")
    print(f"   Format: {result['format']}")
    print()
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    print()

print("🎉 Simple test complete!")

