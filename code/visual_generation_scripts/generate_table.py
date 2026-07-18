import plotly.graph_objects as go
import os

def create_table():
    headers = [
        '<b>Macro Dimension</b>', 
        '<b>Final Retained Variables (Top 5 per category)</b>', 
        '<b>Justification for Retention (VIF < 5)</b>'
    ]
    
    col1 = ['Latent Demand', 'Infrastructure', 'Eco. Velocity']
    
    col2 = [
        '1. Chronic Disease Prev.<br>2. Out-of-Pocket Exp.<br>3. Infant Mortality<br>4. Geriatric Pop %<br>5. Undiagnosed Rate',
        '1. PHC Density<br>2. Cold-Chain Index<br>3. Road Conn. (PMGSY)<br>4. Pharmacy Density<br>5. Supply Chain Proximity',
        '1. Per Capita Income<br>2. Urbanization Growth<br>3. Tech Adoption %<br>4. Insured Population %<br>5. Female Workforce %'
    ]
    
    col3 = [
        'High variance across Tier-2/3; direct proxy for recurring chronic drug sales.',
        'Independent metrics ensuring Sun Pharma logistics can physically reach the market.',
        'Proves out-of-pocket purchasing power for premium branded generics.'
    ]
    
    # Alternating row colors
    row_colors = ['#FFFFFF', '#F8F9FA', '#FFFFFF']
    
    fig = go.Figure(data=[go.Table(
        columnwidth=[0.2, 0.4, 0.4],
        header=dict(
            values=headers,
            fill_color='#0F2046',
            align='center',
            font=dict(color='white', size=18),
            line=dict(color='#C85716', width=2), # Darker orange and thicker
            height=80
        ),
        cells=dict(
            values=[col1, col2, col3],
            fill_color=[row_colors, row_colors, row_colors],
            align=['center', 'left', 'left'], # Macro Dimension centered, others left
            font=dict(color='#2D2D2D', size=15),
            line=dict(color='#C85716', width=2), # Darker orange and thicker
            height=140
        )
    )])
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        width=1200,
        height=550
    )
    
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Variable_Retention_Table.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_table()
