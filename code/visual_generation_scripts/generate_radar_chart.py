import plotly.graph_objects as go
import os

def create_radar_chart():
    categories = ['Raw Disease Prevalence', 'Per Capita Income', 'Infrastructure Readiness', 
                  'Urbanization Rate', 'Insurance Penetration']
    
    # We duplicate the first element at the end to explicitly close the loop for the line trace
    categories_closed = categories + [categories[0]]
    
    trace1_vals = [95, 20, 30, 40, 15]
    trace1_vals_closed = trace1_vals + [trace1_vals[0]]
    
    trace2_vals = [70, 90, 85, 80, 75]
    trace2_vals_closed = trace2_vals + [trace2_vals[0]]
    
    fig = go.Figure()
    
    # Trace 1 (Before MAI - The Flawed Approach)
    fig.add_trace(go.Scatterpolar(
        r=trace1_vals_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(211, 211, 211, 0.4)', # slightly transparent grey fill
        name='Targeting by Disease Only',
        line=dict(color='#A0A0A0', dash='dash', width=2) # Slightly darker grey line so it shows up well
    ))
    
    # Trace 2 (After MAI - The Smart Approach)
    fig.add_trace(go.Scatterpolar(
        r=trace2_vals_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(15, 32, 70, 0.25)', # soft Navy transparent fill
        name='Targeting via MAI Algorithm',
        mode='lines+markers',
        marker=dict(color='#F37021', size=8), # Sun Pharma Orange touch
        line=dict(color='#0F2046', width=3) # solid thick line
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=False, # Hide the numeric axis values (0-100)
                gridcolor='#E0E0E0',  # Soft grey circular gridlines
                range=[0, 100],
                linecolor='rgba(0,0,0,0)' # Hide the main radial spine
            ),
            angularaxis=dict(
                gridcolor='#E0E0E0',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(size=11, color='#2D2D2D') # Text formatting for the 5 axes
            ),
            bgcolor='rgba(0,0,0,0)' # Keep internal radar background transparent
        ),
        title={
            'text': '<b>Algorithm Impact: Shifting to High-Value Markets</b>',
            'font': dict(color='#0F2046', size=14),
            'x': 0.05,
            'xanchor': 'left'
        },
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.15, # Clearly at the top right
            xanchor="right",
            x=1.1,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.5)' # Slight background so it's readable if overlapping lines
        ),
        width=600,
        height=450,
        margin=dict(l=40, r=80, t=80, b=40),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent overall background
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Algorithm_Impact_Radar.png')
    
    # scale=3 generates a high resolution image (~300 DPI equivalent)
    fig.write_image(output_path, scale=3)
    print(f"Radar chart saved to {output_path}")

if __name__ == "__main__":
    create_radar_chart()
