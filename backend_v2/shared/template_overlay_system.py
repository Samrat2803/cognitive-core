"""
Template Overlay System - Use Downloaded Professional Templates

This system allows you to use actual template images from popular platforms
(Venngage, Canva, Freepik, etc.) and overlay your data on them.

How it works:
1. Download template images from popular platforms
2. Define overlay zones (where to place your data)
3. System composites your data onto the template
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json


class TemplateOverlaySystem:
    """Overlay data onto professional template images"""
    
    def __init__(self, template_dir: str = "templates/downloaded", output_dir: str = "artifacts"):
        """
        Initialize the template overlay system
        
        Args:
            template_dir: Directory containing downloaded template images
            output_dir: Where to save final infographics
        """
        self.template_dir = template_dir
        self.output_dir = output_dir
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Load fonts
        try:
            self.font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            self.font_normal = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            self.font_bold = ImageFont.load_default()
            self.font_normal = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def apply_data_to_template(
        self,
        template_path: str,
        overlay_config: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply data overlay to a template image
        
        Args:
            template_path: Path to downloaded template image
            overlay_config: Configuration for data placement
                {
                    "zones": [
                        {
                            "type": "text",
                            "position": (100, 100),  # x, y coordinates
                            "text": "Your Title Here",
                            "font_size": 60,
                            "color": "#FFFFFF",
                            "max_width": 800
                        },
                        {
                            "type": "number",
                            "position": (200, 300),
                            "value": "75%",
                            "font_size": 80,
                            "color": "#00FF00"
                        }
                    ]
                }
            output_path: Where to save (optional)
        
        Returns:
            Artifact info dict
        """
        # Load template
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        template = Image.open(template_path)
        template = template.convert('RGBA')  # Ensure RGBA for transparency
        
        # Create overlay layer
        overlay = Image.new('RGBA', template.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Apply each zone
        zones = overlay_config.get("zones", [])
        
        for zone in zones:
            zone_type = zone.get("type", "text")
            position = zone.get("position", (0, 0))
            color = self._hex_to_rgba(zone.get("color", "#FFFFFF"))
            
            if zone_type == "text":
                text = zone.get("text", "")
                font_size = zone.get("font_size", 36)
                max_width = zone.get("max_width", template.width - position[0] - 50)
                
                font = self._get_font(font_size)
                
                # Word wrap if needed
                if max_width:
                    text = self._wrap_text_simple(text, font, max_width, draw)
                
                draw.text(position, text, font=font, fill=color)
            
            elif zone_type == "number":
                value = str(zone.get("value", ""))
                font_size = zone.get("font_size", 60)
                font = self._get_font(font_size)
                draw.text(position, value, font=font, fill=color)
            
            elif zone_type == "label":
                label = zone.get("label", "")
                font_size = zone.get("font_size", 24)
                font = self._get_font(font_size)
                draw.text(position, label, font=font, fill=color)
            
            elif zone_type == "box":
                # Draw colored box
                box_size = zone.get("size", (200, 100))
                end_pos = (position[0] + box_size[0], position[1] + box_size[1])
                draw.rectangle([position, end_pos], fill=color)
        
        # Composite overlay onto template
        final = Image.alpha_composite(template, overlay)
        final = final.convert('RGB')  # Convert back to RGB for saving
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            template_name = os.path.splitext(os.path.basename(template_path))[0]
            filename = f"overlay_{template_name}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)
        
        # Save
        final.save(output_path, "PNG", quality=95)
        
        return {
            "artifact_id": f"template_overlay_{datetime.now().timestamp()}",
            "type": "template_overlay",
            "template_used": os.path.basename(template_path),
            "path": output_path,
            "size_bytes": os.path.getsize(output_path)
        }
    
    def list_available_templates(self) -> List[str]:
        """List all downloaded templates"""
        templates = []
        for file in os.listdir(self.template_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                templates.append(os.path.join(self.template_dir, file))
        return templates
    
    def create_template_config_helper(self, template_path: str) -> Dict:
        """
        Create a template configuration helper
        Shows template dimensions to help you define overlay zones
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        img = Image.open(template_path)
        
        return {
            "template": os.path.basename(template_path),
            "width": img.width,
            "height": img.height,
            "sample_config": {
                "zones": [
                    {
                        "type": "text",
                        "position": (img.width // 4, 100),  # Top quarter
                        "text": "Main Title Here",
                        "font_size": 60,
                        "color": "#FFFFFF",
                        "max_width": img.width // 2
                    },
                    {
                        "type": "number",
                        "position": (img.width // 2 - 100, img.height // 2),  # Center
                        "value": "75%",
                        "font_size": 80,
                        "color": "#00FF00"
                    },
                    {
                        "type": "label",
                        "position": (img.width // 2 - 50, img.height // 2 + 100),
                        "label": "Approval Rating",
                        "font_size": 32,
                        "color": "#CCCCCC"
                    }
                ]
            },
            "instructions": f"""
Template loaded: {img.width}x{img.height}

To use this template:
1. Define overlay zones with positions (x, y)
2. Positions are in pixels from top-left (0, 0)
3. Template width: {img.width}, height: {img.height}
4. Common positions:
   - Top left: (50, 50)
   - Top center: ({img.width//2}, 50)
   - Center: ({img.width//2}, {img.height//2})
   - Bottom: ({img.width//2}, {img.height - 100})
"""
        }
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font of specific size"""
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, alpha)
    
    def _wrap_text_simple(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> str:
        """Simple word wrap"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)


# Standalone test & usage example
if __name__ == "__main__":
    print("🎨 Template Overlay System - Usage Guide")
    print("=" * 70)
    print()
    
    system = TemplateOverlaySystem()
    
    # Check for available templates
    templates = system.list_available_templates()
    
    if not templates:
        print("📥 No templates found!")
        print()
        print("To use this system:")
        print("1. Download professional templates from:")
        print("   - Venngage: https://venngage.com/templates/infographics")
        print("   - Canva: https://www.canva.com/templates/infographics/")
        print("   - Freepik: https://www.freepik.com/free-photos-vectors/infographic")
        print("   - Visme: https://www.visme.co/templates/infographics/")
        print()
        print("2. Save them as PNG/JPG in: backend_v2/shared/templates/downloaded/")
        print()
        print("3. Run this script again to use them!")
        print()
        print(f"Template directory: {system.template_dir}")
        
    else:
        print(f"✅ Found {len(templates)} template(s):")
        for i, t in enumerate(templates, 1):
            print(f"   {i}. {os.path.basename(t)}")
        print()
        
        # Use first template as example
        template = templates[0]
        print(f"📊 Analyzing template: {os.path.basename(template)}")
        print()
        
        config_helper = system.create_template_config_helper(template)
        print(config_helper["instructions"])
        
        # Create example overlay
        print("🎨 Creating example overlay...")
        
        overlay_config = {
            "zones": [
                {
                    "type": "text",
                    "position": (100, 100),
                    "text": "Political Sentiment Analysis",
                    "font_size": 60,
                    "color": "#FFFFFF",
                    "max_width": config_helper["width"] - 200
                },
                {
                    "type": "number",
                    "position": (config_helper["width"] // 2 - 100, config_helper["height"] // 2),
                    "value": "75%",
                    "font_size": 100,
                    "color": "#00FF00"
                },
                {
                    "type": "label",
                    "position": (config_helper["width"] // 2 - 80, config_helper["height"] // 2 + 120),
                    "label": "Approval Rating",
                    "font_size": 36,
                    "color": "#FFFFFF"
                }
            ]
        }
        
        result = system.apply_data_to_template(template, overlay_config)
        
        print(f"✅ Created overlay: {result['path']}")
        print(f"   Size: {result['size_bytes'] / 1024:.1f} KB")
        print()
        print("🎉 Open the file to see your data on the professional template!")

