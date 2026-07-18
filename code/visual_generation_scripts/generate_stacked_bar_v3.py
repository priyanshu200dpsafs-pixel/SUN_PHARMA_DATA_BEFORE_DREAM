import matplotlib.pyplot as plt
import numpy as np
import os

def create_stacked_bar_v3():
    # Data
    labels = ['Traditional Launch', 'MAI-Optimized Launch']
    low_roi = [45, 15]
    high_roi = [55, 85]
    
    fig, ax = plt.subplots(figsize=(4, 2))
    
    # Transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Reverse order so "Traditional" is visually on top (barh plots bottom-up)
    labels_rev = labels[::-1]
    low_roi_rev = low_roi[::-1]
    high_roi_rev = high_roi[::-1]
    
    # Plot bars
    p1 = ax.barh(labels_rev, low_roi_rev, color='#0F2046', label='Low ROI Zones', height=0.6)
    p2 = ax.barh(labels_rev, high_roi_rev, left=low_roi_rev, color='#00A8B5', label='High ROI Zones', height=0.6)
    
    # Add percentage labels inside bars (all white text as requested)
    for rect in p1:
        width = rect.get_width()
        if width > 0:
            ax.text(rect.get_x() + width/2, rect.get_y() + rect.get_height()/2, 
                    f'{int(width)}%', ha='center', va='center', color='white', fontweight='bold', fontsize=8)
            
    for rect in p2:
        width = rect.get_width()
        if width > 0:
            ax.text(rect.get_x() + width/2, rect.get_y() + rect.get_height()/2, 
                    f'{int(width)}%', ha='center', va='center', color='white', fontweight='bold', fontsize=8)
                    
    # Styling & Title
    ax.set_title('Salesforce OPEX Reallocation', loc='left', color='#0F2046', fontsize=10, fontweight='bold', pad=10)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#E0E0E0')
    
    # Clean axes
    ax.set_xticks([]) # Remove x ticks as labels are inside
    ax.tick_params(axis='y', colors='#2D2D2D', labelsize=8)
    
    # Legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False, fontsize=7)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'OPEX_Reallocation_Bar_v3.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Stacked bar chart v3 saved to {output_path}")

if __name__ == "__main__":
    create_stacked_bar_v3()
