"""
Social Media Reel Generator (Text Animation)

Animates static infographics into engaging short videos (15-60s)
for Instagram Reels, TikTok, YouTube Shorts, etc.
"""

try:
    # MoviePy 2.x imports
    from moviepy import ImageClip, TextClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        # MoviePy 1.x fallback
        from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips, AudioFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        print("⚠️  MoviePy not available. Install with: uv pip install moviepy")
        MOVIEPY_AVAILABLE = False
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json


class ReelGenerator:
    """Animate infographics into social media reels"""
    
    # Standard reel dimensions
    FORMATS = {
        "instagram_reel": (1080, 1920),
        "tiktok": (1080, 1920),
        "youtube_shorts": (1080, 1920),
        "instagram_post": (1080, 1080),
    }
    
    # Animation presets
    ANIMATION_STYLES = {
        "typewriter": {"speed": 0.05, "cursor": True},
        "fade": {"duration": 0.8},
        "slide": {"duration": 0.6, "distance": 100},
        "zoom": {"duration": 0.8, "scale_factor": 1.2},
        "bounce": {"duration": 0.5, "bounce_height": 20}
    }
    
    def __init__(self, output_dir: str = "artifacts"):
        """
        Initialize reel generator
        
        Args:
            output_dir: Directory to save generated videos
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def animate_infographic(
        self,
        infographic_path: str,
        animation_config: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Animate static infographic into video reel
        
        Args:
            infographic_path: Path to infographic image
            animation_config: Animation configuration
                {
                    "duration": 15,  # Total video duration in seconds
                    "style": "fade",  # Animation style
                    "text_zones": [  # Text elements to animate
                        {
                            "text": "US Sentiment: +0.75",
                            "position": ("center", "center"),
                            "start": 0,
                            "duration": 3,
                            "fontsize": 70,
                            "color": "white"
                        }
                    ],
                    "background_music": None,  # Optional audio file path
                    "fps": 30,
                    "format": "instagram_reel"
                }
            output_path: Custom output path
        
        Returns:
            Dict with artifact info
        """
        # Validate infographic exists
        if not os.path.exists(infographic_path):
            raise FileNotFoundError(f"Infographic not found: {infographic_path}")
        
        # Get configuration
        duration = animation_config.get("duration", 15)
        style = animation_config.get("style", "fade")
        text_zones = animation_config.get("text_zones", [])
        bg_music = animation_config.get("background_music")
        fps = animation_config.get("fps", 30)
        format_name = animation_config.get("format", "instagram_reel")
        
        # Get dimensions
        if format_name not in self.FORMATS:
            format_name = "instagram_reel"
        width, height = self.FORMATS[format_name]
        
        print(f"🎬 Creating reel: {width}x{height}, {duration}s, {fps} fps")
        
        # Load background infographic (MoviePy 2.x: duration set in constructor)
        bg_clip = ImageClip(infographic_path, duration=duration)
        
        # Resize to fit format
        bg_clip = bg_clip.resized((width, height))
        
        # Create animated text overlays
        text_clips = []
        
        if text_zones:
            for i, zone in enumerate(text_zones):
                print(f"   📝 Animating text zone {i+1}/{len(text_zones)}: {zone.get('text', '')[:30]}...")
                
                text_clip = self._create_animated_text(
                    text=zone.get("text", ""),
                    position=zone.get("position", ("center", "center")),
                    start_time=zone.get("start", 0),
                    duration=zone.get("duration", 3),
                    fontsize=zone.get("fontsize", 60),
                    color=zone.get("color", "white"),
                    style=style,
                    canvas_size=(width, height)
                )
                
                if text_clip:
                    text_clips.append(text_clip)
        
        # Compose all clips
        all_clips = [bg_clip] + text_clips
        final_video = CompositeVideoClip(all_clips, size=(width, height))
        
        # Add background music if provided
        if bg_music and os.path.exists(bg_music):
            try:
                print(f"   🎵 Adding background music...")
                audio = AudioFileClip(bg_music, duration=duration)
                final_video = final_video.with_audio(audio)
            except Exception as e:
                print(f"   ⚠️  Could not add music: {e}")
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reel_{format_name}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, filename)
        
        # Write video file
        print(f"   💾 Rendering video to: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',
            audio_codec='aac' if bg_music else None,
            preset='medium'
        )
        
        print(f"   ✅ Reel created successfully!")
        
        # Return artifact info
        return {
            "artifact_id": f"reel_{datetime.now().timestamp()}",
            "type": "social_media_reel",
            "format": format_name,
            "duration_seconds": duration,
            "path": output_path,
            "dimensions": f"{width}x{height}",
            "fps": fps,
            "codec": "H.264",
            "size_bytes": os.path.getsize(output_path),
            "has_audio": bg_music is not None
        }
    
    def _create_animated_text(
        self,
        text: str,
        position: Tuple,
        start_time: float,
        duration: float,
        fontsize: int,
        color: str,
        style: str,
        canvas_size: Tuple[int, int]
    ) -> Optional[TextClip]:
        """Create an animated text clip"""
        try:
            # Create base text clip (MoviePy 2.x)
            txt_clip = TextClip(
                text=text,
                font_size=fontsize,
                color=color,
                font='Helvetica-Bold',
                size=(canvas_size[0] - 100, None),  # Max width with padding
                duration=duration
            )
            
            # Set timing
            txt_clip = txt_clip.with_start(start_time)
            
            # Set position
            if position == ("center", "center"):
                txt_clip = txt_clip.with_position("center")
            elif position == ("center", "top"):
                txt_clip = txt_clip.with_position(("center", 100))
            elif position == ("center", "bottom"):
                txt_clip = txt_clip.with_position(("center", canvas_size[1] - 200))
            else:
                txt_clip = txt_clip.with_position(position)
            
            # Apply animation style
            if style == "fade":
                txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
            elif style == "zoom":
                txt_clip = txt_clip.resized(lambda t: 1 + 0.3 * (t / duration))
            elif style == "slide":
                # Slide in from left
                txt_clip = txt_clip.with_position(
                    lambda t: (
                        max(50, canvas_size[0] // 2 - (canvas_size[0] // 2) * (t / 0.6)),
                        canvas_size[1] // 2
                    ) if t < 0.6 else ("center", "center")
                )
            
            return txt_clip
            
        except Exception as e:
            print(f"   ⚠️  Could not create text clip: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_multi_scene_reel(
        self,
        scenes: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        format_name: str = "instagram_reel"
    ) -> Dict[str, Any]:
        """
        Create a reel with multiple scenes/infographics
        
        Args:
            scenes: List of scene configs, each containing:
                {
                    "infographic_path": "path/to/image.png",
                    "duration": 5,
                    "text_overlays": [...]
                }
            output_path: Output file path
            format_name: Video format
        
        Returns:
            Artifact info dict
        """
        print(f"🎬 Creating multi-scene reel with {len(scenes)} scenes...")
        
        width, height = self.FORMATS.get(format_name, self.FORMATS["instagram_reel"])
        scene_clips = []
        
        for i, scene in enumerate(scenes):
            print(f"   🎞️  Processing scene {i+1}/{len(scenes)}...")
            
            # Load scene image
            img_path = scene.get("infographic_path")
            if not os.path.exists(img_path):
                print(f"   ⚠️  Scene image not found: {img_path}")
                continue
            
            scene_duration = scene.get("duration", 5)
            img_clip = ImageClip(img_path, duration=scene_duration)
            img_clip = img_clip.resized((width, height))
            
            # Add text overlays for this scene
            text_overlays = scene.get("text_overlays", [])
            text_clips = []
            
            for overlay in text_overlays:
                txt_clip = self._create_animated_text(
                    text=overlay.get("text", ""),
                    position=overlay.get("position", ("center", "center")),
                    start_time=overlay.get("start", 0),
                    duration=overlay.get("duration", scene_duration),
                    fontsize=overlay.get("fontsize", 60),
                    color=overlay.get("color", "white"),
                    style=overlay.get("style", "fade"),
                    canvas_size=(width, height)
                )
                if txt_clip:
                    text_clips.append(txt_clip)
            
            # Compose scene
            if text_clips:
                scene_clip = CompositeVideoClip([img_clip] + text_clips)
            else:
                scene_clip = img_clip
            
            # Add transition effects
            scene_clip = scene_clip.crossfadein(0.5).crossfadeout(0.5)
            
            scene_clips.append(scene_clip)
        
        # Concatenate all scenes
        if not scene_clips:
            raise ValueError("No valid scenes to create reel")
        
        print(f"   🔗 Concatenating {len(scene_clips)} scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reel_multiscene_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, filename)
        
        # Render
        print(f"   💾 Rendering final video...")
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            preset='medium'
        )
        
        print(f"   ✅ Multi-scene reel created!")
        
        return {
            "artifact_id": f"reel_multiscene_{datetime.now().timestamp()}",
            "type": "social_media_reel",
            "format": format_name,
            "num_scenes": len(scenes),
            "total_duration": final_video.duration,
            "path": output_path,
            "dimensions": f"{width}x{height}",
            "size_bytes": os.path.getsize(output_path)
        }


# Standalone test
if __name__ == "__main__":
    print("🎬 Testing Reel Generator...")
    print()
    
    # First, we need an infographic to animate
    # Check if test infographic exists
    test_infographic = "artifacts/infographic_instagram_post_minimalist_*.png"
    
    import glob
    infographic_files = glob.glob("artifacts/infographic_*.png")
    
    if not infographic_files:
        print("⚠️  No test infographics found!")
        print("Please run infographic_generator.py first to create test images.")
        exit(1)
    
    # Use the first infographic found
    test_img = infographic_files[0]
    print(f"📸 Using test infographic: {test_img}")
    print()
    
    generator = ReelGenerator(output_dir="artifacts")
    
    # Test 1: Simple animated reel with text overlays
    print("Test 1: Fade animation with text overlays")
    print("-" * 50)
    
    config_1 = {
        "duration": 10,
        "style": "fade",
        "text_zones": [
            {
                "text": "Political Sentiment Analysis",
                "position": ("center", "top"),
                "start": 0,
                "duration": 3,
                "fontsize": 70,
                "color": "#d9f378"
            },
            {
                "text": "Positive Trend: +75%",
                "position": ("center", "center"),
                "start": 3,
                "duration": 4,
                "fontsize": 90,
                "color": "white"
            },
            {
                "text": "Source: AI Analysis 2025",
                "position": ("center", "bottom"),
                "start": 7,
                "duration": 3,
                "fontsize": 40,
                "color": "#5d535c"
            }
        ],
        "fps": 30,
        "format": "instagram_reel"
    }
    
    try:
        result_1 = generator.animate_infographic(test_img, config_1)
        print(f"\n✅ Test 1 complete!")
        print(f"   Path: {result_1['path']}")
        print(f"   Size: {result_1['size_bytes'] / (1024*1024):.2f} MB")
        print(f"   Duration: {result_1['duration_seconds']}s")
        print()
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        print()
    
    # Test 2: Multi-scene reel
    if len(infographic_files) >= 2:
        print("Test 2: Multi-scene reel")
        print("-" * 50)
        
        scenes = [
            {
                "infographic_path": infographic_files[0],
                "duration": 4,
                "text_overlays": [
                    {
                        "text": "Scene 1: Overview",
                        "position": ("center", "top"),
                        "start": 0,
                        "duration": 4,
                        "fontsize": 60,
                        "color": "white",
                        "style": "fade"
                    }
                ]
            },
            {
                "infographic_path": infographic_files[1],
                "duration": 4,
                "text_overlays": [
                    {
                        "text": "Scene 2: Details",
                        "position": ("center", "top"),
                        "start": 0,
                        "duration": 4,
                        "fontsize": 60,
                        "color": "white",
                        "style": "fade"
                    }
                ]
            }
        ]
        
        try:
            result_2 = generator.create_multi_scene_reel(scenes)
            print(f"\n✅ Test 2 complete!")
            print(f"   Path: {result_2['path']}")
            print(f"   Scenes: {result_2['num_scenes']}")
            print(f"   Duration: {result_2['total_duration']:.1f}s")
            print()
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            print()
    
    print("🎉 Reel generator testing complete!")
    print(f"📁 Check the artifacts/ folder for generated videos")

