import plotly.graph_objects as go
import os

def create_stacked_bar():
    categories = ['North Belt', 'South Belt']
    
    acute = [75, 35]
    chronic = [25, 65]
    
    fig = go.Figure(data=[
        go.Bar(
            name='Acute/Infectious Disease',
            x=categories,
            y=acute,
            marker_color='#D3D3D3',
            text=[f'{val}%' for val in acute],
            textposition='inside',
            insidetextfont=dict(color='black', size=12)
        ),
        go.Bar(
            name='Chronic/Lifestyle Disease',
            x=categories,
            y=chronic,
            marker_color='#0F2046',
            text=[f'{val}%' for val in chronic],
            textposition='inside',
            insidetextfont=dict(color='white', size=12)
        )
    ])
    
    fig.update_layout(
        barmode='stack',
        title={
            'text': '<b>Disease Burden Profile</b>',
            'font': dict(color='#0F2046', size=12)
        },
        width=400,
        height=350,
        margin=dict(l=20, r=20, t=50, b=40), # Added bottom margin for legend
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2, # Push legend below the x-axis
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        )
    )
    
    # Hide Y-axis numbers and lines
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title="")
    
    # Keep X-axis clean
    fig.update_xaxes(showgrid=False, zeroline=False, title="")
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Disease_Burden_Profile.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Stacked bar chart saved to {output_path}")

if __name__ == "__main__":
    create_stacked_bar()
