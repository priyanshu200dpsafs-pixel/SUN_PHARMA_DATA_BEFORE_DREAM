import matplotlib.pyplot as plt
import os
import textwrap

def create_timeline():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Phase Data tied to Tier colors
    phases = [
        {
            "title": "Phase 1 (Months 0-3)",
            "desc": "Resource concentration in Tier 1 markets. Deploy physical representatives and premium portfolio.",
            "color": "#F37021" # Tier 1 Orange
        },
        {
            "title": "Phase 2 (Months 4-6)",
            "desc": "Digital seeding in Tier 2. Establish localized cold-chain hubs prior to physical expansion.",
            "color": "#0F2046" # Tier 2 Deep Navy
        },
        {
            "title": "Phase 3 (Months 7-12)",
            "desc": "Baseline monitoring in Tier 3. Assess public infrastructure triggers to prevent premature OPEX burn.",
            "color": "#707070" # Tier 3 Dark Grey
        }
    ]
    
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    
    # Title
    ax.text(0.2, 10, "Phased Implementation Timeline", fontsize=14, fontweight='bold', color='#0F2046', ha='left')
    
    y_start = 8.0
    y_gap = 3.0
    
    for i, phase in enumerate(phases):
        y = y_start - i * y_gap
        
        # Draw a sleek vertical bar for emphasis on the side
        ax.plot([0.5, 0.5], [y - 0.5, y + 0.8], color=phase["color"], linewidth=5, solid_capstyle='round')
        
        # Draw timeline dot matching the map's Google Pins look
        ax.scatter([0.5], [y + 0.8], s=200, color=phase["color"], zorder=5)
        ax.scatter([0.5], [y + 0.8], s=50, color='white', zorder=6)
        
        # Connector line to the next phase
        if i < len(phases) - 1:
            ax.plot([0.5, 0.5], [y - 0.5, y - y_gap + 0.8], color='#D3D3D3', linewidth=2, linestyle='--')
            
        # Add Title
        ax.text(1.2, y + 0.6, phase["title"], fontsize=11, fontweight='bold', color=phase["color"], va='center')
        
        # Add Description
        wrapped_desc = "\n".join(textwrap.wrap(phase["desc"], width=75))
        ax.text(1.2, y + 0.1, wrapped_desc, fontsize=9, color='#2D2D2D', va='top', linespacing=1.6)
        
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Implementation_Timeline.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Timeline saved to {output_path}")

if __name__ == "__main__":
    create_timeline()
