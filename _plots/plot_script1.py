import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def generate_plots():
    """Generate example plots and return their metadata."""
    os.makedirs("assets/plots", exist_ok=True)
    plots = {}
    
    # Example 1: Scatter plot
    df = pd.DataFrame({
        'x': range(10),
        'y': [i**2 for i in range(10)]
    })
    
    fig1 = px.scatter(df, x='x', y='y', title="Scatter Plot Example")
    
    # Save as HTML with CDN reference (smaller file)
    fig1.write_html(
        "assets/plots/scatter_plot.html",
        full_html=False,
        include_plotlyjs='cdn'
    )
    
    # Save plot metadata
    plots["scatter_plot"] = {
        "title": "Scatter Plot Example",
        "filename": "scatter_plot.html",
        "description": "A simple scatter plot showing x² function"
    }
    
    # Example 2: Bar chart
    categories = ['A', 'B', 'C', 'D']
    values = [20, 14, 23, 25]
    
    fig2 = px.bar(x=categories, y=values, title="Bar Chart Example")
    
    fig2.write_html(
        "assets/plots/bar_chart.html",
        full_html=False,
        include_plotlyjs='cdn'
    )
    
    plots["bar_chart"] = {
        "title": "Bar Chart Example",
        "filename": "bar_chart.html",
        "description": "A simple bar chart"
    }
    
    return plots