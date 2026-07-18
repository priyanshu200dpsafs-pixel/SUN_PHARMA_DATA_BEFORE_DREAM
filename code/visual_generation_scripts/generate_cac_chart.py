import matplotlib.pyplot as plt
import os

def create_cac_chart():
    # Define Data (Ordered bottom to top in horizontal bar chart)
    labels = ['MAI-Targeted CAC', 'Traditional CAC']
    values = [650, 1200]
    colors = ['#3B1F50', '#D3D3D3'] # Deep Plum for MAI, Light Grey for Traditional
    
    # Initialize figure
    fig, ax = plt.subplots(figsize=(5, 2))
    
    # Fully transparent figure and axes backgrounds
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    
    # Plot horizontal bars
    bars = ax.barh(labels, values, color=colors, height=0.55)
    
    # Strip unnecessary spines (Top, Right, Bottom)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Style the left spine subtly
    ax.spines['left'].set_color('#333333')
    ax.spines['left'].set_linewidth(1.0)
    
    # Remove x-axis tick marks entirely since we will label the bars directly
    ax.xaxis.set_ticks([])
    
    # Clean up y-axis labels
    ax.tick_params(axis='y', colors='black', labelsize=10, length=0, pad=10)
    
    # Append precise Data Labels to the right of each bar
    for bar in bars:
        width = bar.get_width()
        label_text = f"₹{int(width):,}"
        
        # Emphasize the MAI-Targeted label
        text_color = '#3B1F50' if width == 650 else '#808080'
        fontweight = 'bold' if width == 650 else 'normal'
        
        ax.text(width + 25, bar.get_y() + bar.get_height()/2, label_text, 
                ha='left', va='center', fontsize=12, color=text_color, fontweight=fontweight)

    # Save logic
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'CAC_Comparison.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_cac_chart()
