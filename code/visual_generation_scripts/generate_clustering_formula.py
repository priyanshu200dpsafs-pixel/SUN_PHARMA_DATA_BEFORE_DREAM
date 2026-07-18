import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def create_formula_box():
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    fig.patch.set_alpha(0.0)
    
    ax.axis('off') # Turn off spines and ticks
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
    plt.rcParams['mathtext.fontset'] = 'cm' # Standard academic math font
    
    # Add rounded box with thin 1px Deep Plum border and darker peach background
    box = mpatches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                                  boxstyle="round,pad=0.0,rounding_size=0.04",
                                  edgecolor='#3B1F50', facecolor='#FAD7C3', lw=1.0,
                                  transform=ax.transAxes, zorder=0)
    ax.add_patch(box)
    
    # Title (black, bold, top-left aligned like the winner's slide)
    ax.text(0.04, 0.88, "Spatial Clustering Formulation (Gaussian Mixture)", 
            fontsize=12, fontweight='bold', color='black', ha='left', va='center')
    
    # Formula (centered)
    formula = r"$\ln p(X | \pi, \mu, \Sigma) = \sum_{n=1}^{N} \ln \left( \sum_{k=1}^{K} \pi_k \mathcal{N}(x_n | \mu_k, \Sigma_k) \right)$"
    ax.text(0.5, 0.55, formula, fontsize=16, color='black', ha='center', va='center')
    
    # Subtitle/Formula definition (italic, small, centered)
    ax.text(0.5, 0.15, "predicted_mai ~ ns(latitude, 5) + ns(longitude, 5) + per_capita_income", 
            fontsize=10, style='italic', color='black', ha='center', va='center')
    
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Clustering_Formula_Box_Final.png')
    
    # Save with transparent background (so the white rounded box floats on the slide)
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Formula box saved to {output_path}")

if __name__ == "__main__":
    create_formula_box()
