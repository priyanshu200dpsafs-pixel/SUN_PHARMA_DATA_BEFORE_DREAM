import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.colors as mcolors

def create_funnel_chart():
    # Define Funnel Data
    stages = ["Impressions", "Click-Throughs", "Qualified Leads", "Rx Conversions"]
    values = [100000, 45000, 15000, 4000]
    
    # Calculate offsets to center the bars
    max_val = max(values)
    left_positions = [(max_val - val) / 2 for val in values]
    
    fig, ax = plt.subplots(figsize=(4.0, 6.0))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Gradient Colors: Deep Plum -> Crimson Red -> Soft Peach
    cmap = mcolors.LinearSegmentedColormap.from_list("funnel_cmap", ["#3B1F50", "#C33C4E", "#FAD7C3"])
    bar_colors = [cmap(i) for i in np.linspace(0, 1, len(values))]
    
    # Y positions (reverse so widest is at the top)
    y_pos = np.arange(len(stages))[::-1]
    
    # Draw the centered horizontal bars
    bars = ax.barh(y_pos, values, left=left_positions, height=0.7, color=bar_colors, edgecolor='none', zorder=2)
    
    # Draw connecting lines for the "funnel" shape
    for i in range(len(values) - 1):
        top_y = y_pos[i] - 0.35
        bot_y = y_pos[i+1] + 0.35
        
        top_left = left_positions[i]
        top_right = left_positions[i] + values[i]
        bot_left = left_positions[i+1]
        bot_right = left_positions[i+1] + values[i+1]
        
        # Connect left corners
        ax.plot([top_left, bot_left], [top_y, bot_y], color='#D3D3D3', linestyle=':', linewidth=1.5, zorder=1)
        # Connect right corners
        ax.plot([top_right, bot_right], [top_y, bot_y], color='#D3D3D3', linestyle=':', linewidth=1.5, zorder=1)
    
    ax.axis('off')
    
    # Add Data Labels inside the bars
    for i, (bar, stage, val) in enumerate(zip(bars, stages, values)):
        text_color = 'white'
        # The bottom bar (Soft Peach) is too light for white text, so use Deep Plum for contrast
        if i == len(values) - 1:
            text_color = '#3B1F50'
            
        # Add Stage Name
        ax.text(max_val / 2, bar.get_y() + bar.get_height() / 2 + 0.12,
                stage, ha='center', va='center', color=text_color, fontweight='bold', fontsize=12)
        # Add Numeric Value
        ax.text(max_val / 2, bar.get_y() + bar.get_height() / 2 - 0.15,
                f"{val:,}", ha='center', va='center', color=text_color, fontweight='normal', fontsize=11)
    
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Digital_Marketing_Funnel.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_funnel_chart()
