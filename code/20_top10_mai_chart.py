import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(BASE_DIR, 'outputs', 'presentation_visuals')
os.makedirs(OUT_DIR, exist_ok=True)

def generate_chart():
    # Data as specified
    districts = [
        "Ernakulam", "Thiruvananthapuram", "Coimbatore", "Thrissur", 
        "Chennai", "Kollam", "Alappuzha", "Thane", "Surat", "Thiruvallur"
    ]
    # Scores ranging from 98 down to 81
    scores = [98.0, 96.5, 94.2, 92.0, 90.1, 88.5, 87.0, 85.5, 83.2, 81.0]
    
    df = pd.DataFrame({'District': districts, 'MAI Score': scores})
    
    # Setup styling (Arial, bold, size 14)
    # plt.rcParams['font.family'] = 'sans-serif'
    # plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    font_props = {'family': 'sans-serif', 'weight': 'bold', 'size': 14}
    
    # Create the figure with a transparent background
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Generate gradient color palette from Dark Navy Blue to Peach/Orange
    # Dark Navy: #000080, Peach/Orange: #FFC0CB / #FF9933
    color_start = mcolors.to_rgba("#001f3f") # Dark Navy
    color_end = mcolors.to_rgba("#ff9f43")   # Peach/Orange
    
    # Interpolate colors
    cmap = mcolors.LinearSegmentedColormap.from_list("navy_peach", [color_start, color_end])
    colors = [cmap(i) for i in np.linspace(0, 1, len(districts))]
    
    # Plot horizontal bar chart
    bars = ax.barh(df['District'], df['MAI Score'], color=colors, edgecolor='none')
    
    # Invert y-axis so the highest score is at the top
    ax.invert_yaxis()
    
    # Set x-axis limit slightly wider to give bars breathing room, but start at ~80 to emphasize differences
    ax.set_xlim(80, 100)
    
    # Apply label styles
    ax.set_xlabel("MAI Score", fontdict=font_props, labelpad=10)
    ax.set_ylabel("District", fontdict=font_props, labelpad=10)
    
    # Set tick labels to bold and size 14
    plt.xticks(fontsize=14, fontweight='bold', family='sans-serif')
    plt.yticks(fontsize=14, fontweight='bold', family='sans-serif')
    
    # Remove gridlines
    ax.grid(False)
    
    # Remove borders/spines for a cleaner look
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    # Add data labels to the bars
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width - 1.5 if width > 85 else width + 0.5
        align = 'right' if width > 85 else 'left'
        color = 'white' if width > 85 else 'black'
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.1f}',
                ha=align, va='center', fontweight='bold', fontsize=12, color=color, family='sans-serif')
    
    plt.tight_layout()
    
    # Save as high-resolution PNG with transparent background
    out_path = os.path.join(OUT_DIR, 'Top10_MAI_Districts.png')
    plt.savefig(out_path, dpi=300, transparent=True, format='png', bbox_inches='tight')
    print(f"Chart successfully saved to {out_path}")

if __name__ == "__main__":
    generate_chart()
