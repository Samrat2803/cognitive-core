"""
HTML Infographic Renderer

Takes structured schema data + template choice → Generates beautiful HTML infographic

Flow:
1. Agent creates data using schema (e.g., KeyMetricsDashboard)
2. Agent chooses visual template (e.g., 'gradient_modern')
3. Renderer maps schema data to template placeholders
4. Outputs HTML file (and optionally converts to PNG)
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

# Try relative import first (when called as module), then absolute
try:
    from .infographic_schemas import (
        INFOGRAPHIC_SCHEMAS,
        KeyMetricsDashboard,
        ComparisonView,
        TimelineProgression,
        RankingLeaderboard,
        HeroStat,
        CategoryBreakdown
    )
except ImportError:
    from infographic_schemas import (
        INFOGRAPHIC_SCHEMAS,
        KeyMetricsDashboard,
        ComparisonView,
        TimelineProgression,
        RankingLeaderboard,
        HeroStat,
        CategoryBreakdown
    )


class HTMLInfographicRenderer:
    """Render schema data into HTML templates"""
    
    # Available visual templates
    VISUAL_TEMPLATES = [
        "gradient_modern",      # Template 1: Purple glassmorphism
        "minimalist_mono",      # Template 2: Black & white editorial
        "vibrant_cards",        # Template 3: Colorful gradient cards
        "neon_dark",            # Template 4: Cyberpunk/Matrix
        "clean_corporate",      # Template 5: Professional blue/white
        "playful_rounded"       # Template 6: Fun bubble design
    ]
    
    def __init__(self, templates_dir: str = "templates/html_samples", output_dir: str = "artifacts"):
        """
        Initialize renderer
        
        Args:
            templates_dir: Where HTML templates are stored
            output_dir: Where to save generated infographics
        """
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render(
        self,
        schema_data: Any,  # Pydantic model instance
        visual_template: str,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Render schema data into HTML infographic
        
        Args:
            schema_data: Validated Pydantic schema instance (e.g., KeyMetricsDashboard instance)
            visual_template: Template name (e.g., 'gradient_modern')
            output_filename: Optional custom filename
        
        Returns:
            Artifact info dict with path to generated HTML
        """
        # Validate template choice
        if visual_template not in self.VISUAL_TEMPLATES:
            raise ValueError(f"Unknown template: {visual_template}. Valid: {self.VISUAL_TEMPLATES}")
        
        # Load template
        template_path = self.templates_dir / f"template_{self.VISUAL_TEMPLATES.index(visual_template) + 1}_{visual_template}.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            html_template = f.read()
        
        # Map schema data to template placeholders
        placeholder_map = self._map_schema_to_placeholders(schema_data)
        
        # Replace placeholders
        html_output = html_template
        for placeholder, value in placeholder_map.items():
            html_output = html_output.replace(f"{{{{{placeholder}}}}}", str(value))
        
        # Generate output filename
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            schema_type = schema_data.__class__.__name__.lower()
            output_filename = f"infographic_{schema_type}_{visual_template}_{timestamp}.html"
        
        output_path = self.output_dir / output_filename
        
        # Save HTML
        with open(output_path, 'w') as f:
            f.write(html_output)
        
        # Extract artifact_id from filename (without .html extension)
        artifact_id = output_filename.replace('.html', '')
        
        return {
            "artifact_id": artifact_id,
            "type": "html_infographic",
            "schema_type": schema_data.__class__.__name__,
            "visual_template": visual_template,
            "path": str(output_path),
            "size_bytes": os.path.getsize(output_path)
        }
    
    def _map_schema_to_placeholders(self, schema_data: Any) -> Dict[str, str]:
        """
        Map schema data to template placeholders
        
        Different schemas map differently to the same placeholder names.
        This ensures any schema can work with any template.
        """
        schema_type = schema_data.__class__.__name__
        
        if isinstance(schema_data, KeyMetricsDashboard):
            return self._map_key_metrics(schema_data)
        elif isinstance(schema_data, ComparisonView):
            return self._map_comparison(schema_data)
        elif isinstance(schema_data, TimelineProgression):
            return self._map_timeline(schema_data)
        elif isinstance(schema_data, RankingLeaderboard):
            return self._map_ranking(schema_data)
        elif isinstance(schema_data, HeroStat):
            return self._map_hero_stat(schema_data)
        elif isinstance(schema_data, CategoryBreakdown):
            return self._map_category_breakdown(schema_data)
        else:
            raise ValueError(f"Unknown schema type: {schema_type}")
    
    def _map_key_metrics(self, data: KeyMetricsDashboard) -> Dict[str, str]:
        """Map KeyMetricsDashboard to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": data.subtitle,
            "INSIGHT_TEXT": data.insight or "",
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map metrics to STAT1, STAT2, etc.
        for i, metric in enumerate(data.metrics, 1):
            mapping[f"STAT{i}_VALUE"] = metric.value
            mapping[f"STAT{i}_LABEL"] = metric.label
        
        # Fill remaining stat slots with empty strings (for templates with more slots)
        for i in range(len(data.metrics) + 1, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping
    
    def _map_comparison(self, data: ComparisonView) -> Dict[str, str]:
        """Map ComparisonView to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": data.subtitle,
            "INSIGHT_TEXT": data.conclusion or "",
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map left side metrics
        for i, metric in enumerate(data.left_side.metrics, 1):
            mapping[f"STAT{i}_VALUE"] = metric.value
            mapping[f"STAT{i}_LABEL"] = f"{data.left_side.title}: {metric.label}"
        
        # Map right side metrics (continue numbering)
        offset = len(data.left_side.metrics)
        for i, metric in enumerate(data.right_side.metrics, 1):
            mapping[f"STAT{offset + i}_VALUE"] = metric.value
            mapping[f"STAT{offset + i}_LABEL"] = f"{data.right_side.title}: {metric.label}"
        
        # Fill remaining
        total_metrics = len(data.left_side.metrics) + len(data.right_side.metrics)
        for i in range(total_metrics + 1, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping
    
    def _map_timeline(self, data: TimelineProgression) -> Dict[str, str]:
        """Map TimelineProgression to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": data.subtitle,
            "INSIGHT_TEXT": data.trend or "",
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map timeline points
        for i, point in enumerate(data.timeline_points, 1):
            mapping[f"STAT{i}_VALUE"] = point.value
            mapping[f"STAT{i}_LABEL"] = f"{point.date}: {point.label}"
        
        # Fill remaining
        for i in range(len(data.timeline_points) + 1, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping
    
    def _map_ranking(self, data: RankingLeaderboard) -> Dict[str, str]:
        """Map RankingLeaderboard to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": data.subtitle,
            "INSIGHT_TEXT": data.methodology or "",
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map ranked items
        for i, item in enumerate(data.ranked_items, 1):
            change_indicator = f" {item.change}" if item.change else ""
            mapping[f"STAT{i}_VALUE"] = item.score
            mapping[f"STAT{i}_LABEL"] = f"#{item.rank} {item.name}{change_indicator}"
        
        # Fill remaining
        for i in range(len(data.ranked_items) + 1, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping
    
    def _map_hero_stat(self, data: HeroStat) -> Dict[str, str]:
        """Map HeroStat to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": data.hero_label,
            "STAT1_VALUE": data.hero_value,
            "STAT1_LABEL": data.hero_label,
            "INSIGHT_TEXT": data.context,
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map supporting stats
        if data.supporting_stats:
            for i, stat in enumerate(data.supporting_stats, 2):  # Start at 2
                mapping[f"STAT{i}_VALUE"] = stat.value
                mapping[f"STAT{i}_LABEL"] = stat.label
        
        # Fill remaining
        start_idx = 2 + (len(data.supporting_stats) if data.supporting_stats else 0)
        for i in range(start_idx, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping
    
    def _map_category_breakdown(self, data: CategoryBreakdown) -> Dict[str, str]:
        """Map CategoryBreakdown to template placeholders"""
        mapping = {
            "TITLE": data.title,
            "SUBTITLE": f"{data.breakdown_type} - {data.subtitle}",
            "INSIGHT_TEXT": data.insight or "",
            "FOOTER_TEXT": data.footer,
            "DATE": datetime.now().strftime("%B %d, %Y")
        }
        
        # Map categories
        for i, category in enumerate(data.categories, 1):
            percentage_str = f" ({category.percentage})" if category.percentage else ""
            mapping[f"STAT{i}_VALUE"] = category.value
            mapping[f"STAT{i}_LABEL"] = f"{category.name}{percentage_str}"
        
        # Fill remaining
        for i in range(len(data.categories) + 1, 10):
            mapping[f"STAT{i}_VALUE"] = "—"
            mapping[f"STAT{i}_LABEL"] = ""
        
        return mapping


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("🎨 HTML Infographic Renderer - Demo")
    print("=" * 70)
    print()
    
    # Initialize renderer
    renderer = HTMLInfographicRenderer()
    
    # Example 1: Key Metrics Dashboard in Gradient Modern style
    print("📊 Example 1: Key Metrics Dashboard → Gradient Modern")
    print("-" * 70)
    
    metrics_data = KeyMetricsDashboard(
        title="US Climate Policy Sentiment",
        subtitle="Real-time Analysis Across Media Sources",
        metrics=[
            {"value": "72%", "label": "Overall Support"},
            {"value": "1.2M", "label": "Articles Analyzed"},
            {"value": "+15%", "label": "Weekly Change"},
            {"value": "28", "label": "Countries Tracked"}
        ],
        insight="Public sentiment shows strong support for renewable energy initiatives.",
        footer="Generated by Political Analysis AI • Oct 2, 2025"
    )
    
    result1 = renderer.render(
        schema_data=metrics_data,
        visual_template="gradient_modern"
    )
    
    print(f"✅ Generated: {result1['path']}")
    print(f"   Schema: {result1['schema_type']}")
    print(f"   Template: {result1['visual_template']}")
    print(f"   Size: {result1['size_bytes'] / 1024:.1f} KB")
    print()
    
    # Example 2: Same data, different template
    print("📊 Example 2: SAME DATA → Minimalist Monochrome")
    print("-" * 70)
    
    result2 = renderer.render(
        schema_data=metrics_data,  # Same data!
        visual_template="minimalist_mono"  # Different style!
    )
    
    print(f"✅ Generated: {result2['path']}")
    print(f"   Schema: {result2['schema_type']}")
    print(f"   Template: {result2['visual_template']}")
    print(f"   Size: {result2['size_bytes'] / 1024:.1f} KB")
    print()
    
    # Example 3: Comparison schema in Neon Dark style
    print("⚖️  Example 3: Comparison View → Neon Dark")
    print("-" * 70)
    
    comparison_data = ComparisonView(
        title="Media Bias: CNN vs Fox News",
        subtitle="Coverage of Climate Policy",
        left_side={
            "title": "CNN",
            "metrics": [
                {"value": "68%", "label": "Positive Coverage"},
                {"value": "1,240", "label": "Articles"}
            ]
        },
        right_side={
            "title": "Fox News",
            "metrics": [
                {"value": "34%", "label": "Positive Coverage"},
                {"value": "980", "label": "Articles"}
            ]
        },
        conclusion="34-point sentiment gap between outlets",
        footer="Media Bias Detector • Oct 2, 2025"
    )
    
    result3 = renderer.render(
        schema_data=comparison_data,
        visual_template="neon_dark"
    )
    
    print(f"✅ Generated: {result3['path']}")
    print(f"   Schema: {result3['schema_type']}")
    print(f"   Template: {result3['visual_template']}")
    print(f"   Size: {result3['size_bytes'] / 1024:.1f} KB")
    print()
    
    print("🎉 Renderer Demo Complete!")
    print()
    print("Key Concepts:")
    print("  • Same schema → Different visual templates")
    print("  • Agents only need to know schema structure")
    print("  • Visual style is a separate choice")
    print("  • All 6 schemas work with all 6 templates")
    print()
    print(f"Generated files in: {renderer.output_dir}/")
    print()
    print("To view:")
    print(f"  open {result1['path']}")
    print(f"  open {result2['path']}")
    print(f"  open {result3['path']}")

