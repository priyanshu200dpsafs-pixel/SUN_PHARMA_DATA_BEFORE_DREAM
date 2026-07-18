import plotly.graph_objects as go
import os

def create_tier_table():
    headers = [
        '<b>Priority Tier</b>', 
        '<b>Key Target Districts</b>', 
        '<b>Investment Strategy</b>'
    ]
    
    col1 = [
        '<b>Tier 1 (High Priority)</b>', 
        '<b>Tier 2 (Medium Priority)</b>', 
        '<b>Tier 3 (Background)</b>'
    ]
    
    col2 = [
        'Pune, Mumbai, Bengaluru, Chennai, Ernakulam',
        'Ahmedabad, Hyderabad, Coimbatore, Nashik',
        'Patna, Lucknow, Jaipur'
    ]
    
    col3 = [
        'Immediate Salesforce OPEX Reallocation',
        'Phased Strategic Expansion',
        'Minimal Resource Allocation'
    ]
    
    # Color mapping according to the precise style instructions
    header_color = '#0F2046'  # Deep Navy Blue
    row1_color = '#FFF3E0'    # Very Light Peach/Orange (matching hotspot)
    row2_color = '#F0F4F8'    # Very Light Ice Blue
    row3_color = '#FFFFFF'    # Pure White
    
    row_colors = [row1_color, row2_color, row3_color]
    
    fig = go.Figure(data=[go.Table(
        columnwidth=[0.25, 0.45, 0.3],
        header=dict(
            values=headers,
            fill_color=header_color,
            align='center',
            font=dict(color='white', size=14),
            line=dict(color='#0F2046', width=1),
            height=40
        ),
        cells=dict(
            values=[col1, col2, col3],
            fill_color=[row_colors]*3, # Apply colors row by row across all columns
            align=['center', 'left', 'center'],
            font=dict(color='#2D2D2D', size=13),
            line=dict(color='#D3D3D3', width=1),
            height=45
        )
    )])
    
    # Make layout transparent and tight
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        width=800,
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Tier_Strategy_Table.png')
    
    fig.write_image(output_path, scale=3)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_tier_table()
