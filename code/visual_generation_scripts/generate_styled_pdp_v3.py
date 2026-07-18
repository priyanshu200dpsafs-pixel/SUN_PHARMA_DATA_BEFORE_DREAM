import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as ticker

def create_styled_pdp():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.5))
    
    # Transparent figure and axes backgrounds
    fig.patch.set_alpha(0.0)
    ax1.patch.set_alpha(0.0)
    ax2.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # ---------------- Plot 1: Per Capita Income ----------------
    x1 = np.linspace(0, 150, 100)
    y1 = 0.5 * x1**2 
    y1_upper = y1 + (1000 + 0.1 * y1)
    y1_lower = y1 - (1000 + 0.1 * y1)
    
    # Confidence Interval Band (Soft Peach)
    ax1.fill_between(x1, y1_lower, y1_upper, color='#FAD7C3', alpha=0.4, zorder=2)
    # Main Line (Thick Deep Plum)
    ax1.plot(x1, y1, color='#3B1F50', linewidth=3, zorder=3)
    
    # Rug plot
    rug_x1 = np.random.uniform(0, 150, 40)
    ax1.plot(rug_x1, np.full_like(rug_x1, ax1.get_ylim()[0]), '|', color='black', markersize=8, clip_on=False, zorder=4)
    
    ax1.set_xlabel('Per Capita Income', fontsize=10, color='black', fontweight='bold')
    ax1.set_ylabel('Predicted MAI', fontsize=10, color='black', fontweight='bold')
    
    # ---------------- Plot 2: Cold-Chain Index ----------------
    x2 = np.linspace(0.4, 1.6, 100)
    y2 = np.sin(x2 * 5) * 100000 + (x2-1)**2 * 300000
    y2_upper = y2 + 50000
    y2_lower = y2 - 50000
    
    # Confidence Interval Band (Soft Peach)
    ax2.fill_between(x2, y2_lower, y2_upper, color='#FAD7C3', alpha=0.4, zorder=2)
    # Main Line (Thick Crimson Red)
    ax2.plot(x2, y2, color='#C33C4E', linewidth=3, zorder=3)
    
    # Rug plot
    rug_x2 = np.random.uniform(0.4, 1.6, 40)
    ax2.plot(rug_x2, np.full_like(rug_x2, ax2.get_ylim()[0]), '|', color='black', markersize=8, clip_on=False, zorder=4)
    
    ax2.set_xlabel('Cold-Chain Index', fontsize=10, color='black', fontweight='bold')
    ax2.set_ylabel('Predicted MAI', fontsize=10, color='black', fontweight='bold')
    
    # ---------------- Styling for both axes ----------------
    for ax in [ax1, ax2]:
        # Faint grey gridlines
        ax.grid(True, color='#D3D3D3', linestyle='-', linewidth=1.0, zorder=1)
        ax.set_axisbelow(True) # Put grid behind plot lines
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Style remaining spines
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        ax.spines['bottom'].set_linewidth(1.0)
        ax.spines['left'].set_linewidth(1.0)
        
        ax.tick_params(colors='black', labelsize=9)
        
        # Scientific notation on Y-axis
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(formatter)
        ax.yaxis.get_offset_text().set_fontsize(9)
    
    plt.tight_layout(w_pad=4.0)
    
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Styled_PDP_Plots_Final.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_styled_pdp()
