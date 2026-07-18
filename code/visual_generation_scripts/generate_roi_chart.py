import matplotlib.pyplot as plt
import numpy as np
import os

def create_roi_chart():
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Transparent backgrounds
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    quarters = np.arange(1, 13)
    x_labels = [f"Q{i}" for i in quarters]
    
    # Simulate Data
    # Traditional Strategy: linear slope ending at 1.2x
    trad_y = np.linspace(0.1, 1.2, 12)
    
    # MAI-Optimized Strategy: J-curve slope ending at 3.5x
    # We use an exponential curve and scale it from ~0.1 to 3.5
    mai_y = np.exp(np.linspace(-2, 1.5, 12))
    mai_y = (mai_y - mai_y.min()) / (mai_y.max() - mai_y.min()) * 3.4 + 0.1
    
    # To make the J-curve slightly dip or stay flat early on to simulate investment phase:
    # A polynomial or modified exp is better.
    mai_y = 0.1 + 3.4 * ((quarters - 1) / 11)**3 # Cubic curve gives a perfect J-curve look!
    
    # Plot Traditional
    ax.plot(quarters, trad_y, color='#A0A0A0', linewidth=2, label='Traditional Strategy')
    ax.fill_between(quarters, 0, trad_y, color='#B0B0B0', alpha=0.15)
    
    # Plot MAI-Optimized
    ax.plot(quarters, mai_y, color='#0F2046', linewidth=3, label='MAI-Optimized Strategy')
    ax.fill_between(quarters, 0, mai_y, color='#00A8B5', alpha=0.25) # Medical Teal fill
    
    # Dashed line at Q4 (Infrastructure Break-Even Point)
    ax.axvline(x=4, color='#F37021', linestyle='--', linewidth=1.5, zorder=0)
    
    # Label for Q4 line
    ax.text(4.2, 2.5, 'Infrastructure\nBreak-Even\nPoint', color='#F37021', 
            fontsize=8, fontweight='bold', va='center', ha='left')
            
    # Styling
    ax.set_title('3-Year Cumulative ROI Divergence', loc='left', color='#0F2046', fontsize=10, fontweight='bold', pad=15)
    ax.set_ylabel('Return on Investment (Multiple)', color='#2D2D2D', fontsize=9, fontweight='bold')
    
    # Clean spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#808080')
    ax.spines['left'].set_color('#808080')
    
    # Ticks
    ax.set_xticks(quarters)
    ax.set_xticklabels(x_labels, fontsize=8, color='#505050')
    ax.tick_params(axis='y', colors='#505050', labelsize=8)
    
    ax.set_ylim(0, 4.0)
    ax.set_xlim(1, 12)
    
    # Legend
    ax.legend(loc='upper left', frameon=False, fontsize=8)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Cumulative_ROI_Projection.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_roi_chart()
