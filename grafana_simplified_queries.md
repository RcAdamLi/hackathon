# Simplified Year Sales Comparison Queries

## Simple Annual Sales Total
```sql
SELECT 
  YEAR(month) as year,
  SUM(sales_count) as total_sales
FROM vehicle_sales
GROUP BY year
ORDER BY year
```

**Visualization Settings:**
- Type: Bar Chart or Stat Panel
- Set "year" as a text field, not time

## Sales by Model Per Year
```sql
SELECT 
  model,
  YEAR(month) as year,
  SUM(sales_count) as total_sales
FROM vehicle_sales
GROUP BY model, year
ORDER BY model, year
```

**Visualization Settings:**
- Type: Bar Chart
- X-axis: model
- Y-axis: total_sales
- Split series by field: year

## Pre-calculated Year Columns
```sql
SELECT 
  model,
  SUM(IF(YEAR(month) = 2024, sales_count, 0)) as 'Sales_2024',
  SUM(IF(YEAR(month) = 2025, sales_count, 0)) as 'Sales_2025'
FROM vehicle_sales
GROUP BY model
```

**Visualization Settings:**
- Type: Table or Bar Chart
- For Bar Chart: X-axis: model, Y-axis: multiple fields (Sales_2024, Sales_2025)

## Simple Year Totals
```sql
SELECT
  '2024' as year,
  SUM(IF(YEAR(month) = 2024, sales_count, 0)) as sales
FROM vehicle_sales

UNION ALL

SELECT
  '2025' as year,
  SUM(IF(YEAR(month) = 2025, sales_count, 0)) as sales
FROM vehicle_sales
```

**Visualization Settings:**
- Type: Bar Chart or Stat Panel
- X-axis: year
- Y-axis: sales 