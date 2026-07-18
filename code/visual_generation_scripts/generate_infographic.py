import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_infographic():
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Ensure transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib to use modern sans-serif
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # ---------------------------
    # BOX 1: The MAI Framework
    # ---------------------------
    box1_x, box1_y = 0.05, 0.53
    box1_w, box1_h = 0.9, 0.42
    
    rect1 = patches.FancyBboxPatch(
        (box1_x, box1_y), box1_w, box1_h, 
        boxstyle="round,pad=0.0,rounding_size=0.05", 
        linewidth=2, edgecolor='#0F2046', facecolor='#F8F9FA'
    )
    ax.add_patch(rect1)
    
    # Title 1
    ax.text(box1_x + 0.05, box1_y + box1_h - 0.06, '1. The MAI Framework', 
            fontsize=16, color='#0F2046', fontweight='bold', va='top')
    
    # Text 1
    text1_intro = "Evaluates 700+ districts across 3 weighted pillars:"
    ax.text(box1_x + 0.05, box1_y + box1_h - 0.14, text1_intro, 
            fontsize=11, color='#2D2D2D', va='top', fontweight='bold')
            
    text1_bullets = (
        "• Economic Velocity (40%): Out-of-pocket purchasing power.\n\n"
        "• Latent Demand (35%): Chronic lifestyle disease prevalence.\n\n"
        "• Infrastructure (25%): Pharmacy and cold-chain readiness."
    )
    ax.text(box1_x + 0.05, box1_y + box1_h - 0.20, text1_bullets, 
            fontsize=11, color='#444444', va='top', linespacing=1.6)

    # ---------------------------
    # BOX 2: Feature Engineering
    # ---------------------------
    box2_x, box2_y = 0.05, 0.05
    box2_w, box2_h = 0.9, 0.45
    
    rect2 = patches.FancyBboxPatch(
        (box2_x, box2_y), box2_w, box2_h, 
        boxstyle="round,pad=0.0,rounding_size=0.05", 
        linewidth=2, edgecolor='#F37021', facecolor='#F8F9FA'
    )
    ax.add_patch(rect2)
    
    # Title 2
    ax.text(box2_x + 0.05, box2_y + box2_h - 0.06, '2. Engineered Variables', 
            fontsize=16, color='#0F2046', fontweight='bold', va='top')
    
    # Bullet 2.1 Title
    ax.text(box2_x + 0.05, box2_y + box2_h - 0.15, '• Affordability Gap Ratio', 
            fontsize=12, color='#2D2D2D', fontweight='bold', va='top')
            
    # Bullet 2.1 Body
    text2_1 = (
        "   Formula: Per Capita Income / (Chronic Disease Rate + 1)\n"
        "   Impact: Prevents targeting high-disease, low-liquidity areas."
    )
    ax.text(box2_x + 0.05, box2_y + box2_h - 0.20, text2_1, 
            fontsize=11, color='#444444', va='top', linespacing=1.5)
            
    # Bullet 2.2 Title
    ax.text(box2_x + 0.05, box2_y + box2_h - 0.29, '• Infrastructure Penalty', 
            fontsize=12, color='#2D2D2D', fontweight='bold', va='top')
            
    # Bullet 2.2 Body
    text2_2 = (
        "   Formula: Disease Score × Cold_Chain_Index\n"
        "   Impact: Filters out areas lacking temperature-controlled logistics."
    )
    ax.text(box2_x + 0.05, box2_y + box2_h - 0.34, text2_2, 
            fontsize=11, color='#444444', va='top', linespacing=1.5)
            
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Methodology_Infographic.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Infographic saved to {output_path}")

if __name__ == "__main__":
    create_infographic()
