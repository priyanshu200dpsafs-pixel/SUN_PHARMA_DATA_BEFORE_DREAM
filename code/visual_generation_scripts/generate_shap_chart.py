import matplotlib.pyplot as plt
import os
import numpy as np

def create_shap_chart():
    # Features in reverse order so they plot top-to-bottom
    features = [
        'Urbanization Growth',
        'Geriatric Population %',
        'Chronic Disease Prevalence',
        'Affordability Gap Ratio',
        'Infrastructure & Cold Chain Index',
        'Economic Velocity (Purchasing Power)'
    ]
    scores = [0.20, 0.35, 0.55, 0.64, 0.72, 0.85]
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Ensure transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib to use modern sans-serif
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Bar Colors: The top 3 bars must be Sun Pharma Orange. The bottom 3 must be Grey.
    # Note: barh plots from bottom to top, so the last 3 items in the list are the 'top' bars visually.
    colors = ['#B0B0B0', '#B0B0B0', '#B0B0B0', '#F37021', '#F37021', '#F37021']
    
    bars = ax.barh(features, scores, color=colors, height=0.6)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Make bottom and left spines thin and light grey
    ax.spines['left'].set_color('#E0E0E0')
    ax.spines['bottom'].set_color('#E0E0E0')
    
    # Add data labels at the end of each bar showing the exact score
    for bar in bars:
        width = bar.get_width()
        # Add a tiny padding (0.015) to x coordinate
        ax.text(width + 0.015, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                va='center', ha='left', fontsize=11, color='#2D2D2D', fontweight='bold')
                
    # Title
    ax.set_title('SHAP Feature Importance: Drivers of Commercial Viability', 
                 loc='left', color='#0F2046', fontsize=14, fontweight='bold', pad=20)
                 
    # Ensure y-axis labels are fully visible, bold, and dark grey
    ax.set_yticklabels(features, fontweight='bold', color='#2D2D2D', fontsize=11)
    ax.tick_params(axis='y', colors='#2D2D2D')
    ax.tick_params(axis='x', colors='#808080')
    
    # Extend x-axis slightly so labels don't get cut off
    ax.set_xlim(0, 0.95)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'SHAP_Feature_Importance.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"SHAP chart saved to {output_path}")

if __name__ == "__main__":
    create_shap_chart()
