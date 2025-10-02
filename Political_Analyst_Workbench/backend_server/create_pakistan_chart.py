"""
Script to generate cached visualization for Pakistan's GDP growth
"""

import plotly.graph_objects as go
import os

# Data for Pakistan's GDP growth (2020-2024)
years = [2020, 2021, 2022, 2023, 2024]
gdp_growth = [-1.0, 5.7, 6.0, 0.3, 2.8]  # GDP growth percentages

# Create the line chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=years,
    y=gdp_growth,
    mode='lines+markers',
    name='GDP Growth Rate',
    line=dict(color='#d9f378', width=3),
    marker=dict(size=10, color='#d9f378', line=dict(width=2, color='#1c1e20')),
    hovertemplate='<b>%{x}</b><br>GDP Growth: %{y}%<extra></extra>'
))

# Add a zero line for reference
fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)", 
              annotation_text="Zero Growth", annotation_position="bottom right")

# Update layout with custom styling
fig.update_layout(
    title={
        'text': "Pakistan's GDP Growth Rate (2020-2024)",
        'font': {'size': 24, 'color': '#d9f378', 'family': 'Roboto Flex'},
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Year',
        titlefont=dict(size=16, color='#d9f378'),
        tickfont=dict(size=14, color='#5d535c'),
        gridcolor='rgba(93, 83, 92, 0.2)',
        showgrid=True
    ),
    yaxis=dict(
        title='GDP Growth Rate (%)',
        titlefont=dict(size=16, color='#d9f378'),
        tickfont=dict(size=14, color='#5d535c'),
        gridcolor='rgba(93, 83, 92, 0.2)',
        showgrid=True,
        zeroline=True,
        zerolinecolor='rgba(255,255,255,0.3)'
    ),
    plot_bgcolor='#1c1e20',
    paper_bgcolor='#1c1e20',
    font=dict(family='Roboto Flex', color='#5d535c'),
    hovermode='x unified',
    margin=dict(l=60, r=40, t=80, b=60),
    height=500
)

# Ensure artifacts directory exists
artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
os.makedirs(artifacts_dir, exist_ok=True)

# Save as HTML (interactive)
html_path = os.path.join(artifacts_dir, 'pakistan_gdp_cached_2024.html')
fig.write_html(html_path)
print(f"✅ Created HTML: {html_path}")

# Save as PNG (static image)
try:
    png_path = os.path.join(artifacts_dir, 'pakistan_gdp_cached_2024.png')
    fig.write_image(png_path, width=1200, height=600, scale=2)
    print(f"✅ Created PNG: {png_path}")
except Exception as e:
    print(f"⚠️  PNG creation failed (kaleido may not be installed): {e}")
    print("   Run: uv pip install kaleido")

print("\n🎉 Pakistan cached chart files created successfully!")
print(f"📊 HTML: http://localhost:8000/api/artifacts/pakistan_gdp_cached_2024.html")
print(f"🖼️  PNG: http://localhost:8000/api/artifacts/pakistan_gdp_cached_2024.png")

