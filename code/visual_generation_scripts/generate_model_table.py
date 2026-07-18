import matplotlib.pyplot as plt
import os

def create_model_table():
    fig, ax = plt.subplots(figsize=(8, 3.5)) # Slightly taller to fit the table cleanly
    ax.axis('tight')
    ax.axis('off')
    
    # Ensure transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Global Font Setting for Matplotlib to use modern sans-serif
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    col_labels = ['Model', 'Optimization', 'R-Squared', 'MAPE']
    cell_text = [
        ['XGBoost (Selected)', 'Optuna with CV', '0.924', '0.185'],
        ['LightGBM', 'GridSearch', '0.891', '0.210'],
        ['Random Forest', 'Standard CV', '0.845', '0.264']
    ]
    
    table = ax.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2.5) # Scale to fill figure
    
    for (row, col), cell in table.get_celld().items():
        # Orange border around every cell gives it a clean table grid with the Sun Pharma touch
        cell.set_edgecolor('#F37021') 
        cell.set_linewidth(1.5)
        
        if row == 0:
            # Header Row
            cell.set_facecolor('#0F2046')
            cell.set_text_props(color='white', weight='bold')
        elif row == 1:
            # Winning Row (Row 1 - XGBoost)
            cell.set_facecolor('#FFF3E0') # Very light orange/peach
            cell.set_text_props(color='#2D2D2D', weight='bold')
        elif row == 2:
            # Other Row
            cell.set_facecolor('#FFFFFF')
            cell.set_text_props(color='#2D2D2D')
        elif row == 3:
            # Other Row (Alternating light grey)
            cell.set_facecolor('#F8F9FA')
            cell.set_text_props(color='#2D2D2D')

    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Model_Comparison_Table.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Table saved to {output_path}")

if __name__ == "__main__":
    create_model_table()
