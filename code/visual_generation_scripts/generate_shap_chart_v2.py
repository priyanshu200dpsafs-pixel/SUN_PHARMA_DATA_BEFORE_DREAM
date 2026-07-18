import matplotlib.pyplot as plt
import os

def create_shap_chart_v2():
    # Features in reverse order so they plot top-to-bottom
    features = [
        'Sum of 10 other features',
        'Chronic Disease Rate',
        'Affordability Gap',
        'Pharmacy Density',
        'Economic Velocity'
    ]
    scores = [0.25, 0.55, 0.64, 0.72, 0.85]
    
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib to use modern sans-serif
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Top 3 bars (last 3 items in barh) in Orange, rest in Grey
    colors = ['#B0B0B0', '#B0B0B0', '#F37021', '#F37021', '#F37021']
    
    bars = ax.barh(features, scores, color=colors, height=0.6)
    
    # No top/right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Make bottom and left spines thin and light grey
    ax.spines['left'].set_color('#E0E0E0')
    ax.spines['bottom'].set_color('#E0E0E0')
    
    # Add data labels at the end of each bar showing the exact score
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                va='center', ha='left', fontsize=10, color='#2D2D2D', fontweight='bold')
                
    # Title
    ax.set_title('SHAP Value Impact', 
                 loc='left', color='#0F2046', fontsize=12, fontweight='bold', pad=15)
                 
    # Set custom ticks correctly to avoid matplotlib warnings
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features, fontweight='bold', color='#2D2D2D', fontsize=10)
    
    ax.tick_params(axis='y', colors='#2D2D2D')
    ax.tick_params(axis='x', colors='#808080')
    
    ax.set_xlim(0, 0.95)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'SHAP_Feature_Importance_v2.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"SHAP chart saved to {output_path}")

if __name__ == "__main__":
    create_shap_chart_v2()
