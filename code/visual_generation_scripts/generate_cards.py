import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
import os

def create_cards():
    cards = [
        {
            'icon': '₹',
            'title': 'Economic Velocity (40% Weight)',
            'vars': 'Variables: Per Capita Income, Urbanization Growth, Insured Population %.',
            'rationale': 'Rationale: The heaviest weight. Ensures the target market has the actual out-of-pocket liquidity to afford premium therapies.',
            'bg_color': '#FFF3E0', 
            'edge_color': '#F37021', 
            'title_color': '#D95B12'
        },
        {
            'icon': '♥', 
            'title': 'Latent Demand (35% Weight)',
            'vars': 'Variables: Chronic Disease Prevalence, Geriatric Population %, Undiagnosed Rate.',
            'rationale': 'Rationale: Targets structural, recurring disease pools rather than seasonal acute spikes.',
            'bg_color': '#FFEBEE', 
            'edge_color': '#B22222',
            'title_color': '#8B0000' 
        },
        {
            'icon': '✚', 
            'title': 'Infrastructure (25% Weight)',
            'vars': 'Variables: Pharmacy Density, Cold-Chain Index, Road Connectivity.',
            'rationale': 'Rationale: Acts as a commercial feasibility filter ensuring Sun Pharma logistics network can physically deploy the drugs.',
            'bg_color': '#E8EDF5', 
            'edge_color': '#0F2046',
            'title_color': '#0F2046' 
        }
    ]
    
    output_dir = '/Users/priyanshu/Desktop'
    
    for i, card in enumerate(cards):
        # Shorter, more horizontal figure size
        fig, ax = plt.subplots(figsize=(11, 4.5))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        card_width = 0.96
        card_height = 0.90
        x = 0.02
        y = 0.05
        
        # 1. Background Box
        rect = patches.FancyBboxPatch((x, y), card_width, card_height, 
                                      boxstyle="round,pad=0.0,rounding_size=0.05", 
                                      linewidth=4, edgecolor=card['edge_color'], 
                                      facecolor=card['bg_color'])
        ax.add_patch(rect)
        
        # 2. Icon (Top Left)
        ax.text(x + 0.05, y + card_height - 0.08, card['icon'], fontsize=35, 
                color=card['title_color'], fontweight='bold', va='top')
        
        # 3. Title (Next to Icon)
        ax.text(x + 0.15, y + card_height - 0.08, card['title'], fontsize=20, 
                color=card['title_color'], fontweight='bold', va='top')
        
        # 4. Variables (Middle)
        # Much wider text wrap to stretch horizontally and use up horizontal space
        wrapped_vars = "\n".join(textwrap.wrap(card['vars'], width=65))
        ax.text(x + 0.05, y + card_height - 0.35, wrapped_vars, fontsize=15, 
                color='#2D2D2D', va='top', ha='left', linespacing=1.5, fontweight='bold')
        
        # 5. Rationale (Bottom)
        wrapped_rat = "\n".join(textwrap.wrap(card['rationale'], width=68))
        ax.text(x + 0.05, y + card_height - 0.58, wrapped_rat, fontsize=15, 
                color='#444444', va='top', ha='left', style='italic', linespacing=1.5)

        output_path = os.path.join(output_dir, f'Strategic_Weight_Card_{i+1}.png')
        
        plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
        plt.close(fig)
        print(f"Card saved to {output_path}")

if __name__ == "__main__":
    create_cards()
