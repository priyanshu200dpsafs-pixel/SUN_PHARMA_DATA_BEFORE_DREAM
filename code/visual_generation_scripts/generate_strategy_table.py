import matplotlib.pyplot as plt
import os

def create_table():
    # Define Data
    columns = ["Cluster", "Digital Focus", "Channel Strategy", "ROI Objective"]
    cell_text = [
        ["Tier 1", "Loyalty", "Closed-loop Portals", "22% Renewal Lift"],
        ["Tier 2", "Pre-Launch", "Geofenced Webinars", "-45% CAC"],
        ["Tier 3", "Awareness", "Programmatic SMS", "0% Physical OPEX"]
    ]
    
    # Initialize figure
    fig, ax = plt.subplots(figsize=(10.0, 2.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.axis('off')
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Generate Table
    table = ax.table(cellText=cell_text, colLabels=columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.auto_set_column_width(col=list(range(len(columns))))
    table.scale(1.2, 2.5) # scale(width, height)
    
    # Apply Styling
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#D3D3D3')
        cell.set_linewidth(0.5)
        
        if row == 0:
            # Header Row - Dark Cyan
            cell.set_facecolor('#008B8B')
            cell.set_text_props(color='white', weight='bold')
        else:
            # Data Rows - Alternate White and Green/Azure
            if row % 2 == 1:
                cell.set_facecolor('#E0F2F1')
            else:
                cell.set_facecolor('white')
            
            cell.set_text_props(color='#2D2D2D')

    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Strategy_Table.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_table()
