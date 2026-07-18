import plotly.graph_objects as go
import os

def create_slopegraph():
    # Define data mapping
    districts = [
        {'name': 'Patna (BR)', 'left': 1, 'right': 8, 'color': '#B0B0B0', 'width': 2},
        {'name': 'Lucknow (UP)', 'left': 2, 'right': 6, 'color': '#B0B0B0', 'width': 2},
        {'name': 'Pune (MH)', 'left': 5, 'right': 1, 'color': '#F37021', 'width': 4},
        {'name': 'Ernakulam (KL)', 'left': 7, 'right': 2, 'color': '#F37021', 'width': 4},
        {'name': 'Chennai (TN)', 'left': 4, 'right': 3, 'color': '#0F2046', 'width': 3}
    ]
    
    x_labels = ['Raw Disease Rank', 'Final MAI Rank']
    x_vals = [0, 1]
    
    fig = go.Figure()
    
    # Plot each line
    for d in districts:
        # We append rank numbers to the names for extra clarity, or just display the name since we hide Y-axis
        text_left = f"{d['left']} - {d['name']}"
        text_right = f"{d['name']} - {d['right']}"
        
        # Add bold for the highlighted lines
        font_weight = "bold" if d['width'] > 2 else "normal"
        text_template_left = f"<b>{text_left}</b>" if font_weight == "bold" else text_left
        text_template_right = f"<b>{text_right}</b>" if font_weight == "bold" else text_right
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=[d['left'], d['right']],
            mode='lines+markers+text',
            text=[text_template_left, text_template_right],
            textposition=['middle left', 'middle right'],
            textfont=dict(color=d['color'], size=11),
            line=dict(color=d['color'], width=d['width']),
            marker=dict(color=d['color'], size=8),
            name=d['name'],
            showlegend=False
        ))
        
    fig.update_layout(
        title={
            'text': '<b>The MAI Correction: Shifting Focus to Commercial Viability</b>',
            'font': dict(color='#0F2046', size=14),
            'x': 0.05,
            'xanchor': 'left'
        },
        xaxis=dict(
            tickmode='array',
            tickvals=x_vals,
            ticktext=[f"<b>{t}</b>" for t in x_labels],
            showgrid=False,
            zeroline=False,
            range=[-0.6, 1.6], # Padding so the long district names aren't cut off
            side='top',
            tickfont=dict(size=13, color='#0F2046')
        ),
        yaxis=dict(
            autorange="reversed", # Rank 1 at top, Rank 8 at bottom
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        width=500,
        height=450,
        margin=dict(l=20, r=20, t=100, b=40),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Draw custom vertical lines to act as the two axes spines
    fig.add_shape(type="line", x0=0, x1=0, y0=0.5, y1=8.5, line=dict(color="#A0A0A0", width=1.5))
    fig.add_shape(type="line", x0=1, x1=1, y0=0.5, y1=8.5, line=dict(color="#A0A0A0", width=1.5))

    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'MAI_Slopegraph.png')
    
    fig.write_image(output_path, scale=3)
    print(f"Slopegraph saved to {output_path}")

if __name__ == "__main__":
    create_slopegraph()
