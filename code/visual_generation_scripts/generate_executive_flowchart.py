import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
import os

def create_flowchart():
    fig, ax = plt.subplots(figsize=(11, 2.5)) # Slightly wider and taller for padding
    
    # Transparent figure background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.axis('off')
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Define block properties
    blocks = [
        {
            "header": "THE PROBLEM",
            "body": "High-OPEX\nTraditional Launches",
            "facecolor": "#E8EDF5", # Light crisp grey
            "header_color": "#F37021", # Orange header for pop
            "body_color": "#0F2046",
            "x": 0.02
        },
        {
            "header": "THE SOLUTION",
            "body": "XGBoost\nMAI Framework",
            "facecolor": "#0F2046", # Deep Navy
            "header_color": "#F37021",
            "body_color": "white",
            "x": 0.36
        },
        {
            "header": "THE IMPACT",
            "body": "Accelerated Break-Even\n& OPEX Efficiency",
            "facecolor": "#00A8B5", # Medical Teal
            "header_color": "#F37021",
            "body_color": "white",
            "x": 0.70
        }
    ]
    
    block_width = 0.28
    block_height = 0.65
    y_pos = 0.15
    
    # Draw blocks
    for b in blocks:
        # Sharp rectangle
        rect = patches.Rectangle((b["x"], y_pos), block_width, block_height, 
                                 linewidth=0, facecolor=b["facecolor"], zorder=2)
        ax.add_patch(rect)
        
        # Header text
        ax.text(b["x"] + block_width/2, y_pos + block_height - 0.12, 
                b["header"], color=b["header_color"], fontsize=9, fontweight='bold',
                ha='center', va='top', zorder=3)
                
        # Body text
        ax.text(b["x"] + block_width/2, y_pos + block_height/2 - 0.05, 
                b["body"], color=b["body_color"], fontsize=10.5, fontweight='bold',
                ha='center', va='center', zorder=3, linespacing=1.4)
                
    # Draw arrows
    # Arrow 1: from Block 1 to Block 2
    ax.annotate('', xy=(0.36, 0.475), xytext=(0.30, 0.475),
                arrowprops=dict(facecolor='#F37021', edgecolor='none', width=6, headwidth=14), zorder=1)
                
    # Arrow 2: from Block 2 to Block 3
    ax.annotate('', xy=(0.70, 0.475), xytext=(0.64, 0.475),
                arrowprops=dict(facecolor='#F37021', edgecolor='none', width=6, headwidth=14), zorder=1)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Executive_Flowchart.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Flowchart saved to {output_path}")

if __name__ == "__main__":
    create_flowchart()
