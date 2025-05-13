#!/usr/bin/env python3
from flask import Flask, Response
import mysql.connector
import time
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# 指标定义
sales_count = Gauge('vehicle_sales_count', 'Vehicle sales count', ['model', 'month', 'year'])
sales_revenue = Gauge('vehicle_sales_revenue', 'Vehicle sales revenue', ['model', 'month', 'year'])

# 上次抓取时间
last_scrape_time = 0
# 缓存时间(秒)
CACHE_SECONDS = 60

def fetch_data_from_mysql():
    """从MySQL获取数据并更新Prometheus指标"""
    try:
        # 连接MySQL - 在Docker网络中使用服务名称
        conn = mysql.connector.connect(
            host="mysql",  # Docker网络中的服务名称
            port=3306,     # 容器内端口
            user="grafana",
            password="grafana",
            database="grafana"
        )
        
        cursor = conn.cursor()
        
        # 重置指标(避免过时数据)
        sales_count._metrics.clear()
        sales_revenue._metrics.clear()
        
        # 查询销售数据
        cursor.execute("SELECT model, month, sales_count, revenue FROM vehicle_sales")
        
        for (model, month, count, revenue) in cursor:
            year = month.strftime("%Y")
            month_str = month.strftime("%Y-%m")
            # 更新指标
            sales_count.labels(model=model, month=month_str, year=year).set(count)
            sales_revenue.labels(model=model, month=month_str, year=year).set(revenue)
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error fetching data: {e}")
        return False

@app.route('/metrics')
def metrics():
    """暴露Prometheus指标端点"""
    global last_scrape_time
    
    # 如果上次抓取时间超过缓存时间，重新抓取数据
    current_time = time.time()
    if current_time - last_scrape_time > CACHE_SECONDS:
        success = fetch_data_from_mysql()
        if success:
            last_scrape_time = current_time
    
    # 生成Prometheus指标响应
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    # 初始加载数据
    fetch_data_from_mysql()
    # 启动服务器在9102端口(常用的自定义exporter端口范围)
    app.run(host='0.0.0.0', port=9102) 