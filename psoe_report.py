import pandas as pd
from datetime import datetime
import os

REPORT_FILE_PATH = "psoe_report.md"

def generate_final_report(data):
    """
    Generates a detailed Markdown report summarizing the optimization run.
    
    data structure expected:
    {
        'budget': float, 
        'total_cost_spent': float, 
        'total_expected_profit': float,
        'selected_orders': [dict], 
        'rejected_items': [dict], 
        'all_items_ranked': DataFrame (name, priority_score, order_cost)
    }
    """
    
    # Convert lists of dicts to DataFrames for easier table generation
    df_selected = pd.DataFrame(data['selected_orders'])
    df_rejected = pd.DataFrame(data['rejected_items'])
    df_ranked = data['all_items_ranked']
    
    # --- Report Content Assembly ---
    
    report_content = f"""# PSOE Optimization Report

**Generated On:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Initial Low-Stock Items:** {len(data['selected_orders']) + len(data['rejected_items'])}
**Weekly Budget Provided:** **Rs {data['budget']:.2f}**

---

## 1. Optimization Summary

The Procedural Stockflow Optimization Engine (PSOE) utilized the Greedy Knapsack Algorithm to maximize expected profit within the allocated weekly budget.

|               Metric                   |        Value   |
| :---                                   | :---           |
| **Total Cost Spent**                   | **Rs {data['total_cost_spent']:.2f}**|
| **Remaining Budget**                   | **Rs {data['budget'] - data['total_cost_spent']:.2f}** |
| **Total Expected Profit**              | **Rs {data['total_expected_profit']:.2f}**|
| **Items Selected for Reorder**         | {len(data['selected_orders'])}              |
| **Items Rejected (Budget Constraint)** | {len(data['rejected_items'])}              |

---

## 2. Decision Analysis: Reorder Priority Ranking

The Greedy algorithm prioritizes orders based on the **Profit-to-Cost Ratio (Value/Weight)**. A higher score indicates a better return on investment for the limited budget.

### Ranking for Focus
The following table shows the explicit ranking of all low-stock items. The optimization process followed this exact order until the budget was exhausted.

{df_ranked.rename(columns={'name': 'Product Name', 'priority_score': 'Priority Score (Profit/Cost)', 'order_cost': 'Total Order Cost'}).to_markdown(index=False)}

---

## 3. Selected Orders (Budget Approved)

These products were approved for reordering as their individual cost was within the remaining budget, prioritized by their high Profit/Cost ratio.

"""

    if not df_selected.empty:
        df_selected_summary = df_selected[['name', 'reorder_quantity', 'order_cost', 'order_value']].rename(columns={
            'name': 'Product',
            'reorder_quantity': 'Order Qty (Avg Monthly Sales)',
            'order_cost': 'Budget Cost',
            'order_value': 'Expected Profit'
        })
        report_content += df_selected_summary.to_markdown(index=False)
    else:
        report_content += "*No orders were selected within the budget.*"


    report_content += """
---

## 4. Rejected Items (Budget Constraint)

These products required reordering but their cost exceeded the remaining budget at the time the engine processed them. They should be prioritized for the next budget cycle.
"""

    if not df_rejected.empty:
        df_rejected_summary = df_rejected[['name', 'order_cost', 'order_value']].rename(columns={
            'name': 'Product',
            'order_cost': 'Required Cost',
            'order_value': 'Expected Profit'
        })
        report_content += df_rejected_summary.to_markdown(index=False)
    else:
        report_content += "*All necessary orders were selected.*"

    # --- Save the Report ---
    with open(REPORT_FILE_PATH, 'w') as f:
        f.write(report_content)
