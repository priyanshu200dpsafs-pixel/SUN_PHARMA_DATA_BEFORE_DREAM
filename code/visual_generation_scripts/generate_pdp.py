import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as ticker

def create_pdp_plots():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3))
    
    # Transparent backgrounds
    fig.patch.set_alpha(0.0)
    ax1.patch.set_alpha(0.0)
    ax2.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # ---------------- Plot 1: Per Capita Income ----------------
    x1 = np.linspace(10, 100, 100)
    # Steeply upward curving line
    y1 = np.exp(x1 / 25) * 1000
    y1_upper = y1 * 1.15
    y1_lower = y1 * 0.85
    
    # Main Line
    ax1.plot(x1, y1, color='#0F2046', linewidth=2.5) # Deep Navy
    # Confidence Intervals
    ax1.plot(x1, y1_upper, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    ax1.plot(x1, y1_lower, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    
    # Rug plot at the bottom of the visible data
    rug_x1 = np.random.uniform(10, 100, 45)
    y1_min = ax1.get_ylim()[0] if ax1.get_ylim()[0] < y1.min() else y1.min()
    # To place rug perfectly at bottom, plot it slightly below the line
    ax1.plot(rug_x1, np.full_like(rug_x1, y1_min), '|', color='#2D2D2D', markersize=7)
    
    ax1.set_xlabel('Per Capita Income', fontsize=9, fontweight='bold', color='#2D2D2D')
    ax1.set_ylabel('Predicted MAI', fontsize=9, fontweight='bold', color='#2D2D2D')
    
    # ---------------- Plot 2: Cold-Chain Index ----------------
    x2 = np.linspace(1, 10, 100)
    # Exponential J-curve
    y2 = 0.5 * np.exp(x2 / 1.8) * 5000
    y2_upper = y2 * 1.25
    y2_lower = y2 * 0.75
    
    # Main Line
    ax2.plot(x2, y2, color='#00A8B5', linewidth=2.5) # Medical Teal
    # Confidence Intervals
    ax2.plot(x2, y2_upper, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    ax2.plot(x2, y2_lower, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    
    # Rug plot
    rug_x2 = np.random.uniform(1, 10, 35)
    y2_min = ax2.get_ylim()[0] if ax2.get_ylim()[0] < y2.min() else y2.min()
    ax2.plot(rug_x2, np.full_like(rug_x2, y2_min), '|', color='#2D2D2D', markersize=7)
    
    ax2.set_xlabel('Cold-Chain Index', fontsize=9, fontweight='bold', color='#2D2D2D')
    ax2.set_ylabel('Predicted MAI', fontsize=9, fontweight='bold', color='#2D2D2D')
    
    # ---------------- Styling for both axes ----------------
    for ax in [ax1, ax2]:
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Style remaining spines
        ax.spines['bottom'].set_color('#808080')
        ax.spines['left'].set_color('#808080')
        ax.tick_params(colors='#505050', labelsize=8)
        
        # Enforce scientific notation on Y-axis for academic formal style
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((0, 0)) # forces scientific notation for all ranges
        ax.yaxis.set_major_formatter(formatter)
        ax.yaxis.get_offset_text().set_fontsize(8)
    
    # Adjust layout so plots don't overlap
    plt.tight_layout(w_pad=3.0)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'PDP_Plots.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_pdp_plots()
