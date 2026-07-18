import plotly.express as px
import pandas as pd
import os

def create_bar_chart():
    # Data
    districts = ['Ernakulam (KL)', 'Chennai (TN)', 'Pune (MH)', 'Bengaluru (KA)', 'Hyderabad (TG)', 
                 'Thiruvananthapuram (KL)', 'Coimbatore (TN)', 'Ahmedabad (GJ)', 'Nashik (MH)', 'Indore (MP)']
    mai_scores = [92.4, 89.1, 87.5, 85.2, 83.8, 81.0, 79.5, 76.2, 74.8, 71.5]
    
    df = pd.DataFrame({
        'District': districts,
        'MAI Score': mai_scores
    })
    
    # Create the Vertical Bar Chart
    fig = px.bar(
        df, 
        x='District', 
        y='MAI Score',
        text='MAI Score' # Places the value on top
    )
    
    # Styling Traces (Bars and text)
    fig.update_traces(
        marker_color='#0F2046', # Deep Sun Pharma Navy Blue
        textposition='outside', # On top of the bars
        texttemplate='<b>%{text}</b>', # Bold text
        textfont=dict(size=10, color='#2D2D2D') # Font sizing and color
    )
    
    # Overall Layout Formatting
    fig.update_layout(
        title={
            'text': '<b>Top 10 High-Value Districts by MAI Score</b>',
            'font': dict(color='#0F2046', size=14),
            'x': 0.05,
            'xanchor': 'left'
        },
        width=650,
        height=350,
        margin=dict(l=20, r=20, t=60, b=80), # Extra space on top/bottom for labels
        paper_bgcolor='rgba(0,0,0,0)', # Transparent Background
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Remove Y-Axis Redundancies
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title='', range=[0, 105]) # Range added so top labels aren't cut off
    
    # Format X-Axis
    fig.update_xaxes(
        tickangle=-35, # Rotated slightly for readability
        showgrid=False, 
        zeroline=False, 
        title='',
        tickfont=dict(size=10)
    )
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Top10_MAI_BarChart.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Bar chart saved to {output_path}")

if __name__ == "__main__":
    create_bar_chart()
