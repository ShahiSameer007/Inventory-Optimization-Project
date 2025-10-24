import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Create an Images directory to store the visuals
IMAGE_DIR = "Images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def generate_optimization_comparison_chart(optimized_profit, baseline_profit, optimized_cost, baseline_cost):
    """
    Generates a comparison bar chart between Optimized and Baseline performance using
    the dual Y-axis (twinx) structure, but with the X-axis placement and all colors corrected.
    """
    
    labels = ['Optimized (Greedy Knapsack)', 'Baseline (Cheapest First)']
    profits = [optimized_profit, baseline_profit]
    costs = [optimized_cost, baseline_cost]
    
    df_comp = pd.DataFrame({
        'Method': labels, 
        'Profit': profits, 
        'Cost': costs
    })

    fig, ax1 = plt.subplots(figsize=(12, 9))
    
    # Define Color Scheme
    PROFIT_COLOR = "#2AD21E" # Green (Bars)
    COST_COLOR = "#0A4268"   # Blue (Line)
    
    # --- Custom Color Requirements ---
    Y_AXIS_COLOR = "#4A041C" # Pink
    X_AXIS_COLOR = "#023E0E" # Purple

    # 1. Plot Profit on the left Y-axis (Primary)
    profit_bars = ax1.bar(df_comp['Method'], df_comp['Profit'], color=PROFIT_COLOR, alpha=0.8, width=0.5, label='Total Expected Profit')
    
    # Y-axis 1 styling
    ax1.set_ylabel('Total Expected Profit (Rs)', fontsize=15, color=PROFIT_COLOR)
    ax1.tick_params(axis='y', labelcolor=Y_AXIS_COLOR) # Pink Y1 ticks
    ax1.yaxis.label.set_color(PROFIT_COLOR) # Keep Profit label green for association
    
    # Add secondary axis (twinx)
    ax2 = ax1.twinx()
    
    # 2. Plot Cost on the right Y-axis (Secondary)
    cost_line, = ax2.plot(df_comp['Method'], df_comp['Cost'], color=COST_COLOR, marker='o', linestyle='--', linewidth=3, markersize=8, label='Total Cost Committed')
    
    # Y-axis 2 styling
    ax2.set_ylabel('Total Cost Committed (Rs)', fontsize=15, color=COST_COLOR)
    ax2.tick_params(axis='y', labelcolor=Y_AXIS_COLOR) # Pink Y2 ticks
    ax2.yaxis.label.set_color(COST_COLOR) # Keep Cost label blue for association

    # --- X-Axis Fix and Color Application ---
    # CRITICAL FIX: Explicitly set the X-axis ticks and labels to the bottom on the primary axis
    ax1.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, colors=X_AXIS_COLOR)
    # Ensure the secondary axis does not interfere
    ax2.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=False)
    ax1.set_xlabel('Resource Allocation Strategy', fontsize=15, color=X_AXIS_COLOR)
    
    # Annotate Profit bars
    for bar in profit_bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + yval * 0.02, f'P: Rs {yval:,.0f}', 
                 ha='center', va='bottom', fontsize=11, weight='bold', color=PROFIT_COLOR)

    # Annotate Cost points (using ax2 coordinates)
    for i, txt in enumerate(df_comp['Cost']):
        ax2.annotate(f'C: Rs {txt:,.0f}', (df_comp['Method'][i], df_comp['Cost'][i]), 
                     textcoords="offset points", xytext=(0, -25), ha='center', fontsize=11, color=COST_COLOR, weight='bold')

    # Final Touches
    ax1.set_title('Optimization Value Proof: Profit vs. Cost by Strategy', fontsize=17)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # Move Legend to Top Right (as requested)
    handles = [profit_bars[0], cost_line]
    labels = ['Total Expected Profit', 'Total Cost Committed']
    ax1.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.0, 1.15), ncol=2, frameon=True, edgecolor='black')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'optimization_comparison_chart.png'))
    plt.close()

def generate_budget_allocation_chart(selected_orders, rejected_items, budget_limit, total_cost_spent):
    """
    Generates a Diverging Bar Chart showing SELECTED orders (green, positive) 
    and REJECTED orders (red, negative) against the budget axis, using business-friendly labels.
    """
    
    all_items = sorted(selected_orders + rejected_items, 
                       key=lambda item: item.calculate_priority_score(), 
                       reverse=True)

    # 1. Prepare Data for Diverging Chart
    df = pd.DataFrame([item.get_dict() for item in all_items])
    df['status'] = ['Selected' if item in selected_orders else 'Rejected' for item in all_items]
    
    df['budget_impact'] = df.apply(
        lambda row: row['order_cost'] if row['status'] == 'Selected' else -row['order_cost'], 
        axis=1
    )
    df.sort_values(by='priority_score', ascending=False, inplace=True)
    
    # 2. Setup the Plot
    fig, ax = plt.subplots(figsize=(14, 9))

    # Define colors
    colors = df['status'].map({'Selected': '#2ECC71', 'Rejected': '#E74C3C'})
    
    # Plot the diverging bars
    ax.bar(df['name'], df['budget_impact'], color=colors, edgecolor='black', linewidth=1.5)
    
    # 3. Add Key Annotations and Lines
    
    # Draw a line for the total budget (positive side)
    ax.axhline(budget_limit, color='#3498DB', linestyle='--', linewidth=3, 
               label=f'Total Order Budget: Rs {budget_limit:,.0f}')
    
    # Draw a line for the cost spent (positive side)
    if total_cost_spent > 0:
        ax.axhline(total_cost_spent, color='#1ABC9C', linestyle='-', linewidth=3, alpha=0.7,
                   label=f'Total Cost Committed: Rs {total_cost_spent:,.0f}')
        
    ax.axhline(0, color='black', linewidth=1)

    # Annotate bars with their absolute order cost
    for i, row in df.iterrows():
        cost_display = f'Rs {row["order_cost"]:,.0f}'
        y_pos = row['budget_impact'] * 0.5 
        ax.text(row['name'], y_pos, cost_display, ha='center', va='center', fontsize=10, 
                color='white' if row['status'] == 'Selected' else 'black', weight='bold')

    # 4. Final Touches
    ax.set_title('Inventory Reorder Decisions vs. Weekly Budget', fontsize=16)
    ax.set_ylabel('Order Cost (Rs)', fontsize=14)
    ax.set_xlabel('Product (Ordered by Profitability)', fontsize=14)
    ax.set_xticklabels(df['name'], rotation=45, ha="right")
    
    y_max = max(abs(df['budget_impact'].max()), abs(df['budget_impact'].min()), budget_limit) * 1.1
    y_min = -y_max * 0.7 
    
    ax.set_ylim(y_min, y_max)
    
    yticks = ax.get_yticks()
    ax.set_yticklabels([f'Rs {abs(y):,.0f}' for y in yticks])

    # Custom Legend
    final_legend_handles = [
        plt.Rectangle((0, 0), 1, 1, fc='#2ECC71', edgecolor='black', label='Selected for Order (Approved)'),
        plt.Rectangle((0, 0), 1, 1, fc='#E74C3C', edgecolor='black', label='Order Rejected (Budget Constraint)'),
        plt.Line2D([0], [0], color='#3498DB', linestyle='--', label=f'Total Order Budget: Rs {budget_limit:,.0f}'),
    ]
    ax.legend(handles=final_legend_handles, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'budget_allocation_diverging_chart.png'))
    plt.close()

def generate_priority_chart(df_all):
    """
    Generates a simple, clean bar chart for Reorder Priority using business-friendly labels.
    """
    df = df_all.copy()
    df.sort_values(by='priority_score', ascending=False, inplace=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(df['name'], df['priority_score'], 
                  color='#3498DB', 
                  edgecolor='black', linewidth=1)
    
    ax.set_yscale('log') 

    # Use Dark Gray for annotations
    ANNOTATION_COLOR = '#34495E' 
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height * 1.05),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, weight='bold', color=ANNOTATION_COLOR)

    # Final Touches
    ax.set_ylabel('Profit-to-Cost Ratio [Logarithmic Scale]', fontsize=14)
    ax.set_xlabel('Product Name (Ranked from Most Profitable to Least)', fontsize=14)
    ax.set_title('Product Profitability Ranking for Reordering', fontsize=16)
    ax.set_xticklabels(df['name'], rotation=45, ha="right")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'reorder_priority_ranking_simple.png'))
    plt.close()
