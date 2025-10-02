"""
Canva-Style Social Media Infographic Generator

Creates beautiful, shareable infographics for political analysis content.
Supports multiple platforms and templates with Aistra branding.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json


class InfographicGenerator:
    """Generate Canva-style social media infographics"""
    
    # Platform dimensions (width, height)
    PLATFORMS = {
        "instagram_post": (1080, 1080),
        "instagram_story": (1080, 1920),
        "linkedin": (1200, 627),
        "twitter": (1200, 675),
        "facebook": (1200, 630),
        "tiktok": (1080, 1920),
    }
    
    # Aistra color palette
    COLORS = {
        "primary": "#d9f378",      # Bright green
        "secondary": "#5d535c",    # Purple-gray
        "dark": "#333333",         # Dark gray
        "darkest": "#1c1e20",      # Almost black
        "white": "#FFFFFF",
        "light_gray": "#F5F5F5",
        "accent": "#00D9FF",       # Bright cyan for highlights
    }
    
    def __init__(self, output_dir: str = "artifacts"):
        """
        Initialize the infographic generator
        
        Args:
            output_dir: Directory to save generated infographics
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Try to load custom font, fall back to default if not available
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load fonts with fallback to PIL defaults"""
        fonts = {}
        
        try:
            # Try to load Roboto Flex (your specified font)
            fonts["title"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            fonts["subtitle"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
            fonts["body"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            fonts["stat_value"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 68)
            fonts["stat_label"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            fonts["footer"] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except Exception as e:
            print(f"⚠️  Could not load custom fonts, using default: {e}")
            # Use default fonts
            fonts["title"] = ImageFont.load_default()
            fonts["subtitle"] = ImageFont.load_default()
            fonts["body"] = ImageFont.load_default()
            fonts["stat_value"] = ImageFont.load_default()
            fonts["stat_label"] = ImageFont.load_default()
            fonts["footer"] = ImageFont.load_default()
        
        return fonts
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_social_post(
        self,
        data: Dict[str, Any],
        platform: str = "instagram_post",
        template: str = "minimalist",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a Canva-style infographic
        
        Args:
            data: Content data
                {
                    "title": "Main headline",
                    "subtitle": "Supporting text (optional)",
                    "stats": [
                        {"label": "Sentiment", "value": "+0.75", "color": "primary"},
                        {"label": "Sources", "value": "45", "color": "accent"}
                    ],
                    "chart_path": "path/to/chart.png",  # Optional
                    "footer": "Source: Analysis Date"
                }
            platform: Platform preset (instagram_post, linkedin, etc.)
            template: Design style (minimalist, data_heavy, story)
            output_path: Custom output path (optional)
        
        Returns:
            Dict with artifact info including path
        """
        # Get dimensions for platform
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}. Available: {list(self.PLATFORMS.keys())}")
        
        width, height = self.PLATFORMS[platform]
        
        # Create blank canvas
        canvas = Image.new('RGB', (width, height), self._hex_to_rgb(self.COLORS["darkest"]))
        draw = ImageDraw.Draw(canvas)
        
        # Apply template
        if template == "minimalist":
            canvas = self._apply_template_minimalist(canvas, draw, data, width, height)
        elif template == "data_heavy":
            canvas = self._apply_template_data_heavy(canvas, draw, data, width, height)
        elif template == "story":
            canvas = self._apply_template_story(canvas, draw, data, width, height)
        elif template == "dashboard":
            canvas = self._apply_template_dashboard(canvas, draw, data, width, height)
        elif template == "comparison":
            canvas = self._apply_template_comparison(canvas, draw, data, width, height)
        elif template == "timeline":
            canvas = self._apply_template_timeline(canvas, draw, data, width, height)
        elif template == "icon_grid":
            canvas = self._apply_template_icon_grid(canvas, draw, data, width, height)
        else:
            raise ValueError(f"Unknown template: {template}")
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infographic_{platform}_{template}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)
        
        # Save infographic
        canvas.save(output_path, "PNG", quality=95)
        
        # Return artifact info
        return {
            "artifact_id": f"infographic_{datetime.now().timestamp()}",
            "type": "social_media_infographic",
            "platform": platform,
            "template": template,
            "title": data.get("title", "Untitled"),
            "path": output_path,
            "dimensions": f"{width}x{height}",
            "format": "PNG",
            "size_bytes": os.path.getsize(output_path)
        }
    
    def _apply_template_minimalist(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Minimalist template: Clean design with focus on key message
        
        Layout:
        - Top: Primary accent bar
        - Center: Large title
        - Middle: 2-3 key stats in cards
        - Bottom: Footer
        """
        # Top accent bar (primary color)
        bar_height = height // 15
        draw.rectangle(
            [(0, 0), (width, bar_height)],
            fill=self._hex_to_rgb(self.COLORS["primary"])
        )
        
        # Title (centered, upper third)
        title = data.get("title", "Untitled")
        title_y = height // 4
        
        # Word wrap for title
        wrapped_title = self._wrap_text(title, self.fonts["title"], width - 120)
        title_height = self._draw_wrapped_text(
            draw, wrapped_title, (60, title_y),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["white"]),
            align="center", canvas_width=width
        )
        
        # Subtitle (if provided)
        if "subtitle" in data and data["subtitle"]:
            subtitle_y = title_y + title_height + 40
            wrapped_subtitle = self._wrap_text(data["subtitle"], self.fonts["subtitle"], width - 120)
            self._draw_wrapped_text(
                draw, wrapped_subtitle, (60, subtitle_y),
                self.fonts["subtitle"], self._hex_to_rgb(self.COLORS["light_gray"]),
                align="center", canvas_width=width
            )
        
        # Stats (horizontal cards in center)
        stats = data.get("stats", [])
        if stats:
            stats_y = height // 2
            self._draw_stat_cards(draw, stats, width, stats_y, card_style="minimal")
        
        # Chart (if provided)
        if "chart_path" in data and data["chart_path"] and os.path.exists(data["chart_path"]):
            chart_y = int(height * 0.65)
            self._embed_chart(canvas, data["chart_path"], width, chart_y, max_height=int(height * 0.2))
        
        # Footer
        footer = data.get("footer", f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        footer_y = height - 80
        self._draw_centered_text(
            draw, footer, (width // 2, footer_y),
            self.fonts["footer"], self._hex_to_rgb(self.COLORS["secondary"])
        )
        
        return canvas
    
    def _apply_template_data_heavy(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Data-heavy template: More stats, charts, detailed information
        
        Layout:
        - Header with title + gradient background
        - Grid of stat cards (2x2 or 2x3)
        - Large chart area
        - Footer with source
        """
        # Gradient background (dark to darker)
        for i in range(height // 3):
            alpha = i / (height // 3)
            color_top = self._hex_to_rgb(self.COLORS["dark"])
            color_bottom = self._hex_to_rgb(self.COLORS["darkest"])
            
            blended = tuple(int(color_top[j] * (1 - alpha) + color_bottom[j] * alpha) for j in range(3))
            draw.rectangle([(0, i * 3), (width, (i + 1) * 3)], fill=blended)
        
        # Title with background box
        title = data.get("title", "Untitled")
        title_box_height = 150
        draw.rectangle(
            [(0, 40), (width, 40 + title_box_height)],
            fill=self._hex_to_rgb(self.COLORS["primary"])
        )
        
        wrapped_title = self._wrap_text(title, self.fonts["title"], width - 80)
        self._draw_wrapped_text(
            draw, wrapped_title, (40, 70),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["darkest"]),
            align="left", canvas_width=width
        )
        
        # Stats grid (2x2)
        stats = data.get("stats", [])
        if stats:
            stats_start_y = 250
            self._draw_stat_grid(draw, stats, width, stats_start_y, rows=2, cols=2)
        
        # Chart
        if "chart_path" in data and data["chart_path"] and os.path.exists(data["chart_path"]):
            chart_y = int(height * 0.60)
            self._embed_chart(canvas, data["chart_path"], width, chart_y, max_height=int(height * 0.25))
        
        # Footer
        footer = data.get("footer", "")
        if footer:
            footer_y = height - 60
            self._draw_centered_text(
                draw, footer, (width // 2, footer_y),
                self.fonts["footer"], self._hex_to_rgb(self.COLORS["light_gray"])
            )
        
        return canvas
    
    def _apply_template_story(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Story template: Narrative-driven with flowing text
        
        Layout:
        - Vertical story format (good for Instagram stories)
        - Title at top
        - Key quote or stat in the middle
        - Context at bottom
        """
        # Background with accent gradient
        for i in range(height):
            alpha = i / height
            color_start = self._hex_to_rgb(self.COLORS["darkest"])
            color_end = self._hex_to_rgb(self.COLORS["dark"])
            blended = tuple(int(color_start[j] * (1 - alpha) + color_end[j] * alpha) for j in range(3))
            draw.line([(0, i), (width, i)], fill=blended, width=1)
        
        # Title (top)
        title = data.get("title", "Untitled")
        wrapped_title = self._wrap_text(title, self.fonts["title"], width - 100)
        title_height = self._draw_wrapped_text(
            draw, wrapped_title, (50, 100),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["primary"]),
            align="left", canvas_width=width
        )
        
        # Featured stat (center, large)
        stats = data.get("stats", [])
        if stats and len(stats) > 0:
            main_stat = stats[0]
            stat_y = height // 2 - 100
            
            # Draw stat in large format
            stat_value = main_stat.get("value", "")
            stat_label = main_stat.get("label", "")
            
            # Value (huge)
            bbox = draw.textbbox((0, 0), stat_value, font=self.fonts["stat_value"])
            text_width = bbox[2] - bbox[0]
            value_x = (width - text_width) // 2
            
            draw.text(
                (value_x, stat_y),
                stat_value,
                font=self.fonts["stat_value"],
                fill=self._hex_to_rgb(self.COLORS["primary"])
            )
            
            # Label (below value)
            label_y = stat_y + 100
            self._draw_centered_text(
                draw, stat_label, (width // 2, label_y),
                self.fonts["subtitle"], self._hex_to_rgb(self.COLORS["white"])
            )
        
        # Subtitle/context (bottom)
        if "subtitle" in data and data["subtitle"]:
            context_y = height - 250
            wrapped_context = self._wrap_text(data["subtitle"], self.fonts["body"], width - 100)
            self._draw_wrapped_text(
                draw, wrapped_context, (50, context_y),
                self.fonts["body"], self._hex_to_rgb(self.COLORS["light_gray"]),
                align="left", canvas_width=width
            )
        
        # Footer
        footer = data.get("footer", "")
        if footer:
            footer_y = height - 80
            self._draw_centered_text(
                draw, footer, (width // 2, footer_y),
                self.fonts["footer"], self._hex_to_rgb(self.COLORS["secondary"])
            )
        
        return canvas
    
    def _apply_template_dashboard(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Statistical Dashboard template: KPI-focused with multiple stats and charts
        
        Layout:
        - Top: Title
        - Row 1: 3-4 large KPI numbers
        - Row 2: Chart embed
        - Bottom: Key insight text
        """
        # Background with subtle gradient
        for i in range(height // 2):
            alpha = i / (height // 2)
            color_top = self._hex_to_rgb(self.COLORS["darkest"])
            color_mid = self._hex_to_rgb(self.COLORS["dark"])
            blended = tuple(int(color_top[j] * (1 - alpha) + color_mid[j] * alpha) for j in range(3))
            draw.line([(0, i), (width, i)], fill=blended, width=1)
        
        # Top accent strip
        draw.rectangle([(0, 0), (width, 8)], fill=self._hex_to_rgb(self.COLORS["primary"]))
        
        # Title
        title = data.get("title", "Dashboard")
        title_y = 40
        wrapped_title = self._wrap_text(title, self.fonts["title"], width - 80)
        self._draw_wrapped_text(
            draw, wrapped_title, (40, title_y),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["white"]),
            align="left", canvas_width=width
        )
        
        # Large KPI stats (horizontal row)
        stats = data.get("stats", [])
        if stats:
            kpi_y = 180
            num_kpis = min(len(stats), 4)
            kpi_width = (width - 100) // num_kpis
            
            for i, stat in enumerate(stats[:num_kpis]):
                x = 50 + i * kpi_width
                
                # Value (very large)
                value = str(stat.get("value", ""))
                bbox = draw.textbbox((0, 0), value, font=self.fonts["stat_value"])
                text_width = bbox[2] - bbox[0]
                value_x = x + (kpi_width - text_width) // 2
                
                # Color based on stat
                stat_color = self.COLORS.get(stat.get("color", "primary"), self.COLORS["primary"])
                draw.text(
                    (value_x, kpi_y),
                    value,
                    font=self.fonts["stat_value"],
                    fill=self._hex_to_rgb(stat_color)
                )
                
                # Label below
                label = stat.get("label", "")
                self._draw_centered_text(
                    draw, label, (x + kpi_width // 2, kpi_y + 90),
                    self.fonts["stat_label"], self._hex_to_rgb(self.COLORS["light_gray"])
                )
        
        # Chart area
        if "chart_path" in data and data["chart_path"] and os.path.exists(data["chart_path"]):
            chart_y = int(height * 0.50)
            self._embed_chart(canvas, data["chart_path"], width, chart_y, max_height=int(height * 0.28))
        
        # Key insight (bottom)
        if "subtitle" in data and data["subtitle"]:
            insight_y = height - 150
            wrapped_insight = self._wrap_text(data["subtitle"], self.fonts["body"], width - 100)
            self._draw_wrapped_text(
                draw, wrapped_insight, (50, insight_y),
                self.fonts["body"], self._hex_to_rgb(self.COLORS["white"]),
                align="left", canvas_width=width
            )
        
        # Footer
        footer = data.get("footer", "")
        if footer:
            self._draw_centered_text(
                draw, footer, (width // 2, height - 60),
                self.fonts["footer"], self._hex_to_rgb(self.COLORS["secondary"])
            )
        
        return canvas
    
    def _apply_template_comparison(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Comparison Split template: Side-by-side comparison with VS styling
        
        Layout:
        - Top: Title
        - Left half: Option A
        - Right half: Option B
        - Center: VS divider
        - Bottom: Conclusion
        """
        # Background
        draw.rectangle([(0, 0), (width, height)], fill=self._hex_to_rgb(self.COLORS["darkest"]))
        
        # Title
        title = data.get("title", "Comparison")
        self._draw_centered_text(
            draw, title, (width // 2, 60),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["white"])
        )
        
        # Split background colors
        draw.rectangle(
            [(0, 140), (width // 2 - 30, height - 120)],
            fill=self._hex_to_rgb(self.COLORS["dark"])
        )
        draw.rectangle(
            [(width // 2 + 30, 140), (width, height - 120)],
            fill=self._hex_to_rgb(self.COLORS["dark"])
        )
        
        # VS in center
        vs_y = height // 2 - 40
        draw.ellipse(
            [(width // 2 - 60, vs_y), (width // 2 + 60, vs_y + 120)],
            fill=self._hex_to_rgb(self.COLORS["primary"])
        )
        self._draw_centered_text(
            draw, "VS", (width // 2, vs_y + 60),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["darkest"])
        )
        
        # Get comparison data
        comparison = data.get("comparison", {})
        option_a = comparison.get("option_a", {})
        option_b = comparison.get("option_b", {})
        
        # Left side (Option A)
        a_title = option_a.get("title", "Option A")
        self._draw_centered_text(
            draw, a_title, (width // 4, 180),
            self.fonts["subtitle"], self._hex_to_rgb(self.COLORS["primary"])
        )
        
        # Option A stats
        a_stats = option_a.get("stats", [])
        if a_stats:
            y_offset = 240
            for stat in a_stats[:3]:
                text = f"• {stat.get('label', '')}: {stat.get('value', '')}"
                draw.text(
                    (40, y_offset),
                    text,
                    font=self.fonts["body"],
                    fill=self._hex_to_rgb(self.COLORS["white"])
                )
                y_offset += 50
        
        # Right side (Option B)
        b_title = option_b.get("title", "Option B")
        self._draw_centered_text(
            draw, b_title, (width * 3 // 4, 180),
            self.fonts["subtitle"], self._hex_to_rgb(self.COLORS["accent"])
        )
        
        # Option B stats
        b_stats = option_b.get("stats", [])
        if b_stats:
            y_offset = 240
            for stat in b_stats[:3]:
                text = f"• {stat.get('label', '')}: {stat.get('value', '')}"
                draw.text(
                    (width // 2 + 60, y_offset),
                    text,
                    font=self.fonts["body"],
                    fill=self._hex_to_rgb(self.COLORS["white"])
                )
                y_offset += 50
        
        # Conclusion
        conclusion = comparison.get("conclusion", data.get("footer", ""))
        if conclusion:
            self._draw_centered_text(
                draw, conclusion, (width // 2, height - 70),
                self.fonts["body"], self._hex_to_rgb(self.COLORS["primary"])
            )
        
        return canvas
    
    def _apply_template_timeline(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Timeline template: Chronological progression with event markers
        
        Layout:
        - Top: Title
        - Center: Horizontal timeline with events
        - Events alternate above/below line
        """
        # Background
        draw.rectangle([(0, 0), (width, height)], fill=self._hex_to_rgb(self.COLORS["darkest"]))
        
        # Title
        title = data.get("title", "Timeline")
        self._draw_centered_text(
            draw, title, (width // 2, 50),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["white"])
        )
        
        # Timeline line (horizontal center)
        timeline_y = height // 2
        draw.line(
            [(80, timeline_y), (width - 80, timeline_y)],
            fill=self._hex_to_rgb(self.COLORS["primary"]),
            width=4
        )
        
        # Get timeline events
        events = data.get("timeline", [])
        if not events and "stats" in data:
            # Fallback: use stats as events
            events = [{"date": stat.get("label", ""), "event": stat.get("value", "")} 
                     for stat in data.get("stats", [])]
        
        if events:
            num_events = len(events)
            spacing = (width - 160) // max(num_events - 1, 1)
            
            for i, event in enumerate(events):
                x = 80 + i * spacing
                
                # Event marker (circle)
                draw.ellipse(
                    [(x - 15, timeline_y - 15), (x + 15, timeline_y + 15)],
                    fill=self._hex_to_rgb(self.COLORS["primary"])
                )
                
                # Date
                date = event.get("date", f"Event {i+1}")
                self._draw_centered_text(
                    draw, date, (x, timeline_y - 60),
                    self.fonts["stat_label"], self._hex_to_rgb(self.COLORS["primary"])
                )
                
                # Event description (alternate above/below)
                event_text = event.get("event", "")
                if event_text:
                    if i % 2 == 0:
                        # Above timeline
                        wrapped = self._wrap_text(event_text, self.fonts["footer"], 180)
                        y_pos = timeline_y - 120
                    else:
                        # Below timeline
                        wrapped = self._wrap_text(event_text, self.fonts["footer"], 180)
                        y_pos = timeline_y + 40
                    
                    for line in wrapped[:2]:  # Max 2 lines
                        self._draw_centered_text(
                            draw, line, (x, y_pos),
                            self.fonts["footer"], self._hex_to_rgb(self.COLORS["white"])
                        )
                        y_pos += 24
        
        # Footer
        footer = data.get("footer", "")
        if footer:
            self._draw_centered_text(
                draw, footer, (width // 2, height - 40),
                self.fonts["footer"], self._hex_to_rgb(self.COLORS["secondary"])
            )
        
        return canvas
    
    def _apply_template_icon_grid(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        data: Dict,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Icon Grid template: Grid of stats with large numbers and icons
        
        Layout:
        - Top: Title
        - Center: 2x3 or 3x3 grid of stat boxes
        - Each box: Number + Label
        """
        # Background
        draw.rectangle([(0, 0), (width, height)], fill=self._hex_to_rgb(self.COLORS["darkest"]))
        
        # Title
        title = data.get("title", "Key Statistics")
        title_y = 50
        self._draw_centered_text(
            draw, title, (width // 2, title_y),
            self.fonts["title"], self._hex_to_rgb(self.COLORS["primary"])
        )
        
        # Grid configuration
        stats = data.get("stats", [])
        num_stats = len(stats)
        
        if num_stats <= 4:
            cols, rows = 2, 2
        elif num_stats <= 6:
            cols, rows = 3, 2
        else:
            cols, rows = 3, 3
        
        # Grid dimensions
        grid_start_y = 150
        grid_height = height - grid_start_y - 100
        cell_width = (width - 100) // cols
        cell_height = grid_height // rows
        
        # Draw grid cells
        for i, stat in enumerate(stats[:cols * rows]):
            row = i // cols
            col = i % cols
            
            x = 50 + col * cell_width
            y = grid_start_y + row * cell_height
            
            # Cell background (subtle)
            padding = 15
            draw.rounded_rectangle(
                [(x + padding, y + padding), 
                 (x + cell_width - padding, y + cell_height - padding)],
                radius=20,
                fill=self._hex_to_rgb(self.COLORS["dark"])
            )
            
            # Large number (center top of cell)
            value = str(stat.get("value", ""))
            bbox = draw.textbbox((0, 0), value, font=self.fonts["stat_value"])
            text_width = bbox[2] - bbox[0]
            value_x = x + (cell_width - text_width) // 2
            value_y = y + cell_height // 3
            
            stat_color = self.COLORS.get(stat.get("color", "primary"), self.COLORS["primary"])
            draw.text(
                (value_x, value_y),
                value,
                font=self.fonts["stat_value"],
                fill=self._hex_to_rgb(stat_color)
            )
            
            # Label (center bottom of cell)
            label = stat.get("label", "")
            self._draw_centered_text(
                draw, label, (x + cell_width // 2, y + cell_height * 2 // 3 + 20),
                self.fonts["stat_label"], self._hex_to_rgb(self.COLORS["white"])
            )
        
        # Footer
        footer = data.get("footer", "")
        if footer:
            self._draw_centered_text(
                draw, footer, (width // 2, height - 50),
                self.fonts["footer"], self._hex_to_rgb(self.COLORS["secondary"])
            )
        
        return canvas
    
    def _draw_stat_cards(
        self,
        draw: ImageDraw.Draw,
        stats: List[Dict],
        canvas_width: int,
        y_position: int,
        card_style: str = "minimal"
    ):
        """Draw horizontal stat cards"""
        num_stats = len(stats)
        if num_stats == 0:
            return
        
        card_width = (canvas_width - 120 - (num_stats - 1) * 30) // num_stats
        card_height = 160
        
        for i, stat in enumerate(stats):
            x = 60 + i * (card_width + 30)
            
            # Card background
            color = self.COLORS.get(stat.get("color", "secondary"), self.COLORS["secondary"])
            draw.rectangle(
                [(x, y_position), (x + card_width, y_position + card_height)],
                fill=self._hex_to_rgb(color)
            )
            
            # Stat value (centered)
            value = str(stat.get("value", ""))
            bbox = draw.textbbox((0, 0), value, font=self.fonts["stat_value"])
            text_width = bbox[2] - bbox[0]
            value_x = x + (card_width - text_width) // 2
            value_y = y_position + 30
            
            draw.text(
                (value_x, value_y),
                value,
                font=self.fonts["stat_value"],
                fill=self._hex_to_rgb(self.COLORS["darkest"])
            )
            
            # Stat label (centered below)
            label = stat.get("label", "")
            label_y = value_y + 85
            self._draw_centered_text(
                draw, label, (x + card_width // 2, label_y),
                self.fonts["stat_label"], self._hex_to_rgb(self.COLORS["darkest"])
            )
    
    def _draw_stat_grid(
        self,
        draw: ImageDraw.Draw,
        stats: List[Dict],
        canvas_width: int,
        start_y: int,
        rows: int = 2,
        cols: int = 2
    ):
        """Draw stats in a grid layout"""
        card_width = (canvas_width - 80 - 30) // cols
        card_height = 140
        
        for i, stat in enumerate(stats[:rows * cols]):
            row = i // cols
            col = i % cols
            
            x = 40 + col * (card_width + 30)
            y = start_y + row * (card_height + 30)
            
            # Card background
            color = self.COLORS.get(stat.get("color", "secondary"), self.COLORS["secondary"])
            draw.rounded_rectangle(
                [(x, y), (x + card_width, y + card_height)],
                radius=15,
                fill=self._hex_to_rgb(color)
            )
            
            # Value
            value = str(stat.get("value", ""))
            self._draw_centered_text(
                draw, value, (x + card_width // 2, y + 35),
                self.fonts["stat_value"], self._hex_to_rgb(self.COLORS["darkest"])
            )
            
            # Label
            label = stat.get("label", "")
            self._draw_centered_text(
                draw, label, (x + card_width // 2, y + 100),
                self.fonts["stat_label"], self._hex_to_rgb(self.COLORS["darkest"])
            )
    
    def _embed_chart(
        self,
        canvas: Image.Image,
        chart_path: str,
        canvas_width: int,
        y_position: int,
        max_height: int
    ):
        """Embed a chart image into the canvas"""
        try:
            chart = Image.open(chart_path)
            
            # Resize to fit
            chart_width = canvas_width - 120
            aspect_ratio = chart.height / chart.width
            chart_height = min(int(chart_width * aspect_ratio), max_height)
            chart = chart.resize((chart_width, chart_height), Image.Resampling.LANCZOS)
            
            # Paste at center
            x = (canvas_width - chart_width) // 2
            canvas.paste(chart, (x, y_position))
        except Exception as e:
            print(f"⚠️  Could not embed chart: {e}")
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width > max_width:
                if len(current_line) == 1:
                    lines.append(current_line[0])
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_wrapped_text(
        self,
        draw: ImageDraw.Draw,
        lines: List[str],
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int],
        align: str = "left",
        canvas_width: int = 0
    ) -> int:
        """Draw wrapped text and return total height"""
        x, y = position
        line_height = font.size + 10
        
        for line in lines:
            if align == "center" and canvas_width > 0:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (canvas_width - text_width) // 2
            
            draw.text((x, y), line, font=font, fill=color)
            y += line_height
        
        return len(lines) * line_height
    
    def _draw_centered_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int]
    ):
        """Draw text centered at position"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = position[0] - text_width // 2
        y = position[1] - text_height // 2
        
        draw.text((x, y), text, font=font, fill=color)


# Standalone test
if __name__ == "__main__":
    print("🎨 Testing Infographic Generator...")
    print()
    
    generator = InfographicGenerator(output_dir="artifacts")
    
    # Test data
    test_data = {
        "title": "US Climate Policy Sentiment",
        "subtitle": "Public opinion analysis across 50 states",
        "stats": [
            {"label": "Sentiment", "value": "+0.75", "color": "primary"},
            {"label": "Sources", "value": "45", "color": "accent"},
            {"label": "Countries", "value": "5", "color": "secondary"}
        ],
        "footer": "Analysis Date: Oct 2, 2025 | Source: Political Analyst AI"
    }
    
    # Test all templates and platforms
    templates = ["minimalist", "data_heavy", "story"]
    platforms = ["instagram_post", "instagram_story", "linkedin"]
    
    results = []
    
    for template in templates:
        for platform in platforms:
            print(f"📊 Generating {platform} - {template}...")
            
            try:
                result = generator.create_social_post(
                    data=test_data,
                    platform=platform,
                    template=template
                )
                
                results.append(result)
                print(f"   ✅ Created: {result['path']}")
                print(f"   Size: {result['size_bytes'] / 1024:.1f} KB")
                print()
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
    
    print(f"\n🎉 Generated {len(results)} infographics!")
    print(f"📁 Output directory: artifacts/")
    print()
    
    # Save results summary
    summary_path = "artifacts/infographic_test_results.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Test results saved to: {summary_path}")

