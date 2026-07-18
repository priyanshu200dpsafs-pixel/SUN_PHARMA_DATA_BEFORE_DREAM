import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def create_scatter():
    np.random.seed(42)
    
    # Cluster 1: North India
    x1 = np.random.normal(45000, 10000, 50)
    y1 = np.random.normal(85, 10, 50)
    region1 = ['North India'] * 50
    
    # Cluster 2: South India
    x2 = np.random.normal(120000, 15000, 50)
    y2 = np.random.normal(55, 10, 50)
    region2 = ['South India'] * 50
    
    df = pd.DataFrame({
        'Per Capita Income (INR)': np.concatenate([x1, x2]),
        'Healthcare Deficit Index': np.concatenate([y1, y2]),
        'Region': np.concatenate([region1, region2])
    })
    
    # Ensure points stay roughly in specified bounds
    df['Per Capita Income (INR)'] = df['Per Capita Income (INR)'].clip(30000, 150000)
    df['Healthcare Deficit Index'] = df['Healthcare Deficit Index'].clip(0, 100)
    
    color_discrete_map = {
        'North India': '#8B0000', # Dark Red
        'South India': '#F37021' # Sun Pharma Orange
    }
    
    fig = px.scatter(
        df, 
        x='Per Capita Income (INR)', 
        y='Healthcare Deficit Index', 
        color='Region',
        color_discrete_map=color_discrete_map
    )
    
    # Add vertical and horizontal dotted lines to create 4 quadrants
    x_mid = 82500  # midpoint of 30k to 135k
    y_mid = 65     # midpoint
    
    fig.add_vline(x=x_mid, line_dash="dot", line_color="black", line_width=1.5, opacity=0.5)
    fig.add_hline(y=y_mid, line_dash="dot", line_color="black", line_width=1.5, opacity=0.5)
    
    fig.update_layout(
        title={
            'text': '<b>Market Viability: Wealth vs. Deficit</b>',
            'font': dict(color='#0F2046', size=12)
        },
        width=500,
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title='',
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        )
    )
    
    # Faint grey gridlines and axis ranges
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#F0F0F0', # Very faint grey
        range=[20000, 160000],
        zeroline=False,
        tickfont=dict(size=10),
        title_font=dict(size=11)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#F0F0F0', # Very faint grey
        range=[30, 110], # Zoom in nicely
        zeroline=False,
        tickfont=dict(size=10),
        title_font=dict(size=11)
    )
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Market_Viability_Scatter.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Scatter plot saved to {output_path}")

if __name__ == "__main__":
    create_scatter()
