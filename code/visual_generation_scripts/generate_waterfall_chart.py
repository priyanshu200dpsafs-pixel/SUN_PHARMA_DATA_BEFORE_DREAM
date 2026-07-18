import matplotlib.pyplot as plt
import os

def create_waterfall_chart():
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Transparent backgrounds
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    categories = ['Baseline\nLaunch Budget', 'Tier 3 MR\nAvoidance', 'Logistics\nOptimization', 'MAI Optimized\nBudget']
    values = [1000, -250, -200, 550]
    
    # Calculate bottom positions for the bars
    # Step 1: Start at 0, goes up to 1000
    # Step 2: Starts at 1000, goes down by 250 (bottom is 1000, height is -250)
    # Step 3: Starts at 750, goes down by 200 (bottom is 750, height is -200)
    # Step 4: Final total starts at 0, goes up to 550
    bottoms = [0, 1000, 750, 0]
    
    colors = ['#B0B0B0', '#00A8B5', '#00A8B5', '#0F2046']
    
    # Plot bars
    bars = ax.bar(categories, values, bottom=bottoms, color=colors, width=0.6)
    
    # Add connecting lines between steps to emphasize the waterfall effect
    ax.plot([0.3, 0.7], [1000, 1000], color='#B0B0B0', linestyle='--', linewidth=1.5)
    ax.plot([1.3, 1.7], [750, 750], color='#00A8B5', linestyle='--', linewidth=1.5)
    ax.plot([2.3, 2.7], [550, 550], color='#00A8B5', linestyle='--', linewidth=1.5)
    
    # Add data labels
    for i, bar in enumerate(bars):
        height = values[i]
        bottom = bottoms[i]
        
        if height > 0:
            y_pos = bottom + height + 15
            text = f"{height}M"
            ax.text(bar.get_x() + bar.get_width()/2., y_pos, text, 
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=colors[i])
        else:
            y_pos = bottom + height - 15
            text = f"{height}M"
            ax.text(bar.get_x() + bar.get_width()/2., y_pos, text, 
                    ha='center', va='top', fontsize=9, fontweight='bold', color=colors[i])

    # Title
    ax.set_title('OPEX Efficiency Breakdown (INR Millions)', loc='left', color='#0F2046', fontsize=10, fontweight='bold', pad=25)
    
    # Clean spines and grid
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Hide y-axis entirely as we have data labels
    ax.set_yticks([])
    
    # Format x-axis
    ax.tick_params(axis='x', colors='#2D2D2D', labelsize=8, length=0)
    
    # Adjust y-limit to fit labels properly
    ax.set_ylim(0, 1150)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'OPEX_Waterfall_Chart.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_waterfall_chart()
