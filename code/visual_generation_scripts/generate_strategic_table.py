import plotly.graph_objects as go
import os

def create_table():
    headers = [
        '<b>Strategic Metric</b>', 
        '<b>Northern Belt (UP, Bihar, MP)</b>', 
        '<b>Southern/Western Belt (TN, Kerala, MH)</b>'
    ]
    
    col1 = [
        'Latent Healthcare Deficit', 
        'Chronic Disease Penetration', 
        'Out-of-Pocket Spend Capacity', 
        'Commercial Viability Score'
    ]
    
    col2 = [
        'Severe (85th Percentile)',
        '12% (Low Target)',
        '₹1,200 / year',
        'Low (Volume-driven, low margin)'
    ]
    
    col3 = [
        'Low/Moderate (35th Percentile)',
        '34% (High Target)',
        '₹5,800 / year',
        'High (Premium, recurring margin)'
    ]
    
    # Alternating row colors for 4 rows
    row_colors = ['#FFFFFF', '#F8F9FA', '#FFFFFF', '#F8F9FA']
    
    fig = go.Figure(data=[go.Table(
        columnwidth=[0.4, 0.3, 0.3],
        header=dict(
            values=headers,
            fill_color='#0F2046',
            align='center',
            font=dict(color='white', size=15),
            line=dict(color='#F37021', width=1),
            height=40
        ),
        cells=dict(
            values=[col1, col2, col3],
            fill_color=[row_colors, row_colors, row_colors],
            align=['left', 'center', 'center'], # Left-align metric, center data
            font=dict(color='#2D2D2D', size=13),
            line=dict(color='#F37021', width=1),
            height=45
        )
    )])
    
    # Force layout dimensions and make background transparent
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        width=900,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Strategic_Metrics_Table.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_table()
