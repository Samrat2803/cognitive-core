"""
Visualization Tools for Political Analyst Agent

Template-based, minimalistic, auto-styled visualizations with export to HTML and PNG.

Features:
- Bar Charts: Categorical comparisons
- Line Charts: Trend analysis
- Mind Maps: Hierarchical concepts (Graphviz/Plotly)
- Map Charts: Geographic/choropleth maps
- Auto-detection: Smart chart selection

Quick Start:
    >>> from langgraph_master_agent.tools.visualization_tools import create_bar_chart, create_map_chart
    >>> 
    >>> artifact = create_bar_chart(
    ...     data={"categories": ["US", "EU", "China"], "values": [85, 72, 45]},
    ...     title="Global Sentiment"
    ... )
    >>> 
    >>> map_artifact = create_map_chart(
    ...     data={"countries": ["US", "Israel"], "values": [-0.4, -0.7]},
    ...     title="Sentiment Map"
    ... )

See README_VISUALIZATIONS.md for complete documentation.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# For progressive PNG loading (interlacing)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL/Pillow not available - interlaced PNGs disabled")


class VisualizationTemplates:
    """Pre-defined professional templates"""
    
    # Professional color palette
    COLORS = {
        "primary": "#2E86AB",      # Blue
        "secondary": "#A23B72",    # Purple
        "accent": "#F18F01",       # Orange
        "success": "#06A77D",      # Green
        "warning": "#F77F00",      # Dark Orange
        "danger": "#D62828",       # Red
        "neutral": "#6C757D"       # Gray
    }
    
    THEME = {
        "font_family": "Arial, sans-serif",
        "title_font_size": 18,
        "axis_font_size": 12,
        "background_color": "#FFFFFF",
        "grid_color": "#E5E5E5"
    }


def _optimize_png(png_path: str) -> None:
    """
    Optimize PNG file size without quality loss.
    Uses PIL's optimize flag for compression.
    
    Benefits:
    - Reduces file size by 10-20% without quality loss
    - No external dependencies (uses Pillow/PIL)
    - Fast processing (< 0.5s per image)
    
    Note: Interlacing requires ImageMagick (not included to avoid heavy dependencies)
    For true progressive loading, consider WebP format (Option 2 from PNG optimization guide)
    """
    if not PIL_AVAILABLE or not os.path.exists(png_path):
        return
    
    try:
        img = Image.open(png_path)
        # Optimize PNG compression (lossless)
        img.save(png_path, 'PNG', optimize=True)
        print(f"   ✅ Optimized PNG: {os.path.basename(png_path)}")
    except Exception as e:
        print(f"   ⚠️  PNG optimization failed: {e}")


class BarChartTool:
    """
    Bar Chart for Categorical + Numerical Data
    Auto-styled, professional templates
    """
    
    @staticmethod
    def create(
        data: Dict[str, List],
        title: str = "Bar Chart Analysis",
        x_label: str = "Category",
        y_label: str = "Value",
        template: str = "professional"
    ) -> Dict[str, Any]:
        """
        Create bar chart from categorical and numerical data.
        
        Args:
            data: Dictionary with "categories" and "values" lists
                  Example: {"categories": ["US", "EU"], "values": [85, 72]}
            title: Chart title (default: "Bar Chart Analysis")
            x_label: X-axis label (default: "Category")
            y_label: Y-axis label (default: "Value")
            template: Visual style - "professional" (default), "colorful", or "minimal"
        
        Returns:
            Dictionary containing:
                - artifact_id: Unique identifier
                - type: "bar_chart"
                - title: Chart title
                - html_path: Path to interactive HTML
                - png_path: Path to static PNG
                - data: Original data
                - created_at: ISO timestamp
        
        Example:
            >>> data = {
            ...     "categories": ["United States", "China", "India"],
            ...     "values": [85, 72, 60]
            ... }
            >>> artifact = BarChartTool.create(data, title="Sentiment Scores")
            >>> print(artifact['png_path'])
            artifacts/bar_abc123.png
        """
        
        categories = data.get("categories", [])
        values = data.get("values", [])
        
        # Create figure
        fig = go.Figure()
        
        # Color scheme based on template
        if template == "professional":
            colors = [VisualizationTemplates.COLORS["primary"]] * len(categories)
        elif template == "colorful":
            colors = [
                VisualizationTemplates.COLORS["primary"],
                VisualizationTemplates.COLORS["secondary"],
                VisualizationTemplates.COLORS["accent"],
                VisualizationTemplates.COLORS["success"]
            ] * (len(categories) // 4 + 1)
            colors = colors[:len(categories)]
        else:  # minimal
            colors = [VisualizationTemplates.COLORS["neutral"]] * len(categories)
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
        ))
        
        # Update layout with template
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': VisualizationTemplates.THEME["title_font_size"],
                    'family': VisualizationTemplates.THEME["font_family"]
                }
            },
            xaxis_title=x_label,
            yaxis_title=y_label,
            plot_bgcolor=VisualizationTemplates.THEME["background_color"],
            paper_bgcolor=VisualizationTemplates.THEME["background_color"],
            font_family=VisualizationTemplates.THEME["font_family"],
            showlegend=False,
            height=500,
            margin=dict(t=80, b=60, l=60, r=40)
        )
        
        # Grid styling
        fig.update_xaxes(
            showgrid=False,
            gridcolor=VisualizationTemplates.THEME["grid_color"]
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor=VisualizationTemplates.THEME["grid_color"]
        )
        
        # Save files
        artifact_id = f"bar_{uuid.uuid4().hex[:12]}"
        os.makedirs("artifacts", exist_ok=True)
        
        html_path = f"artifacts/{artifact_id}.html"
        png_path = f"artifacts/{artifact_id}.png"
        
        # Use CDN for Plotly.js to reduce file size by 80% (4.6MB → 800KB)
        fig.write_html(html_path, include_plotlyjs='cdn')
        fig.write_image(png_path, width=1200, height=600)
        
        # Convert to interlaced PNG for progressive loading
        _optimize_png(png_path)
        
        return {
            "artifact_id": artifact_id,
            "type": "bar_chart",
            "title": title,
            "html_path": html_path,
            "png_path": png_path,
            "data": data,
            "created_at": datetime.utcnow().isoformat()
        }


class LineChartTool:
    """
    Line Chart for Trend Analysis
    Time-series and progression visualization
    """
    
    @staticmethod
    def create(
        data: Dict[str, List],
        title: str = "Trend Analysis",
        x_label: str = "Time",
        y_label: str = "Value",
        template: str = "professional"
    ) -> Dict[str, Any]:
        """
        Create line chart for trend analysis and time-series data.
        
        Args:
            data: Dictionary with "x" and "y" lists, or "x" and "series" for multiple lines
                  Single series: {"x": ["2020", "2021"], "y": [10, 15]}
                  Multi-series: {"x": ["Q1", "Q2"], "series": [
                      {"name": "Series 1", "y": [10, 15]},
                      {"name": "Series 2", "y": [12, 14]}
                  ]}
            title: Chart title (default: "Trend Analysis")
            x_label: X-axis label (default: "Time")
            y_label: Y-axis label (default: "Value")
            template: Visual style - "professional" (default), "colorful", or "minimal"
        
        Returns:
            Dictionary containing artifact metadata and file paths
        
        Example:
            >>> data = {
            ...     "x": ["2020", "2021", "2022", "2023"],
            ...     "y": [-5.78, 9.69, 6.99, 8.15]
            ... }
            >>> artifact = LineChartTool.create(data, title="India GDP Growth")
            >>> print(artifact['html_path'])
            artifacts/line_def456.html
        """
        
        x_data = data.get("x", [])
        y_data = data.get("y", [])
        series = data.get("series", [{"name": "Trend", "y": y_data}])
        
        # Create figure
        fig = go.Figure()
        
        # Color palette
        color_palette = [
            VisualizationTemplates.COLORS["primary"],
            VisualizationTemplates.COLORS["secondary"],
            VisualizationTemplates.COLORS["accent"],
            VisualizationTemplates.COLORS["success"]
        ]
        
        # Add lines for each series
        for idx, s in enumerate(series):
            color = color_palette[idx % len(color_palette)]
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=s.get("y", y_data),
                name=s.get("name", f"Series {idx+1}"),
                mode='lines+markers',
                line=dict(color=color, width=3),
                marker=dict(size=8, color=color),
                hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': VisualizationTemplates.THEME["title_font_size"],
                    'family': VisualizationTemplates.THEME["font_family"]
                }
            },
            xaxis_title=x_label,
            yaxis_title=y_label,
            plot_bgcolor=VisualizationTemplates.THEME["background_color"],
            paper_bgcolor=VisualizationTemplates.THEME["background_color"],
            font_family=VisualizationTemplates.THEME["font_family"],
            showlegend=len(series) > 1,
            height=500,
            margin=dict(t=80, b=60, l=60, r=40),
            hovermode='x unified'
        )
        
        # Grid styling
        fig.update_xaxes(
            showgrid=True,
            gridcolor=VisualizationTemplates.THEME["grid_color"]
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor=VisualizationTemplates.THEME["grid_color"]
        )
        
        # Save files
        artifact_id = f"line_{uuid.uuid4().hex[:12]}"
        os.makedirs("artifacts", exist_ok=True)
        
        html_path = f"artifacts/{artifact_id}.html"
        png_path = f"artifacts/{artifact_id}.png"
        
        # Use CDN for Plotly.js to reduce file size by 80% (4.6MB → 800KB)
        fig.write_html(html_path, include_plotlyjs='cdn')
        fig.write_image(png_path, width=1200, height=600)
        
        # Convert to interlaced PNG for progressive loading
        _optimize_png(png_path)
        
        return {
            "artifact_id": artifact_id,
            "type": "line_chart",
            "title": title,
            "html_path": html_path,
            "png_path": png_path,
            "data": data,
            "created_at": datetime.utcnow().isoformat()
        }


class MindMapTool:
    """
    Mind Map for Concept Visualization
    Hierarchical concept relationships
    """
    
    @staticmethod
    def create(
        data: Dict[str, Any],
        title: str = "Concept Mind Map",
        template: str = "professional"
    ) -> Dict[str, Any]:
        """
        Create mind map from hierarchical data using Graphviz via pydot.
        Falls back to Plotly treemap if Graphviz binary is unavailable.
        
        Args:
            data: {
                "root": "Main Concept",
                "children": [
                    {"name": "Sub 1", "children": [...]},
                    {"name": "Sub 2", "value": 10}
                ]
            }
            title: Chart title
            template: professional | colorful | minimal
        
        Returns:
            Chart metadata and file paths
        """
        artifact_id = f"mindmap_{uuid.uuid4().hex[:12]}"
        os.makedirs("artifacts", exist_ok=True)
        html_path = f"artifacts/{artifact_id}.html"
        png_path = f"artifacts/{artifact_id}.png"
        
        # Try Graphviz via pydot for true mind map
        try:
            import pydot
            # Build graph (radial layout via twopi if available)
            graph = pydot.Dot(graph_type='graph')
            graph.set_rankdir('LR')
            graph.set_overlap('false')
            graph.set_splines('true')
            graph.set_bgcolor('white')
            graph.set('layout', 'dot')  # default to dot; twopi may not be present
            
            # Node style
            def add_node(name: str, level: int):
                color_keys = list(VisualizationTemplates.COLORS.keys())
                color_val = VisualizationTemplates.COLORS[color_keys[level % len(color_keys)]]
                node = pydot.Node(
                    name,
                    shape='box',
                    style='filled,rounded',
                    fillcolor=color_val,
                    fontname=VisualizationTemplates.THEME["font_family"],
                    fontsize='12',
                    color='white'
                )
                graph.add_node(node)
            
            def traverse(node: Dict[str, Any], parent: Optional[str] = None, level: int = 0):
                node_name = node.get('name') or node.get('root') or 'Node'
                add_node(node_name, level)
                if parent:
                    edge = pydot.Edge(parent, node_name, color='#999999')
                    graph.add_edge(edge)
                for child in node.get('children', []):
                    traverse(child, node_name, level + 1)
            
            # Build from data
            if 'root' in data:
                traverse(data, None, 0)
            else:
                # Fallback simple list to a single root
                root_name = title or 'Mind Map'
                add_node(root_name, 0)
                for item in data.get('items', []):
                    child_name = item.get('name', 'Item')
                    add_node(child_name, 1)
                    graph.add_edge(pydot.Edge(root_name, child_name, color='#999999'))
            
            # Write PNG (requires Graphviz binary)
            graph.write_png(png_path)
            
            # Create a very simple HTML wrapper to preview the PNG
            with open(html_path, 'w') as f:
                f.write(f"""
<!doctype html>
<html>
<head><meta charset=\"utf-8\"><title>{title}</title></head>
<body style=\"margin:0; padding:0; background:#ffffff;\">
  <img src=\"{os.path.basename(png_path)}\" style=\"max-width:100%; height:auto; display:block; margin:auto;\" />
  <h3 style=\"font-family:{VisualizationTemplates.THEME['font_family']}; text-align:center;\">{title}</h3>
</body>
</html>
""")
            
            return {
                "artifact_id": artifact_id,
                "type": "mind_map",
                "title": title,
                "html_path": html_path,
                "png_path": png_path,
                "data": data,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception:
            # Fallback to Plotly treemap if Graphviz not available
            labels = []
            parents = []
            values = []
            colors = []
            
            def traverse_plotly(node, parent=""):
                node_name = node.get("name", node.get("root", ""))
                labels.append(node_name)
                parents.append(parent)
                values.append(node.get("value", 1))
                depth = len([p for p in parents if p])
                color_idx = depth % len(VisualizationTemplates.COLORS)
                color = list(VisualizationTemplates.COLORS.values())[color_idx]
                colors.append(color)
                for child in node.get("children", []):
                    traverse_plotly(child, node_name)
            
            if "root" in data:
                traverse_plotly(data)
            else:
                for item in data.get("items", []):
                    labels.append(item.get("name", ""))
                    parents.append("")
                    values.append(item.get("value", 1))
                    colors.append(VisualizationTemplates.COLORS["primary"])
            
            fig = go.Figure(go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                marker=dict(
                    colors=colors,
                    line=dict(width=2, color='white')
                ),
                textfont=dict(
                    size=14,
                    family=VisualizationTemplates.THEME["font_family"],
                    color='white'
                ),
                hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>'
            ))
            
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {
                        'size': VisualizationTemplates.THEME["title_font_size"],
                        'family': VisualizationTemplates.THEME["font_family"]
                    }
                },
                height=600,
                margin=dict(t=80, b=20, l=20, r=20)
            )
            
            # Use CDN for Plotly.js to reduce file size by 80% (4.6MB → 800KB)
            fig.write_html(html_path, include_plotlyjs='cdn')
            fig.write_image(png_path, width=1200, height=800)
            
            # Convert to interlaced PNG for progressive loading
            _optimize_png(png_path)
            
            return {
                "artifact_id": artifact_id,
                "type": "mind_map",
                "title": title,
                "html_path": html_path,
                "png_path": png_path,
                "data": data,
                "created_at": datetime.utcnow().isoformat()
            }


class MapChartTool:
    """
    Choropleth Map for Geographic Data
    Visualize sentiment/data across countries
    
    Data format:
        {
            "countries": ["US", "Israel", "UK"],
            "values": [-0.4, -0.7, 0.3],
            "labels": ["US: Negative", "Israel: Very Negative", "UK: Positive"]  # optional
        }
    """
    
    @staticmethod
    def create(
        data: Dict[str, Any],
        title: str = "Geographic Analysis",
        legend_title: str = "Score"
    ) -> Dict[str, Any]:
        """
        Create choropleth map visualization
        
        Args:
            data: Must contain "countries" and "values" keys
            title: Chart title
            legend_title: Legend title (e.g., "Sentiment Score")
        
        Returns:
            Artifact metadata dict
        """
        # Import country code mapping from shared
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
        from shared.visualization_factory import get_country_code
        
        countries = data.get("countries", [])
        values = data.get("values", [])
        labels = data.get("labels", countries)
        
        if not countries or not values:
            raise ValueError("Map data must include 'countries' and 'values' keys")
        
        if len(countries) != len(values):
            raise ValueError(f"Mismatch: {len(countries)} countries but {len(values)} values")
        
        # Filter out None values and convert to float (defensive handling)
        clean_values = []
        for i, val in enumerate(values):
            if val is None:
                # Use midpoint as default (0 for sentiment, 50 for corruption scores)
                default_val = 0 if all(isinstance(v, (int, float)) and -1 <= v <= 1 for v in values if v is not None) else 50
                clean_values.append(default_val)
                print(f"⚠️  Warning: {countries[i]} has None value, using default: {default_val}")
            else:
                clean_values.append(float(val))
        values = clean_values
        
        # Convert country names to ISO codes
        iso_codes = []
        mapped_values = []
        mapped_labels = []
        skipped = []
        
        for i, country in enumerate(countries):
            iso_code = get_country_code(country)
            if iso_code:
                iso_codes.append(iso_code)
                mapped_values.append(values[i])
                mapped_labels.append(labels[i] if i < len(labels) else country)
            else:
                skipped.append(country)
        
        if not iso_codes:
            raise ValueError(f"No valid country codes found. Skipped: {skipped}")
        
        # Calculate value range for better color scaling
        min_val = min(mapped_values)
        max_val = max(mapped_values)
        val_range = max_val - min_val
        
        # Ensure color scale has good range (at least 0.5 range for visibility)
        if val_range < 0.5:
            # Expand range symmetrically around the values
            center = (min_val + max_val) / 2
            min_val = center - 0.5
            max_val = center + 0.5
        
        # Country center coordinates for text labels (approximate)
        COUNTRY_CENTERS = {
            'USA': {'lat': 37.0902, 'lon': -95.7129},
            'GBR': {'lat': 55.3781, 'lon': -3.4360},
            'FRA': {'lat': 46.2276, 'lon': 2.2137},
            'DEU': {'lat': 51.1657, 'lon': 10.4515},
            'ITA': {'lat': 41.8719, 'lon': 12.5674},
            'ESP': {'lat': 40.4637, 'lon': -3.7492},
            'CHN': {'lat': 35.8617, 'lon': 104.1954},
            'JPN': {'lat': 36.2048, 'lon': 138.2529},
            'IND': {'lat': 20.5937, 'lon': 78.9629},
            'BRA': {'lat': -14.2350, 'lon': -51.9253},
            'RUS': {'lat': 61.5240, 'lon': 105.3188},
            'CAN': {'lat': 56.1304, 'lon': -106.3468},
            'AUS': {'lat': -25.2744, 'lon': 133.7751},
            'ISR': {'lat': 31.0461, 'lon': 34.8516},
            'ARE': {'lat': 23.4241, 'lon': 53.8478},
            'SAU': {'lat': 23.8859, 'lon': 45.0792},
            'EGY': {'lat': 26.8206, 'lon': 30.8025},
            'ZAF': {'lat': -30.5595, 'lon': 22.9375},
            'MEX': {'lat': 23.6345, 'lon': -102.5528},
            'ARG': {'lat': -38.4161, 'lon': -63.6167},
        }
        
        # Create choropleth map with improved settings
        fig = go.Figure(data=go.Choropleth(
            locations=iso_codes,
            z=mapped_values,
            text=mapped_labels,
            locationmode='ISO-3',
            colorscale='RdYlGn',  # Red-Yellow-Green
            reversescale=False,
            zmid=0,  # Center at 0 for sentiment
            zmin=min_val,
            zmax=max_val,
            marker_line_color='darkgray',
            marker_line_width=1.5,  # Thicker borders for visibility
            colorbar=dict(
                title=legend_title,
                thickness=15,
                len=0.7,
                tickformat='.2f'
            ),
            hovertemplate='<b>%{text}</b><br>Value: %{z:.2f}<extra></extra>',
            showscale=True,
            name=''
        ))
        
        # Add text labels on countries showing the actual values
        text_lats = []
        text_lons = []
        text_labels = []
        text_colors = []
        
        for i, code in enumerate(iso_codes):
            if code in COUNTRY_CENTERS:
                text_lats.append(COUNTRY_CENTERS[code]['lat'])
                text_lons.append(COUNTRY_CENTERS[code]['lon'])
                # Format: "Country: Value"
                country_name = countries[i]
                value = mapped_values[i]
                text_labels.append(f"<b>{country_name}</b><br>{value:+.2f}")
                # Use contrasting color (white for dark backgrounds, black for light)
                text_colors.append('white' if value < -0.2 else 'black')
        
        # Add scatter trace for text annotations
        if text_lats:
            fig.add_trace(go.Scattergeo(
                lon=text_lons,
                lat=text_lats,
                text=text_labels,
                mode='text',
                textfont=dict(
                    size=14,
                    family=VisualizationTemplates.THEME["font_family"],
                    color='white'
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Determine best projection based on countries
        # If only small region, zoom in
        if len(iso_codes) <= 3:
            # For small number of countries, use a projection that shows detail
            projection = 'natural earth'
            # Try to detect if it's Middle East region
            if any(code in ['ISR', 'PSE', 'LBN', 'SYR', 'JOR', 'IRQ'] for code in iso_codes):
                projection = 'mercator'
        else:
            projection = 'natural earth'
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(
                    size=VisualizationTemplates.THEME["title_font_size"],
                    family=VisualizationTemplates.THEME["font_family"]
                ),
                x=0.5,
                xanchor='center'
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                showcountries=True,
                coastlinecolor='lightgray',
                countrycolor='lightgray',
                projection_type=projection,
                resolution=50,  # Higher resolution for better detail
                showlakes=True,
                lakecolor='rgb(255, 255, 255)'
            ),
            paper_bgcolor=VisualizationTemplates.THEME["background_color"],
            font=dict(family=VisualizationTemplates.THEME["font_family"]),
            height=600,
            margin=dict(t=60, b=20, l=20, r=20)
        )
        
        # Save files
        artifact_id = f"map_{uuid.uuid4().hex[:12]}"
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
        os.makedirs(output_dir, exist_ok=True)
        
        html_path = os.path.join(output_dir, f"{artifact_id}.html")
        # Use CDN for Plotly.js to reduce file size by 80% (4.6MB → 800KB)
        fig.write_html(html_path, include_plotlyjs='cdn')
        
        # PNG export (note: requires kaleido)
        png_path = os.path.join(output_dir, f"{artifact_id}.png")
        try:
            fig.write_image(png_path, width=1200, height=600)
            # Convert to interlaced PNG for progressive loading
            _optimize_png(png_path)
        except Exception:
            png_path = None  # Fallback if kaleido not available
        
        return {
            "artifact_id": artifact_id,
            "type": "map_chart",
            "title": title,
            "html_path": html_path,
            "png_path": png_path,
            "data": {
                "countries": countries,
                "mapped_countries": iso_codes,
                "skipped_countries": skipped,
                "values": values
            },
            "created_at": datetime.utcnow().isoformat()
        }


class VisualizationFactory:
    """
    Auto-detect and create appropriate visualization
    """
    
    @staticmethod
    def auto_create(
        data: Dict[str, Any],
        context: str = "",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically detect data type and create best visualization
        
        Args:
            data: Data to visualize
            context: Context from query to help determine chart type
            title: Optional title
        
        Returns:
            Artifact metadata
        """
        
        context_lower = context.lower()
        
        # Detect chart type from context
        if any(word in context_lower for word in ["trend", "over time", "timeline", "progression"]):
            return LineChartTool.create(data, title or "Trend Analysis")
        
        elif any(word in context_lower for word in ["concept", "mind", "hierarchy", "structure", "breakdown"]):
            return MindMapTool.create(data, title or "Concept Map")
        
        elif any(word in context_lower for word in ["compare", "comparison", "versus", "vs"]):
            return BarChartTool.create(data, title or "Comparison Analysis")
        
        else:
            # Default: detect from data structure
            if "x" in data and "y" in data:
                # Time series data
                return LineChartTool.create(data, title or "Trend Analysis")
            elif "root" in data or "children" in data:
                # Hierarchical data
                return MindMapTool.create(data, title or "Concept Map")
            else:
                # Categorical data
                return BarChartTool.create(data, title or "Analysis Results")


# Easy exports
def create_bar_chart(data: Dict, title: str = "Bar Chart") -> Dict:
    """
    Quick bar chart creation.
    
    Args:
        data: {"categories": [...], "values": [...]}
        title: Chart title
    
    Returns:
        Artifact dictionary with file paths
    
    Example:
        >>> artifact = create_bar_chart(
        ...     {"categories": ["A", "B"], "values": [10, 20]},
        ...     title="Comparison"
        ... )
    """
    return BarChartTool.create(data, title)

def create_line_chart(data: Dict, title: str = "Line Chart") -> Dict:
    """
    Quick line chart creation.
    
    Args:
        data: {"x": [...], "y": [...]} or {"x": [...], "series": [...]}
        title: Chart title
    
    Returns:
        Artifact dictionary with file paths
    
    Example:
        >>> artifact = create_line_chart(
        ...     {"x": ["2020", "2021"], "y": [10, 15]},
        ...     title="Trend"
        ... )
    """
    return LineChartTool.create(data, title)

def create_mind_map(data: Dict, title: str = "Mind Map") -> Dict:
    """
    Quick mind map creation.
    
    Args:
        data: {"root": "...", "children": [...]}
        title: Chart title
    
    Returns:
        Artifact dictionary with file paths
    
    Example:
        >>> artifact = create_mind_map(
        ...     {"root": "Main", "children": [{"name": "Sub1", "value": 10}]},
        ...     title="Concepts"
        ... )
    """
    return MindMapTool.create(data, title)

def create_map_chart(data: Dict, title: str = "Geographic Map", legend_title: str = "Score") -> Dict:
    """
    Quick map chart creation for geographic data.
    
    Args:
        data: {"countries": [...], "values": [...], "labels": [...] (optional)}
        title: Chart title
        legend_title: Legend title (e.g., "Sentiment Score")
    
    Returns:
        Artifact dictionary with file paths
    
    Example:
        >>> artifact = create_map_chart(
        ...     {"countries": ["US", "Israel"], "values": [-0.4, -0.7]},
        ...     title="Sentiment Map",
        ...     legend_title="Sentiment Score"
        ... )
    """
    return MapChartTool.create(data, title, legend_title)

def auto_visualize(data: Dict, context: str = "", title: str = None) -> Dict:
    """
    Auto-detect and create appropriate visualization based on context.
    
    Args:
        data: Data dictionary (format depends on detected chart type)
        context: Query context for detection (e.g., "trend over time")
        title: Optional title
    
    Returns:
        Artifact dictionary with file paths
    
    Detection:
        - "trend", "over time" → Line chart
        - "concept", "hierarchy" → Mind map
        - "compare", "versus" → Bar chart
        - Default → Bar chart
    
    Example:
        >>> artifact = auto_visualize(
        ...     data={"x": [...], "y": [...]},
        ...     context="Show me the trend over 5 years",
        ...     title="5-Year Analysis"
        ... )
    """
    return VisualizationFactory.auto_create(data, context, title)

