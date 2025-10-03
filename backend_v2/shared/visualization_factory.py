"""
Shared Visualization Factory for all agents

This module provides reusable visualization tools using Plotly.
All agents should use these functions to maintain consistency.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional, Tuple
import uuid
import os
import json
from datetime import datetime
import pandas as pd


class VisualizationFactory:
    """Reusable visualization tools for all agents"""
    
    # Color schemes
    SENTIMENT_COLORS = "RdYlGn"  # Red-Yellow-Green
    BIAS_COLORS = "RdBu"  # Red-Blue
    DEFAULT_TEMPLATE = "plotly_white"
    
    @staticmethod
    def create_bar_chart(
        x_data: List[str],
        y_data: List[float],
        title: str,
        x_label: str = "Category",
        y_label: str = "Value",
        color_scale: str = "RdYlGn",
        color_range: Tuple[float, float] = (-1, 1),
        height: int = 500
    ) -> go.Figure:
        """
        Create standard bar chart with color gradient
        
        Args:
            x_data: Categories (e.g., country names)
            y_data: Values (e.g., sentiment scores)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            color_scale: Plotly color scale name
            color_range: Min/max for color mapping (cmin, cmax)
            height: Chart height in pixels
        
        Returns:
            Plotly Figure object
        """
        fig = go.Figure(data=[
            go.Bar(
                x=x_data,
                y=y_data,
                marker=dict(
                    color=y_data,
                    colorscale=color_scale,
                    cmin=color_range[0],
                    cmax=color_range[1],
                    colorbar=dict(title=y_label)
                ),
                text=[f"{val:.2f}" for val in y_data],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=height,
            template=VisualizationFactory.DEFAULT_TEMPLATE,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(
        categories: List[str],
        values_dict: Dict[str, List[float]],
        title: str,
        height: int = 500,
        max_series: int = 5
    ) -> go.Figure:
        """
        Create multi-series radar chart
        
        Args:
            categories: Axis labels (e.g., ['Positive', 'Neutral', 'Negative'])
            values_dict: {series_name: [values]} (e.g., {'US': [0.6, 0.3, 0.1]})
            title: Chart title
            height: Chart height in pixels
            max_series: Maximum number of series to display
        
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Limit to max_series for readability
        for i, (series_name, values) in enumerate(list(values_dict.items())[:max_series]):
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=series_name
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title=title,
            height=height,
            template=VisualizationFactory.DEFAULT_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_choropleth_map(
        country_data: Dict[str, float],
        title: str,
        color_scale: str = "RdYlGn",
        color_range: Tuple[float, float] = (-1, 1),
        height: int = 500
    ) -> go.Figure:
        """
        Create world map (choropleth) visualization
        
        Args:
            country_data: {country_code: value} (e.g., {'USA': 0.8, 'GBR': -0.3})
            title: Chart title
            color_scale: Plotly color scale name
            color_range: Min/max for color mapping
            height: Chart height in pixels
        
        Returns:
            Plotly Figure object
        
        Note: Country codes should be ISO 3-letter codes (USA, GBR, FRA, etc.)
        """
        countries = list(country_data.keys())
        values = list(country_data.values())
        
        fig = go.Figure(data=go.Choropleth(
            locations=countries,
            z=values,
            locationmode='ISO-3',
            colorscale=color_scale,
            zmin=color_range[0],
            zmax=color_range[1],
            colorbar=dict(title="Score"),
            marker_line_color='white',
            marker_line_width=0.5
        ))
        
        fig.update_layout(
            title=title,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            ),
            height=height,
            template=VisualizationFactory.DEFAULT_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_line_chart(
        x_data: List[Any],
        y_data_dict: Dict[str, List[float]],
        title: str,
        x_label: str = "Time",
        y_label: str = "Value",
        height: int = 500
    ) -> go.Figure:
        """
        Create multi-line chart (e.g., trend over time)
        
        Args:
            x_data: X-axis values (e.g., dates or timestamps)
            y_data_dict: {series_name: [values]} (e.g., {'US': [0.5, 0.6, 0.7]})
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            height: Chart height in pixels
        
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        for series_name, y_values in y_data_dict.items():
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_values,
                mode='lines+markers',
                name=series_name,
                line=dict(width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=height,
            template=VisualizationFactory.DEFAULT_TEMPLATE,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(
        z_data: List[List[float]],
        x_labels: List[str],
        y_labels: List[str],
        title: str,
        color_scale: str = "RdYlGn",
        height: int = 500
    ) -> go.Figure:
        """
        Create heatmap visualization
        
        Args:
            z_data: 2D array of values
            x_labels: Column labels
            y_labels: Row labels
            title: Chart title
            color_scale: Plotly color scale name
            height: Chart height in pixels
        
        Returns:
            Plotly Figure object
        """
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale=color_scale,
            text=[[f"{val:.2f}" for val in row] for row in z_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Score")
        ))
        
        fig.update_layout(
            title=title,
            height=height,
            template=VisualizationFactory.DEFAULT_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def save_artifact(
        fig: go.Figure,
        output_dir: str,
        artifact_type: str,
        title: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save Plotly figure to HTML and return artifact metadata
        
        Args:
            fig: Plotly Figure object
            output_dir: Directory to save files
            artifact_type: Type identifier (e.g., 'bar_chart', 'radar_chart')
            title: Human-readable title
            data: Optional structured data to save alongside
        
        Returns:
            Artifact metadata dictionary
        """
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique ID
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:12]}"
        
        # Save HTML
        html_path = os.path.join(output_dir, f"{artifact_id}.html")
        fig.write_html(html_path)
        
        artifact = {
            "artifact_id": artifact_id,
            "type": artifact_type,
            "title": title or artifact_type.replace('_', ' ').title(),
            "html_path": html_path,
            "created_at": datetime.now().isoformat()
        }
        
        # Save accompanying data if provided
        if data:
            json_path = os.path.join(output_dir, f"{artifact_id}_data.json")
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            artifact["json_path"] = json_path
        
        return artifact
    
    @staticmethod
    def save_json_export(
        data: Dict[str, Any],
        output_dir: str,
        artifact_type: str = "data_table",
        title: str = "Data Export"
    ) -> Dict[str, Any]:
        """
        Save structured data as JSON artifact
        
        Args:
            data: Data to export
            output_dir: Directory to save file
            artifact_type: Type identifier
            title: Human-readable title
        
        Returns:
            Artifact metadata dictionary
        """
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique ID
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:12]}"
        
        # Save JSON
        json_path = os.path.join(output_dir, f"{artifact_id}.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "artifact_id": artifact_id,
            "type": artifact_type,
            "title": title,
            "json_path": json_path,
            "created_at": datetime.now().isoformat()
        }


# ============================================================================
# Country Code Mapping Utility
# ============================================================================

# Common country name variations → ISO 3-letter code (All ~195 UN member states)
COUNTRY_CODE_MAP = {
    # North America
    "US": "USA", "USA": "USA", "United States": "USA", "United States of America": "USA",
    "America": "USA", "U.S.": "USA", "U.S.A.": "USA",
    "Canada": "CAN", "CA": "CAN",
    "Mexico": "MEX", "MX": "MEX",
    
    # Central America & Caribbean
    "Guatemala": "GTM", "GT": "GTM",
    "Belize": "BLZ", "BZ": "BLZ",
    "El Salvador": "SLV", "SV": "SLV",
    "Honduras": "HND", "HN": "HND",
    "Nicaragua": "NIC", "NI": "NIC",
    "Costa Rica": "CRI", "CR": "CRI",
    "Panama": "PAN", "PA": "PAN",
    "Cuba": "CUB", "CU": "CUB",
    "Jamaica": "JAM", "JM": "JAM",
    "Haiti": "HTI", "HT": "HTI",
    "Dominican Republic": "DOM", "DO": "DOM",
    "Trinidad and Tobago": "TTO", "TT": "TTO",
    "Bahamas": "BHS", "BS": "BHS",
    "Barbados": "BRB", "BB": "BRB",
    
    # South America
    "Brazil": "BRA", "BR": "BRA",
    "Argentina": "ARG", "AR": "ARG",
    "Chile": "CHL", "CL": "CHL",
    "Colombia": "COL", "CO": "COL",
    "Peru": "PER", "PE": "PER",
    "Venezuela": "VEN", "VE": "VEN",
    "Ecuador": "ECU", "EC": "ECU",
    "Bolivia": "BOL", "BO": "BOL",
    "Paraguay": "PRY", "PY": "PRY",
    "Uruguay": "URY", "UY": "URY",
    "Guyana": "GUY", "GY": "GUY",
    "Suriname": "SUR", "SR": "SUR",
    
    # Western Europe
    "UK": "GBR", "United Kingdom": "GBR", "Britain": "GBR", "Great Britain": "GBR", "GB": "GBR",
    "England": "GBR", "Scotland": "GBR", "Wales": "GBR",
    "France": "FRA", "FR": "FRA",
    "Germany": "DEU", "DE": "DEU", "Deutschland": "DEU",
    "Italy": "ITA", "IT": "ITA", "Italia": "ITA",
    "Spain": "ESP", "ES": "ESP", "España": "ESP",
    "Netherlands": "NLD", "Holland": "NLD", "NL": "NLD",
    "Belgium": "BEL", "BE": "BEL",
    "Switzerland": "CHE", "CH": "CHE",
    "Austria": "AUT", "AT": "AUT",
    "Portugal": "PRT", "PT": "PRT",
    "Ireland": "IRL", "IE": "IRL",
    "Luxembourg": "LUX", "LU": "LUX",
    "Monaco": "MCO", "MC": "MCO",
    "Liechtenstein": "LIE", "LI": "LIE",
    
    # Northern Europe
    "Sweden": "SWE", "SE": "SWE",
    "Norway": "NOR", "NO": "NOR",
    "Denmark": "DNK", "DK": "DNK",
    "Finland": "FIN", "FI": "FIN",
    "Iceland": "ISL", "IS": "ISL",
    
    # Eastern Europe
    "Poland": "POL", "PL": "POL",
    "Czech Republic": "CZE", "Czechia": "CZE", "CZ": "CZE",
    "Slovakia": "SVK", "SK": "SVK",
    "Hungary": "HUN", "HU": "HUN",
    "Romania": "ROU", "RO": "ROU",
    "Bulgaria": "BGR", "BG": "BGR",
    "Ukraine": "UKR", "UA": "UKR",
    "Belarus": "BLR", "BY": "BLR",
    "Moldova": "MDA", "MD": "MDA",
    "Lithuania": "LTU", "LT": "LTU",
    "Latvia": "LVA", "LV": "LVA",
    "Estonia": "EST", "EE": "EST",
    
    # Southern Europe
    "Greece": "GRC", "GR": "GRC",
    "Croatia": "HRV", "HR": "HRV",
    "Slovenia": "SVN", "SI": "SVN",
    "Bosnia and Herzegovina": "BIH", "BA": "BIH", "Bosnia": "BIH",
    "Serbia": "SRB", "RS": "SRB",
    "Montenegro": "MNE", "ME": "MNE",
    "North Macedonia": "MKD", "Macedonia": "MKD", "MK": "MKD",
    "Albania": "ALB", "AL": "ALB",
    "Kosovo": "XKX", "XK": "XKX",
    "Malta": "MLT", "MT": "MLT",
    "Cyprus": "CYP", "CY": "CYP",
    
    # Russia & Former USSR
    "Russia": "RUS", "RU": "RUS", "Russian Federation": "RUS",
    "Kazakhstan": "KAZ", "KZ": "KAZ",
    "Uzbekistan": "UZB", "UZ": "UZB",
    "Turkmenistan": "TKM", "TM": "TKM",
    "Kyrgyzstan": "KGZ", "KG": "KGZ",
    "Tajikistan": "TJK", "TJ": "TJK",
    "Armenia": "ARM", "AM": "ARM",
    "Azerbaijan": "AZE", "AZ": "AZE",
    "Georgia": "GEO", "GE": "GEO",
    
    # Middle East
    "Turkey": "TUR", "TR": "TUR", "Türkiye": "TUR",
    "Israel": "ISR", "IL": "ISR",
    "Palestine": "PSE", "PS": "PSE",
    "Jordan": "JOR", "JO": "JOR",
    "Lebanon": "LBN", "LB": "LBN",
    "Syria": "SYR", "SY": "SYR",
    "Iraq": "IRQ", "IQ": "IRQ",
    "Iran": "IRN", "IR": "IRN",
    "Saudi Arabia": "SAU", "SA": "SAU",
    "Yemen": "YEM", "YE": "YEM",
    "Oman": "OMN", "OM": "OMN",
    "UAE": "ARE", "United Arab Emirates": "ARE", "AE": "ARE",
    "Qatar": "QAT", "QA": "QAT",
    "Kuwait": "KWT", "KW": "KWT",
    "Bahrain": "BHR", "BH": "BHR",
    
    # North Africa
    "Egypt": "EGY", "EG": "EGY",
    "Libya": "LBY", "LY": "LBY",
    "Tunisia": "TUN", "TN": "TUN",
    "Algeria": "DZA", "DZ": "DZA",
    "Morocco": "MAR", "MA": "MAR",
    "Mauritania": "MRT", "MR": "MRT",
    "Sudan": "SDN", "SD": "SDN",
    "South Sudan": "SSD", "SS": "SSD",
    
    # West Africa
    "Nigeria": "NGA", "NG": "NGA",
    "Ghana": "GHA", "GH": "GHA",
    "Senegal": "SEN", "SN": "SEN",
    "Mali": "MLI", "ML": "MLI",
    "Burkina Faso": "BFA", "BF": "BFA",
    "Niger": "NER", "NE": "NER",
    "Chad": "TCD", "TD": "TCD",
    "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV", "CI": "CIV",
    "Guinea": "GIN", "GN": "GIN",
    "Benin": "BEN", "BJ": "BEN",
    "Togo": "TGO", "TG": "TGO",
    "Sierra Leone": "SLE", "SL": "SLE",
    "Liberia": "LBR", "LR": "LBR",
    "Gambia": "GMB", "GM": "GMB",
    "Guinea-Bissau": "GNB", "GW": "GNB",
    "Cape Verde": "CPV", "CV": "CPV",
    
    # East Africa
    "Kenya": "KEN", "KE": "KEN",
    "Ethiopia": "ETH", "ET": "ETH",
    "Tanzania": "TZA", "TZ": "TZA",
    "Uganda": "UGA", "UG": "UGA",
    "Somalia": "SOM", "SO": "SOM",
    "Rwanda": "RWA", "RW": "RWA",
    "Burundi": "BDI", "BI": "BDI",
    "Eritrea": "ERI", "ER": "ERI",
    "Djibouti": "DJI", "DJ": "DJI",
    
    # Central Africa
    "Democratic Republic of the Congo": "COD", "DR Congo": "COD", "DRC": "COD", "CD": "COD",
    "Congo": "COG", "Republic of the Congo": "COG", "CG": "COG",
    "Central African Republic": "CAF", "CAR": "CAF", "CF": "CAF",
    "Cameroon": "CMR", "CM": "CMR",
    "Gabon": "GAB", "GA": "GAB",
    "Equatorial Guinea": "GNQ", "GQ": "GNQ",
    "Sao Tome and Principe": "STP", "ST": "STP",
    
    # Southern Africa
    "South Africa": "ZAF", "ZA": "ZAF",
    "Zimbabwe": "ZWE", "ZW": "ZWE",
    "Zambia": "ZMB", "ZM": "ZMB",
    "Botswana": "BWA", "BW": "BWA",
    "Namibia": "NAM", "NA": "NAM",
    "Angola": "AGO", "AO": "AGO",
    "Mozambique": "MOZ", "MZ": "MOZ",
    "Malawi": "MWI", "MW": "MWI",
    "Lesotho": "LSO", "LS": "LSO",
    "Eswatini": "SWZ", "Swaziland": "SWZ", "SZ": "SWZ",
    "Madagascar": "MDG", "MG": "MDG",
    "Mauritius": "MUS", "MU": "MUS",
    "Seychelles": "SYC", "SC": "SYC",
    "Comoros": "COM", "KM": "COM",
    
    # East Asia
    "China": "CHN", "CN": "CHN", "PRC": "CHN",
    "Japan": "JPN", "JP": "JPN",
    "South Korea": "KOR", "Korea": "KOR", "KR": "KOR",
    "North Korea": "PRK", "KP": "PRK", "DPRK": "PRK",
    "Mongolia": "MNG", "MN": "MNG",
    "Taiwan": "TWN", "TW": "TWN",
    
    # Southeast Asia
    "Indonesia": "IDN", "ID": "IDN",
    "Thailand": "THA", "TH": "THA",
    "Vietnam": "VNM", "VN": "VNM",
    "Philippines": "PHL", "PH": "PHL",
    "Malaysia": "MYS", "MY": "MYS",
    "Singapore": "SGP", "SG": "SGP",
    "Myanmar": "MMR", "Burma": "MMR", "MM": "MMR",
    "Cambodia": "KHM", "KH": "KHM",
    "Laos": "LAO", "LA": "LAO",
    "Brunei": "BRN", "BN": "BRN",
    "Timor-Leste": "TLS", "East Timor": "TLS", "TL": "TLS",
    
    # South Asia
    "India": "IND", "IN": "IND",
    "Pakistan": "PAK", "PK": "PAK",
    "Bangladesh": "BGD", "BD": "BGD",
    "Afghanistan": "AFG", "AF": "AFG",
    "Sri Lanka": "LKA", "LK": "LKA",
    "Nepal": "NPL", "NP": "NPL",
    "Bhutan": "BTN", "BT": "BTN",
    "Maldives": "MDV", "MV": "MDV",
    
    # Oceania
    "Australia": "AUS", "AU": "AUS",
    "New Zealand": "NZL", "NZ": "NZL",
    "Papua New Guinea": "PNG", "PG": "PNG",
    "Fiji": "FJI", "FJ": "FJI",
    "Solomon Islands": "SLB", "SB": "SLB",
    "Vanuatu": "VUT", "VU": "VUT",
    "Samoa": "WSM", "WS": "WSM",
    "Tonga": "TON", "TO": "TON",
    "Micronesia": "FSM", "FM": "FSM",
    "Palau": "PLW", "PW": "PLW",
    "Marshall Islands": "MHL", "MH": "MHL",
    "Kiribati": "KIR", "KI": "KIR",
    "Tuvalu": "TUV", "TV": "TUV",
    "Nauru": "NRU", "NR": "NRU",
}


def get_country_code(country_name: str) -> Optional[str]:
    """
    Convert country name to ISO 3-letter code
    
    Args:
        country_name: Country name (various formats accepted)
    
    Returns:
        ISO 3-letter code (e.g., 'USA', 'GBR') or None if not found
    
    Examples:
        >>> get_country_code("US")
        'USA'
        >>> get_country_code("United Kingdom")
        'GBR'
        >>> get_country_code("Israel")
        'ISR'
    """
    # Try exact match first
    if country_name in COUNTRY_CODE_MAP:
        return COUNTRY_CODE_MAP[country_name]
    
    # Try case-insensitive match
    for key, value in COUNTRY_CODE_MAP.items():
        if key.lower() == country_name.lower():
            return value
    
    # Return None if not found (caller should handle)
    return None


# ============================================================================
# Helper Functions for Common Patterns
# ============================================================================

def create_sentiment_bar_chart(
    country_scores: Dict[str, Dict[str, float]],
    query: str,
    output_dir: str
) -> Dict[str, Any]:
    """
    Convenience function: Create sentiment bar chart
    
    Args:
        country_scores: {country: {'score': 0.8, 'sentiment': 'positive'}}
        query: Original query
        output_dir: Where to save artifact
    
    Returns:
        Artifact metadata
    """
    countries = list(country_scores.keys())
    scores = [country_scores[c].get('score', 0) for c in countries]
    
    fig = VisualizationFactory.create_bar_chart(
        x_data=countries,
        y_data=scores,
        title=f"Sentiment Analysis: {query}",
        x_label="Country",
        y_label="Sentiment Score",
        color_scale="RdYlGn",
        color_range=(-1, 1)
    )
    
    return VisualizationFactory.save_artifact(
        fig=fig,
        output_dir=output_dir,
        artifact_type="sentiment_bar_chart",
        title="Sentiment Score Comparison",
        data={"query": query, "scores": country_scores}
    )


def create_sentiment_radar_chart(
    country_scores: Dict[str, Dict[str, float]],
    query: str,
    output_dir: str,
    max_countries: int = 5
) -> Dict[str, Any]:
    """
    Convenience function: Create sentiment distribution radar chart
    
    Args:
        country_scores: {country: {'positive_pct': 0.6, 'neutral_pct': 0.3, 'negative_pct': 0.1}}
        query: Original query
        output_dir: Where to save artifact
        max_countries: Limit number of countries shown
    
    Returns:
        Artifact metadata
    """
    # Build values dict for radar chart
    values_dict = {}
    for country in list(country_scores.keys())[:max_countries]:
        scores = country_scores[country]
        values_dict[country] = [
            scores.get('positive_pct', 0.33),
            scores.get('neutral_pct', 0.33),
            scores.get('negative_pct', 0.33)
        ]
    
    fig = VisualizationFactory.create_radar_chart(
        categories=['Positive', 'Neutral', 'Negative'],
        values_dict=values_dict,
        title=f"Sentiment Distribution: {query}"
    )
    
    return VisualizationFactory.save_artifact(
        fig=fig,
        output_dir=output_dir,
        artifact_type="sentiment_radar_chart",
        title="Sentiment Distribution Radar"
    )


def create_sentiment_table(
    country_scores: Dict[str, Dict[str, Any]],
    bias_analysis: Dict[str, Dict[str, Any]],
    query: str,
    output_dir: str,
    search_results: Optional[Dict[str, List[Dict]]] = None
) -> Dict[str, Any]:
    """
    Create comprehensive data table with Excel export (3 sheets)
    
    Creates:
    - Sheet 1: Country Summary (aggregated sentiment by country)
    - Sheet 2: Bias Analysis (bias detection results)
    - Sheet 3: Article Details (if search_results provided)
    
    Args:
        country_scores: {country: {score, sentiment, reasoning, ...}}
        bias_analysis: {country: {bias_types, bias_severity, bias_notes, ...}}
        query: Query text
        output_dir: Where to save files
        search_results: Optional raw article data
    
    Returns:
        Artifact metadata with Excel/JSON/HTML paths
    """
    os.makedirs(output_dir, exist_ok=True)
    artifact_id = f"sentiment_table_{uuid.uuid4().hex[:12]}"
    
    # Sheet 1: Country Summary
    summary_data = []
    for country in country_scores.keys():
        score_data = country_scores.get(country, {})
        bias_data = bias_analysis.get(country, {})
        
        summary_data.append({
            "Country": country,
            "Sentiment_Score": score_data.get("score", 0.0),
            "Sentiment": score_data.get("sentiment", "neutral"),
            "Reasoning": score_data.get("reasoning", ""),
            "Source_Type": score_data.get("source_type", "other"),
            "Credibility": score_data.get("credibility_score", 0.0),
            "Positive_%": f"{score_data.get('positive_pct', 0)*100:.1f}%",
            "Negative_%": f"{score_data.get('negative_pct', 0)*100:.1f}%",
            "Neutral_%": f"{score_data.get('neutral_pct', 0)*100:.1f}%",
            "Bias_Types_Count": len(bias_data.get("bias_types", [])),
            "Bias_Severity": bias_data.get("bias_severity", 0.0)
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    # Sheet 2: Bias Analysis
    bias_data_list = []
    for country, bias in bias_analysis.items():
        bias_types = bias.get("bias_types", [])
        if not bias_types:
            bias_types = ["none"]
        
        for bias_type in bias_types:
            bias_data_list.append({
                "Country": country,
                "Bias_Type": bias_type,
                "Severity": bias.get("bias_severity", 0.0),
                "Overall_Bias": bias.get("overall_bias", "unknown"),
                "Bias_Score": bias.get("bias_score", 0.0),
                "Notes": bias.get("bias_notes", ""),
                "Examples": ", ".join(bias.get("examples", []))
            })
    
    df_bias = pd.DataFrame(bias_data_list) if bias_data_list else pd.DataFrame()
    
    # Sheet 3: Article Details (if provided)
    if search_results:
        article_data = []
        for country, results in search_results.items():
            for result in results:
                article_data.append({
                    "Country": country,
                    "Title": result.get("title", ""),
                    "URL": result.get("url", ""),
                    "Content_Preview": result.get("content", "")[:200] + "...",
                    "Published_Date": result.get("published_date", "Unknown")
                })
        df_articles = pd.DataFrame(article_data) if article_data else pd.DataFrame()
    else:
        df_articles = pd.DataFrame()
    
    # Save as Excel (3 sheets)
    excel_path = os.path.join(output_dir, f"{artifact_id}.xlsx")
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Country_Summary', index=False)
            if not df_bias.empty:
                df_bias.to_excel(writer, sheet_name='Bias_Analysis', index=False)
            if not df_articles.empty:
                df_articles.to_excel(writer, sheet_name='Article_Details', index=False)
        excel_available = True
    except Exception as e:
        print(f"   ⚠️ Excel export failed: {e}. Saving JSON only.")
        excel_available = False
    
    # Save as JSON
    json_data = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "country_summary": summary_data,
        "bias_analysis": bias_data_list,
        "article_count": len(df_articles) if not df_articles.empty else 0
    }
    json_path = os.path.join(output_dir, f"{artifact_id}.json")
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    # Create HTML table (interactive)
    html_path = os.path.join(output_dir, f"{artifact_id}.html")
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sentiment Analysis Data - {query}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
                th {{ background-color: #4CAF50; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .download-btn {{ background-color: #008CBA; color: white; padding: 10px 20px; 
                               text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Sentiment Analysis: {query}</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <a href="{os.path.basename(excel_path)}" class="download-btn" download>📥 Download Excel</a>
            <a href="{os.path.basename(json_path)}" class="download-btn" download>📥 Download JSON</a>
            
            <h2>Country Summary</h2>
            {df_summary.to_html(index=False, classes='data-table')}
            
            <h2>Bias Analysis</h2>
            {df_bias.to_html(index=False, classes='data-table') if not df_bias.empty else '<p>No bias data available</p>'}
            
            {f"<h2>Article Details ({len(df_articles)} articles)</h2>" + df_articles.to_html(index=False, classes='data-table') if not df_articles.empty else ''}
        </body>
        </html>
        """
        with open(html_path, 'w') as f:
            f.write(html_content)
    except Exception as e:
        print(f"   ⚠️ HTML generation failed: {e}")
        html_path = None
    
    artifact_metadata = {
        "artifact_id": artifact_id,
        "type": "sentiment_table",
        "title": f"Sentiment Data Table: {query}",
        "json_path": json_path,
        "html_path": html_path,
        "created_at": datetime.now().isoformat(),
        "row_counts": {
            "summary": len(df_summary),
            "bias": len(df_bias),
            "articles": len(df_articles)
        }
    }
    
    if excel_available:
        artifact_metadata["excel_path"] = excel_path
    
    return artifact_metadata


def create_sentiment_map(
    country_scores: Dict[str, Dict[str, float]],
    query: str,
    output_dir: str
) -> Dict[str, Any]:
    """
    Convenience function: Create sentiment choropleth map
    
    Args:
        country_scores: {country: {'score': 0.8, 'sentiment': 'positive'}}
        query: Original query
        output_dir: Where to save artifact
    
    Returns:
        Artifact metadata
    
    Note: Countries without ISO codes will be skipped with a warning
    """
    # Convert country names to ISO codes
    country_data = {}
    skipped = []
    
    for country, score_dict in country_scores.items():
        iso_code = get_country_code(country)
        if iso_code:
            country_data[iso_code] = score_dict.get('score', 0)
        else:
            skipped.append(country)
            print(f"   ⚠️ No ISO code found for '{country}', skipping from map")
    
    if not country_data:
        print(f"   ❌ No valid countries for map (all skipped: {skipped})")
        return {
            "artifact_id": f"sentiment_map_error_{uuid.uuid4().hex[:12]}",
            "type": "sentiment_map",
            "title": "Sentiment Map (Error)",
            "error": "No countries could be mapped to ISO codes",
            "created_at": datetime.now().isoformat()
        }
    
    if skipped:
        print(f"   ℹ️  Showing {len(country_data)} countries on map ({len(skipped)} skipped)")
    
    # Create map
    fig = VisualizationFactory.create_choropleth_map(
        country_data=country_data,
        title=f"Sentiment Analysis Map: {query}",
        color_scale="RdYlGn",
        color_range=(-1, 1)
    )
    
    # Add annotations for country names
    annotations_text = []
    for country in country_scores.keys():
        iso_code = get_country_code(country)
        if iso_code and iso_code in country_data:
            score = country_data[iso_code]
            sentiment = country_scores[country].get('sentiment', 'neutral')
            annotations_text.append(f"{country}: {score:.2f} ({sentiment})")
    
    return VisualizationFactory.save_artifact(
        fig=fig,
        output_dir=output_dir,
        artifact_type="sentiment_map",
        title="Sentiment Analysis Map",
        data={
            "query": query,
            "scores": country_scores,
            "mapped_countries": list(country_data.keys()),
            "skipped_countries": skipped,
            "annotations": annotations_text
        }
    )

