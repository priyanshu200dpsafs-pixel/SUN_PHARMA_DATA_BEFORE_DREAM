import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def create_formula_box():
    # Increased width to 8.5 to ensure the long text fits inside the bounding box comfortably
    fig, ax = plt.subplots(figsize=(8.5, 4.0))
    
    # Transparent figure background so it floats cleanly on the slide
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.axis('off')
    
    # Global Font Setting
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    # Use standard Computer Modern for math to make it look highly professional
    plt.rcParams['mathtext.fontset'] = 'cm'
    
    # Draw a crisp, rounded background box (Ice Blue / Light Grey)
    box = mpatches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                                  boxstyle="round,pad=0.0,rounding_size=0.03",
                                  edgecolor='#0F2046', facecolor='#F8F9FA', lw=1.5,
                                  transform=ax.transAxes, zorder=0)
    ax.add_patch(box)
    
    # Title
    ax.text(0.5, 0.88, "Expected Commercial Value (ECV) Formulation", 
            fontsize=13, fontweight='bold', color='#0F2046', ha='center', va='center')
    
    # Manually split lines to ensure math symbols are not broken mid-line
    lines1 = [
        "The financial projections are grounded in the following discounted cash flow",
        r"adaptation, where $P_t$ represents the MAI-predicted localized demand,",
        r"$M$ is the premium portfolio margin, and $C_t$ is the optimized regional OPEX:"
    ]
    ax.text(0.5, 0.65, "\n".join(lines1), fontsize=10, color='#2D2D2D', 
            ha='center', va='center', linespacing=1.6)
            
    # Formula (Rendered using Matplotlib MathText)
    formula = r"$ECV = \sum_{t=1}^{n} \frac{(P_t \cdot M) - C_t}{(1 + r)^t}$"
    ax.text(0.5, 0.35, formula, fontsize=18, color='#0F2046', ha='center', va='center')
    
    # Body text 2
    body2 = r"By minimizing $C_t$ through our XGBoost outputs, the overall ECV is mathematically maximized."
    ax.text(0.5, 0.12, body2, fontsize=10, color='#F37021', 
            ha='center', va='center', linespacing=1.5, fontweight='bold')
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'ECV_Formula_Box.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Formula box saved to {output_path}")

if __name__ == "__main__":
    create_formula_box()
