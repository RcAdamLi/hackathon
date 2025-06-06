-- 使用grafana数据库
USE grafana;

-- 创建车辆销售数据表
CREATE TABLE IF NOT EXISTS vehicle_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month DATE NOT NULL,
    model VARCHAR(50) NOT NULL,
    sales_count INT NOT NULL,
    revenue DECIMAL(15, 2) NOT NULL
);

-- 插入模拟数据 - 2024年1月至2025年5月
-- 2024年数据
INSERT INTO vehicle_sales (month, model, sales_count, revenue) VALUES
('2024-01-01', 'BYD Han', 3245, 81125000.00),
('2024-01-01', 'BYD Tang', 2876, 74776000.00),
('2024-01-01', 'BYD Seal', 4521, 99462000.00),
('2024-02-01', 'BYD Han', 3456, 86400000.00),
('2024-02-01', 'BYD Tang', 2987, 77662000.00),
('2024-02-01', 'BYD Seal', 4765, 104830000.00),
('2024-03-01', 'BYD Han', 3789, 94725000.00),
('2024-03-01', 'BYD Tang', 3102, 80652000.00),
('2024-03-01', 'BYD Seal', 5012, 110264000.00),
('2024-04-01', 'BYD Han', 4123, 103075000.00),
('2024-04-01', 'BYD Tang', 3354, 87204000.00),
('2024-04-01', 'BYD Seal', 5345, 117590000.00),
('2024-05-01', 'BYD Han', 4532, 113300000.00),
('2024-05-01', 'BYD Tang', 3687, 95862000.00),
('2024-05-01', 'BYD Seal', 5678, 124916000.00),
('2024-06-01', 'BYD Han', 4678, 116950000.00),
('2024-06-01', 'BYD Tang', 3845, 99970000.00),
('2024-06-01', 'BYD Seal', 5987, 131714000.00),
('2024-07-01', 'BYD Han', 4823, 120575000.00),
('2024-07-01', 'BYD Tang', 3967, 103142000.00),
('2024-07-01', 'BYD Seal', 6134, 134948000.00),
('2024-08-01', 'BYD Han', 4621, 115525000.00),
('2024-08-01', 'BYD Tang', 3789, 98514000.00),
('2024-08-01', 'BYD Seal', 5875, 129250000.00),
('2024-09-01', 'BYD Han', 4876, 121900000.00),
('2024-09-01', 'BYD Tang', 3945, 102570000.00),
('2024-09-01', 'BYD Seal', 6213, 136686000.00),
('2024-10-01', 'BYD Han', 5134, 128350000.00),
('2024-10-01', 'BYD Tang', 4134, 107484000.00),
('2024-10-01', 'BYD Seal', 6547, 144034000.00),
('2024-11-01', 'BYD Han', 5432, 135800000.00),
('2024-11-01', 'BYD Tang', 4356, 113256000.00),
('2024-11-01', 'BYD Seal', 6879, 151338000.00),
('2024-12-01', 'BYD Han', 5678, 141950000.00),
('2024-12-01', 'BYD Tang', 4532, 117832000.00),
('2024-12-01', 'BYD Seal', 7123, 156706000.00),

-- 2025年数据
('2025-01-01', 'BYD Han', 5432, 135800000.00),
('2025-01-01', 'BYD Tang', 4567, 118742000.00),
('2025-01-01', 'BYD Seal', 7245, 159390000.00),
('2025-02-01', 'BYD Han', 5678, 141950000.00),
('2025-02-01', 'BYD Tang', 4689, 121914000.00),
('2025-02-01', 'BYD Seal', 7456, 164032000.00),
('2025-03-01', 'BYD Han', 5987, 149675000.00),
('2025-03-01', 'BYD Tang', 4912, 127712000.00),
('2025-03-01', 'BYD Seal', 7689, 169158000.00),
('2025-04-01', 'BYD Han', 6234, 155850000.00),
('2025-04-01', 'BYD Tang', 5145, 133770000.00),
('2025-04-01', 'BYD Seal', 8012, 176264000.00),
('2025-05-01', 'BYD Han', 6543, 163575000.00),
('2025-05-01', 'BYD Tang', 5432, 141232000.00),
('2025-05-01', 'BYD Seal', 8345, 183590000.00); 