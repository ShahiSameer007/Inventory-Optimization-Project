# PSOE Optimization Report

**Generated On:** 2025-10-25 12:22:01
**Total Initial Low-Stock Items:** 9
**Weekly Budget Provided:** **Rs 56000.00**

---

## 1. Optimization Summary

The Procedural Stockflow Optimization Engine (PSOE) utilized the Greedy Knapsack Algorithm to maximize expected profit within the allocated weekly budget.

|               Metric                   |        Value   |
| :---                                   | :---           |
| **Total Cost Spent**                   | **Rs 52156.60**|
| **Remaining Budget**                   | **Rs 3843.40** |
| **Total Expected Profit**              | **Rs 27911.90**|
| **Items Selected for Reorder**         | 6              |
| **Items Rejected (Budget Constraint)** | 3              |

---

## 2. Decision Analysis: Reorder Priority Ranking

The Greedy algorithm prioritizes orders based on the **Profit-to-Cost Ratio (Value/Weight)**. A higher score indicates a better return on investment for the limited budget.

### Ranking for Focus
The following table shows the explicit ranking of all low-stock items. The optimization process followed this exact order until the budget was exhausted.

| Product Name     |   Priority Score (Profit/Cost) |   Total Order Cost |
|:-----------------|-------------------------------:|-------------------:|
| Berry Juice      |                       0.666667 |            21829.5 |
| Mango Drink      |                       0.538462 |            10436.4 |
| Cola             |                       0.538462 |             7523.1 |
| Diet Soda        |                       0.428571 |             3340.4 |
| Cranberry Juice  |                       0.25     |             6743.2 |
| Diet Cola        |                       0.25     |             2284   |
| Cream Soda       |                       0.25     |             7505.6 |
| Orange Juice     |                       0.25     |             5909.6 |
| Strawberry Drink |                       0.25     |             6144   |

---

## 3. Selected Orders (Budget Approved)

These products were approved for reordering as their individual cost was within the remaining budget, prioritized by their high Profit/Cost ratio.

| Product         |   Order Qty (Avg Monthly Sales) |   Budget Cost |   Expected Profit |
|:----------------|--------------------------------:|--------------:|------------------:|
| Berry Juice     |                            8085 |       21829.5 |           14553   |
| Mango Drink     |                            5352 |       10436.4 |            5619.6 |
| Cola            |                            5787 |        7523.1 |            4050.9 |
| Diet Soda       |                            2386 |        3340.4 |            1431.6 |
| Cranberry Juice |                            8429 |        6743.2 |            1685.8 |
| Diet Cola       |                            2855 |        2284   |             571   |
---

## 4. Rejected Items (Budget Constraint)

These products required reordering but their cost exceeded the remaining budget at the time the engine processed them. They should be prioritized for the next budget cycle.
| Product          |   Required Cost |   Expected Profit |
|:-----------------|----------------:|------------------:|
| Cream Soda       |          7505.6 |            1876.4 |
| Orange Juice     |          5909.6 |            1477.4 |
| Strawberry Drink |          6144   |            1536   |