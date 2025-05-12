# Grafana Dashboard Queries for BYD Vehicle Sales Data

## 1. Monthly Sales Trend by Model (Time Series)
```sql
SELECT 
  month as time,
  model as metric,
  sales_count as value
FROM vehicle_sales
ORDER BY month, model
```
- Visualization: Time Series
- Panel Title: "Monthly Sales Trend by Model"

## 2. Total Sales by Model (Pie Chart)
```sql
SELECT 
  model,
  SUM(sales_count) as total_sales
FROM vehicle_sales
GROUP BY model
ORDER BY total_sales DESC
```
- Visualization: Pie Chart
- Panel Title: "Total Vehicle Sales by Model"

## 3. Year-over-Year Comparison (Bar Chart)
```sql
SELECT 
  model,
  YEAR(month) as year,
  SUM(sales_count) as annual_sales
FROM vehicle_sales
GROUP BY model, YEAR(month)
ORDER BY model, year
```
- Visualization: Bar Chart
- Panel Title: "Year-over-Year Sales Comparison"

## 4. Monthly Revenue Trend (Time Series)
```sql
SELECT 
  month as time,
  SUM(revenue) as monthly_revenue
FROM vehicle_sales
GROUP BY month
ORDER BY month
```
- Visualization: Time Series
- Panel Title: "Monthly Revenue Trend"

## 5. Average Unit Price by Model (Gauge)
```sql
SELECT
  model,
  ROUND(SUM(revenue)/SUM(sales_count), 2) as avg_unit_price
FROM vehicle_sales
GROUP BY model
```
- Visualization: Gauge
- Panel Title: "Average Unit Price by Model"

## 6. Sales Growth Month-over-Month (Table)
```sql
SELECT
  DATE_FORMAT(v1.month, '%Y-%m') as month,
  v1.model,
  v1.sales_count as current_month_sales,
  v2.sales_count as previous_month_sales,
  ROUND(((v1.sales_count - v2.sales_count) / v2.sales_count) * 100, 2) as growth_percentage
FROM vehicle_sales v1
JOIN vehicle_sales v2 
  ON v1.model = v2.model 
  AND PERIOD_DIFF(DATE_FORMAT(v1.month, '%Y%m'), DATE_FORMAT(v2.month, '%Y%m')) = 1
ORDER BY v1.month DESC, v1.model
```
- Visualization: Table
- Panel Title: "Sales Growth Month-over-Month"

## 7. Seasonal Analysis (Heatmap)
```sql
SELECT
  MONTH(month) as month_number,
  model,
  AVG(sales_count) as avg_sales
FROM vehicle_sales
GROUP BY MONTH(month), model
ORDER BY month_number, model
```
- Visualization: Heatmap
- Panel Title: "Seasonal Sales Patterns"

## 8. Cumulative Sales by Model (Time Series)
```sql
SELECT
  month as time,
  model,
  SUM(sales_count) OVER (PARTITION BY model ORDER BY month) as cumulative_sales
FROM vehicle_sales
ORDER BY month, model
```
- Visualization: Time Series
- Panel Title: "Cumulative Sales by Model"

## 9. Revenue vs Sales Count (Scatter Plot)
```sql
SELECT
  model,
  month as time,
  sales_count,
  revenue
FROM vehicle_sales
ORDER BY month
```
- Visualization: Scatter Plot
- Panel Title: "Revenue vs Sales Count Correlation"

## 10. Model Market Share Over Time (Stacked Bar Chart)
```sql
SELECT
  DATE_FORMAT(month, '%Y-%m') as month,
  model,
  ROUND((sales_count / SUM(sales_count) OVER (PARTITION BY DATE_FORMAT(month, '%Y-%m'))) * 100, 2) as market_share_percentage
FROM vehicle_sales
ORDER BY month, model
```
- Visualization: Stacked Bar Chart
- Panel Title: "Model Market Share Over Time" 

## 11. Total Sales Comparison by Year (Bar Chart)
```sql
SELECT 
  YEAR(month) as year,
  SUM(sales_count) as total_annual_sales
FROM vehicle_sales
GROUP BY YEAR(month)
ORDER BY year
```
- Visualization: Bar Chart 
- Panel Title: "2024 vs 2025 Total Sales Comparison"

## 12. Total Sales Comparison by Year and Model (Bar Chart)
```sql
SELECT 
  YEAR(month) as year,
  model,
  SUM(sales_count) as total_annual_sales
FROM vehicle_sales
GROUP BY YEAR(month), model
ORDER BY year, model
```
- Visualization: Bar Chart (Grouped)
- Panel Title: "2024 vs 2025 Sales by Model" 