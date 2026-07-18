import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def create_kde_plot():
    np.random.seed(101)
    
    # Simulate overlapping normal distributions (representing data in log space)
    actual_log = np.random.normal(4.5, 0.9, 1000)
    predicted_log = np.random.normal(4.6, 0.85, 1000)
    
    fig, ax = plt.subplots(figsize=(4, 3))
    
    # Transparent backgrounds
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Generate KDE Plots
    sns.kdeplot(actual_log, fill=True, color='#0F2046', alpha=0.4, 
                linewidth=1.5, label='Actual Log Demand', ax=ax)
    sns.kdeplot(predicted_log, fill=True, color='#F37021', alpha=0.4, 
                linewidth=1.5, label='Predicted Log Demand', ax=ax)
                
    # Title & Labels
    ax.set_title('Log-Transformed Score Distribution', loc='center', 
                 color='#0F2046', fontsize=12, fontweight='bold', pad=15)
                 
    ax.set_xlabel('Log Value', fontsize=9, color='#2D2D2D', fontweight='bold')
    ax.set_ylabel('Density', fontsize=9, color='#2D2D2D', fontweight='bold')
    
    # Minimalist grey grid
    ax.grid(True, linestyle='-', color='#F0F0F0', alpha=1.0)
    
    # Clean up spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#C0C0C0')
    ax.spines['bottom'].set_color('#C0C0C0')
    
    ax.tick_params(axis='both', colors='#444444', labelsize=8)
    
    # Legend
    ax.legend(frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Log_KDE_Plot.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"KDE plot saved to {output_path}")

if __name__ == "__main__":
    create_kde_plot()
