# Improved Grafana Queries for Year-over-Year Comparison

## Annual Sales Comparison (Bar Gauge)
```sql
SELECT 
  CONCAT('Year ', YEAR(month)) as year_label,
  SUM(sales_count) as total_sales
FROM vehicle_sales
GROUP BY YEAR(month)
ORDER BY YEAR(month)
```

**Visualization Settings:**
- Type: Bar Gauge
- Field: total_sales
- Text Mode: Value and name
- Orientation: Horizontal
- Display Mode: Gradient

## Annual Sales Comparison (Bar Chart Alternative)
```sql
SELECT 
  CASE 
    WHEN YEAR(month) = 2024 THEN '2024'
    WHEN YEAR(month) = 2025 THEN '2025'
    ELSE CONCAT('Year ', YEAR(month))
  END as year_label,
  SUM(sales_count) as total_sales
FROM vehicle_sales
GROUP BY YEAR(month)
ORDER BY YEAR(month)
```

**Visualization Settings:**
- Type: Bar Chart
- X Field: year_label
- Y Field: total_sales
- Series (Y-axis): total_sales

## Annual Sales by Model (Grouped Bar Chart)
```sql
SELECT 
  model,
  SUM(CASE WHEN YEAR(month) = 2024 THEN sales_count ELSE 0 END) as 'Year 2024',
  SUM(CASE WHEN YEAR(month) = 2025 THEN sales_count ELSE 0 END) as 'Year 2025'
FROM vehicle_sales
GROUP BY model
```

**Visualization Settings:**
- Type: Bar Chart
- X Field: model
- Y Field: Set as multiple fields (Year 2024, Year 2025)
- Orientation: Auto

## Monthly Comparison (Bar Chart)
```sql
SELECT 
  MONTH(month) as month_number,
  MONTHNAME(month) as month_name,
  SUM(CASE WHEN YEAR(month) = 2024 THEN sales_count ELSE 0 END) as 'Year 2024',
  SUM(CASE WHEN YEAR(month) = 2025 THEN sales_count ELSE 0 END) as 'Year 2025'
FROM vehicle_sales
GROUP BY MONTH(month), MONTHNAME(month)
ORDER BY MONTH(month)
```

**Visualization Settings:**
- Type: Bar Chart
- X Field: month_name
- Y Field: Set as multiple fields (Year 2024, Year 2025)
- Orientation: Auto 