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
        'Low (Volume-driven)'
    ]
    
    col3 = [
        'Low/Moderate (35th Percentile)',
        '34% (High Target)',
        '₹5,800 / year',
        'High (Premium, recurring)'
    ]
    
    # Column shading colors
    col_colors = ['#E8EDF5', '#FFFFFF', '#FFF3E0']
    
    # Font colors per column
    text_colors = ['#2D2D2D', '#2D2D2D', '#0F2046']
    
    fig = go.Figure(data=[go.Table(
        columnwidth=[0.35, 0.325, 0.325],
        header=dict(
            values=headers,
            fill_color='#0F2046',
            align='center',
            font=dict(color='#FFFFFF', size=15),
            line=dict(color='#0F2046', width=1.5),
            height=45
        ),
        cells=dict(
            values=[col1, col2, col3],
            fill_color=col_colors,  # Plotly maps this list to each column respectively
            align=['left', 'center', 'center'],
            font=dict(color=text_colors, size=14),
            line=dict(color='#0F2046', width=1.5), # Thick crisp borders
            height=50 # Spacious row heights
        )
    )])
    
    # Force layout dimensions and make background transparent
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        width=950,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Advanced_Strategic_Table.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_table()
