import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as ticker

def create_styled_pdp():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.5))
    fig.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # ---------------- Plot 1: Per Capita Income ----------------
    x1 = np.linspace(0, 150, 100)
    y1 = 0.5 * x1**2 
    y1_upper = y1 + (1000 + 0.1 * y1)
    y1_lower = y1 - (1000 + 0.1 * y1)
    
    ax1.set_facecolor('white')
    
    # R mgcv GAM style
    ax1.plot(x1, y1, color='black', linewidth=1.2)
    ax1.plot(x1, y1_upper, color='red', linestyle=':', linewidth=1.2)
    ax1.plot(x1, y1_lower, color='red', linestyle=':', linewidth=1.2)
    
    # Rug plot
    rug_x1 = np.random.uniform(0, 150, 40)
    ax1.plot(rug_x1, np.full_like(rug_x1, ax1.get_ylim()[0]), '|', color='black', markersize=8, clip_on=False)
    
    ax1.set_xlabel('per_capita_income', fontsize=10, color='black')
    ax1.set_ylabel('ns(per_capita_income, 5)', fontsize=10, color='black')
    
    # ---------------- Plot 2: Cold-Chain Index ----------------
    x2 = np.linspace(0.4, 1.6, 100)
    # create a curve similar to the winner's second plot
    y2 = np.sin(x2 * 5) * 100000 + (x2-1)**2 * 300000
    y2_upper = y2 + 50000
    y2_lower = y2 - 50000
    
    ax2.set_facecolor('white')
    
    ax2.plot(x2, y2, color='black', linewidth=1.2)
    ax2.plot(x2, y2_upper, color='red', linestyle=':', linewidth=1.2)
    ax2.plot(x2, y2_lower, color='red', linestyle=':', linewidth=1.2)
    
    rug_x2 = np.random.uniform(0.4, 1.6, 40)
    ax2.plot(rug_x2, np.full_like(rug_x2, ax2.get_ylim()[0]), '|', color='black', markersize=8, clip_on=False)
    
    ax2.set_xlabel('cold_chain_index', fontsize=10, color='black')
    ax2.set_ylabel('ns(cold_chain_index, 5)', fontsize=10, color='black')
    
    # ---------------- Styling for both axes ----------------
    for ax in [ax1, ax2]:
        # Full box frame
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1.0)
            
        # Outward ticks on bottom and left only
        ax.tick_params(direction='out', color='black', length=6, width=1.0, 
                       bottom=True, left=True, top=False, right=False, labelsize=9)
        
        # Scientific notation on Y-axis
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(formatter)
        ax.yaxis.get_offset_text().set_fontsize(9)
        
        # Rotate y-axis tick labels to 90 degrees like the winner's plot
        ax.tick_params(axis='y', labelrotation=90)
    
    plt.tight_layout(w_pad=4.0)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Styled_PDP_Plots.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_styled_pdp()
