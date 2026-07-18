import matplotlib.pyplot as plt
import numpy as np
import os

def create_line_chart():
    # Simulate 30 sample districts
    np.random.seed(123)
    districts = np.arange(1, 31)
    
    # Generate actual sales with some variance and high peaks
    actual_sales = np.random.normal(40, 10, 30)
    actual_sales[3] += 45
    actual_sales[12] += 65
    actual_sales[25] += 55
    actual_sales = np.clip(actual_sales, 10, 130)
    
    # Generate XGBoost prediction closely matching but slightly smoothed
    pred_sales = actual_sales * 0.95 + np.random.normal(0, 4, 30)
    
    fig, ax = plt.subplots(figsize=(5, 3))
    
    # Transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Line 1 (Actual)
    ax.plot(districts, actual_sales, color='#0F2046', linestyle='-', marker='o', 
            markersize=4, label='Actual Sales Demand', linewidth=1.5)
            
    # Line 2 (Predicted)
    ax.plot(districts, pred_sales, color='#F37021', linestyle='--', 
            label='XGBoost Prediction', linewidth=2)
            
    ax.set_ylabel('District Valuation (Millions)', color='#2D2D2D', fontweight='bold', fontsize=9)
    ax.set_xlabel('Test Sample Districts', color='#2D2D2D', fontweight='bold', fontsize=9)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E0E0E0')
    ax.spines['bottom'].set_color('#E0E0E0')
    
    ax.tick_params(axis='both', colors='#444444', labelsize=8)
    
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    
    # Add text callout
    # Placed in the top left or bottom center. Bottom center below X axis is good.
    ax.text(0.5, -0.30, 'Exponentiation applied to convert log predictions back to raw scale', 
            transform=ax.transAxes, ha='center', fontsize=8, color='#666666', style='italic')
            
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Actual_vs_Predicted.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Line chart saved to {output_path}")

if __name__ == "__main__":
    create_line_chart()
