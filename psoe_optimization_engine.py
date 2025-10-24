import psycopg2
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# --- CRITICAL FIX: Ensure these imports match your Python file names ---
from psoe_visualization import generate_priority_chart, generate_budget_allocation_chart, generate_optimization_comparison_chart
from psoe_report import generate_final_report

# --- 1. CONFIGURATION ---
# !! CRITICAL: UPDATE THESE PARAMETERS (if you haven't already) !!
DB_PARAMS = {
    "host": "localhost",
    "database": "inventory_data",
    "user": "psoe_user",        # Use your PostgreSQL application user
    "password": "psoe_pass123"  # Use your actual password
}

# --- 2. OOP Implementation (Product Class) ---

class Product:
    """Represents a low-stock product, calculating reorder priority."""
    def __init__(self, product_id, name, current_stock, reorder_quantity, unit_cost, unit_price, low_stock_threshold):
        self.product_id = product_id
        self.name = name
        self.current_stock = int(current_stock)
        
        # CRITICAL FIX: Convert Decimal from DB to float/int
        self.reorder_quantity = round(float(reorder_quantity)) 
        self.unit_cost = float(unit_cost)
        self.unit_price = float(unit_price)
        self.low_stock_threshold = float(low_stock_threshold)
        
        # Derived values for DAA
        self.order_cost = self.reorder_quantity * self.unit_cost     
        self.order_value = self.reorder_quantity * (self.unit_price - self.unit_cost) 

    def calculate_priority_score(self):
        """Calculates the Value-to-Weight ratio (Profit/Cost) for the Greedy Knapsack algorithm."""
        if self.order_cost > 0:
            return self.order_value / self.order_cost
        return 0.0

    def get_dict(self):
        """Returns a dictionary representation for easy reporting/plotting."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'current_stock': self.current_stock,
            'reorder_quantity': self.reorder_quantity,
            'unit_cost': self.unit_cost,
            'unit_price': self.unit_price,
            'low_stock_threshold': self.low_stock_threshold,
            'order_cost': self.order_cost,
            'order_value': self.order_value,
            'priority_score': self.calculate_priority_score()
        }
    
    def __repr__(self):
        return f"Product({self.product_id}, Name:'{self.name}', Cost:Rs {self.order_cost:.2f}, Priority:{self.calculate_priority_score():.2f})"


# --- 3. Database Interaction Functions ---

def fetch_low_stock_products(db_params):
    """Connects to DB and fetches products that need reordering."""
    conn = None
    inventory_list = []
    print("\n--- Fetching Inventory Data ---")
    
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Fetch products where current stock is below the calculated threshold
        sql = """
        SELECT product_id, product_name, current_stock, reorder_quantity, 
               unit_cost, unit_price, low_stock_threshold
        FROM inventory_data
        WHERE current_stock < low_stock_threshold
        ORDER BY product_name;
        """
        cursor.execute(sql)
        
        for row in cursor.fetchall():
            inventory_list.append(Product(*row))
        print(f"✅ Success: Fetched {len(inventory_list)} low-stock products requiring optimization.")
            
    except psycopg2.OperationalError as e:
        print(f"❌ FATAL ERROR: Database Connection Failed. Details: {e}")
        sys.exit(1) 
    except Exception as e:
        print(f"❌ An error occurred during database fetch: {e}")
    finally:
        if conn:
            conn.close()
            
    return inventory_list


def log_order_decision(db_params, product, status, budget_cost=0, run_type="OPTIMIZED"):
    """Logs the reorder decision (SELECTED or REJECTED) to psoe_audit_log."""
    conn = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        log_data = (
            product.product_id, 
            float(product.reorder_quantity),
            float(budget_cost),
            status,
            run_type # Added run_type to distinguish DAA vs Baseline
        )
        
        # Updated SQL to include run_type column (assuming you added it to the audit table)
        sql = """
        INSERT INTO psoe_audit_log (product_id, order_quantity, budget_cost, status, run_type)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(sql, log_data)
        conn.commit()
        
    except psycopg2.Error as e:
        print(f"❌ Error logging decision for {product.name}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# --- 4. DAA Algorithm (0/1 Knapsack - Greedy Approach) ---

def run_daa_optimization(inventory_list, budget_limit):
    """
    Implements the Greedy 0/1 Knapsack algorithm for budgeted reordering.
    Sorts by priority_score (Profit/Cost Ratio).
    """
    print(f"\n--- Running DAA OPTIMIZATION (Greedy Knapsack) ---")
    
    # Step 1: Sort by Greedy Choice (Priority Score: Profit/Cost) -> OPTIMAL
    sorted_list = sorted(inventory_list, key=lambda item: item.calculate_priority_score(), reverse=True)

    current_budget = budget_limit
    total_cost_spent = 0
    total_expected_profit = 0
    
    # Run the allocation logic
    for item in sorted_list:
        cost = item.order_cost
        
        if cost <= current_budget:
            current_budget -= cost
            total_cost_spent += cost
            total_expected_profit += item.order_value
            # Log only the final OPTIMIZED results
            # log_order_decision(DB_PARAMS, item, "SELECTED", cost, "OPTIMIZED") 
        else:
            pass
            # log_order_decision(DB_PARAMS, item, "REJECTED", 0, "OPTIMIZED")
            
    # Return the key metrics for comparison
    print(f"  ✅ DAA Optimization Complete. Profit: Rs {total_expected_profit:,.2f}, Cost: Rs {total_cost_spent:,.2f}")
    return total_expected_profit, total_cost_spent


def run_baseline_optimization(inventory_list, budget_limit):
    """
    Implements a non-optimized baseline: simply select the cheapest items first.
    Sorts by order_cost (Cost).
    """
    print(f"\n--- Running BASELINE OPTIMIZATION (Cheapest First) ---")
    
    # Step 1: Sort by non-optimal choice (Cost, ascending) -> BASELINE
    sorted_list = sorted(inventory_list, key=lambda item: item.order_cost, reverse=False)

    current_budget = budget_limit
    total_cost_spent = 0
    total_expected_profit = 0
    
    # Run the allocation logic
    for item in sorted_list:
        cost = item.order_cost
        
        if cost <= current_budget:
            current_budget -= cost
            total_cost_spent += cost
            total_expected_profit += item.order_value
            # log_order_decision(DB_PARAMS, item, "SELECTED", cost, "BASELINE") 
        else:
            pass
            # log_order_decision(DB_PARAMS, item, "REJECTED", 0, "BASELINE")
            
    # Return the key metrics for comparison
    print(f"  ❌ Baseline Complete. Profit: Rs {total_expected_profit:,.2f}, Cost: Rs {total_cost_spent:,.2f}")
    return total_expected_profit, total_cost_spent


# --- 5. Main Execution Block ---

def get_budget_input():
    """Prompts user for the weekly budget using standard input."""
    while True:
        try:
            budget_str = input("\n[PSOE INPUT] Please enter the available WEEKLY REORDER BUDGET (e.g., 20000.00): Rs")
            budget = float(budget_str)
            if budget >= 0:
                return budget
            else:
                print("Budget must be a positive number. Try again.")
        except ValueError:
            print("Invalid input. Please enter a numerical value.")


if __name__ == '__main__':
    print("--- Procedural Stockflow Optimization Engine (PSOE) ---")
    
    # 1. Get user input for budget
    DAILY_BUDGET = get_budget_input() 
    
    # 2. Fetch data 
    inventory_items = fetch_low_stock_products(DB_PARAMS)
    
    if not inventory_items:
        print("No products currently below the low-stock threshold. Optimization skipped.")
        sys.exit(0)
    
    # Convert list of Product objects to DataFrame for easy manipulation
    df_all = pd.DataFrame([item.get_dict() for item in inventory_items])

    # 3. Run BOTH Optimization Models for Comparison
    # We must use a DEEP COPY of the inventory_items for the DAA to ensure the list is clean
    
    # A. Run OPTIMIZED (Greedy Knapsack)
    optimized_profit, optimized_cost = run_daa_optimization(inventory_items.copy(), DAILY_BUDGET)
    
    # B. Run BASELINE (Cheapest First)
    baseline_profit, baseline_cost = run_baseline_optimization(inventory_items.copy(), DAILY_BUDGET)
    
    # 4. Run the DAA Optimization a third time to get the individual selected/rejected lists for the Diverging Chart
    # This is slightly redundant but necessary to get the item lists (not just the totals)
    
    # NOTE: The original run_daa_optimization in previous versions returned the lists and totals.
    # To keep the optimization logic clear and separate, we'll revert to the list-returning structure
    # for the FINAL run that logs to DB and generates the diverging chart.
    
    # We will modify run_daa_optimization to return lists and totals.
    
    # --- Re-running final optimization to get detailed lists (Selected/Rejected) ---
    print("\n--- Running Final DAA Allocation for Detailed Reporting ---")
    
    # Reset inventory_items to original data for the final run
    final_inventory = fetch_low_stock_products(DB_PARAMS)
    final_inventory.sort(key=lambda item: item.calculate_priority_score(), reverse=True)
    
    selected = []
    rejected = []
    current_budget = DAILY_BUDGET
    total_cost_spent_final = 0
    total_expected_profit_final = 0
    
    for item in final_inventory:
        cost = item.order_cost
        if cost <= current_budget:
            selected.append(item)
            current_budget -= cost
            total_cost_spent_final += cost
            total_expected_profit_final += item.order_value
            log_order_decision(DB_PARAMS, item, "SELECTED", cost, "OPTIMIZED")
        else:
            rejected.append(item)
            log_order_decision(DB_PARAMS, item, "REJECTED", 0, "OPTIMIZED")
            
    print(f"✅ Final DAA Allocation Complete. {len(selected)} items selected.")
    
    
    print("\n--- Generating Final Visualizations ---")
    
    # 5. Generate Visualizations
    try:
        # Image 1: Optimized vs. Baseline Comparison (The new visual you requested)
        generate_optimization_comparison_chart(optimized_profit, baseline_profit, optimized_cost, baseline_cost)
        print("Image 1: 'optimization_comparison_chart.png' saved (Value Proof).")

        # Image 2: Budget Allocation Chart (Diverging Visual, now using final run data)
        generate_budget_allocation_chart(selected, rejected, DAILY_BUDGET, total_cost_spent_final)
        print("Image 2: 'budget_allocation_diverging_chart.png' saved (Decision Flow).")
        
        # Image 3: Priority Ranking Chart
        generate_priority_chart(df_all)
        print("Image 3: 'reorder_priority_ranking_simple.png' saved (Simple Ranking).")
        
    except Exception as e:
        print(f"❌ Visualization Error: Could not generate charts. Details: {e}")

    # 6. Generate and Save Final Report
    try:
        report_data = {
            'budget': DAILY_BUDGET,
            'total_cost_spent': total_cost_spent_final,
            'total_expected_profit': total_expected_profit_final,
            'selected_orders': [p.get_dict() for p in selected],
            'rejected_items': [p.get_dict() for p in rejected],
            'all_items_ranked': df_all[['name', 'priority_score', 'order_cost']].sort_values(by='priority_score', ascending=False),
            # Add comparison data to the report for narrative section
            'optimized_profit': optimized_profit,
            'baseline_profit': baseline_profit,
        }
        generate_final_report(report_data)
        print("✅ Report 'psoe_report.md' generated successfully.")

    except Exception as e:
        print(f"❌ Reporting Error: Could not generate final report. Details: {e}")

    print("\n--- PSOE Execution Complete ---")