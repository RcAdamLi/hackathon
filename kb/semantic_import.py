#!/usr/bin/env python3
"""
将数据批量导入到Elasticsearch语义知识库
使用方法: python semantic_import.py [文件路径]
文件格式: CSV或JSON
"""

import sys
import json
import csv
import os
import requests
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Elasticsearch配置
ES_HOST = "http://localhost:9200"
INDEX_NAME = "my_knowledge_base_semantic"

# 向量嵌入模型
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 多语言模型，支持中文

# 样例数据文件路径
SAMPLE_JSON_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.json")
SAMPLE_CSV_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.csv")

def initialize_model():
    """初始化语义模型"""
    try:
        print(f"正在加载语义模型 '{MODEL_NAME}'...")
        model = SentenceTransformer(MODEL_NAME)
        print(f"模型加载完成")
        return model
    except Exception as e:
        print(f"加载模型失败: {e}")
        sys.exit(1)

def create_index_if_not_exists():
    """创建带有向量字段的Elasticsearch索引"""
    index_url = f"{ES_HOST}/{INDEX_NAME}"
    
    # 检查索引是否存在
    response = requests.head(index_url)
    if response.status_code == 200:
        print(f"索引 '{INDEX_NAME}' 已存在")
        return
    
    # 创建支持向量搜索的索引
    index_mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "standard"},
                "tags": {"type": "keyword"},
                "date": {"type": "date"},
                "source": {"type": "keyword"},
                "import_date": {"type": "date"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384  # MiniLM-L12模型的维度
                }
            }
        }
    }
    
    response = requests.put(index_url, json=index_mapping)
    if response.status_code == 200:
        print(f"成功创建索引 '{INDEX_NAME}'")
    else:
        print(f"创建索引失败: {response.text}")
        sys.exit(1)

def import_json_file(file_path, model):
    """从JSON文件导入数据，并添加向量嵌入"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            documents = data
        else:
            documents = [data]
            
        # 为每个文档添加向量嵌入
        for doc in documents:
            # 组合标题和内容以创建更丰富的嵌入
            text_for_embedding = f"{doc.get('title', '')} {doc.get('content', '')}"
            # 生成向量嵌入
            embedding = model.encode(text_for_embedding).tolist()
            doc['embedding'] = embedding
            
        return documents
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        sys.exit(1)

def import_csv_file(file_path, model):
    """从CSV文件导入数据，并添加向量嵌入"""
    documents = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 处理标签（如果是逗号分隔的字符串）
                if 'tags' in row and isinstance(row['tags'], str):
                    row['tags'] = [tag.strip() for tag in row['tags'].split(',')]
                    
                # 组合标题和内容以创建更丰富的嵌入
                text_for_embedding = f"{row.get('title', '')} {row.get('content', '')}"
                # 生成向量嵌入
                embedding = model.encode(text_for_embedding).tolist()
                row['embedding'] = embedding
                
                documents.append(row)
        return documents
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        sys.exit(1)

def bulk_import_to_elasticsearch(documents):
    """批量导入数据到Elasticsearch"""
    bulk_data = []
    
    for doc in documents:
        # 添加导入日期
        doc['import_date'] = datetime.now().isoformat()
        
        # 准备批量导入的格式
        bulk_data.append({"index": {"_index": INDEX_NAME}})
        bulk_data.append(doc)
    
    # 发送批量请求
    bulk_request_body = "\n".join(json.dumps(d) for d in bulk_data) + "\n"
    response = requests.post(f"{ES_HOST}/_bulk", headers={"Content-Type": "application/x-ndjson"}, data=bulk_request_body)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('errors', True):
            print("导入过程中出现错误:")
            for item in result['items']:
                if 'error' in item.get('index', {}):
                    print(f"错误: {item['index']['error']}")
        else:
            print(f"成功导入 {len(documents)} 条文档到语义知识库 '{INDEX_NAME}'")
    else:
        print(f"批量导入失败: {response.text}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print(f"使用方法: {sys.argv[0]} [文件路径]")
        print(f"可用的示例数据文件:")
        print(f"  - JSON示例: {SAMPLE_JSON_FILE}")
        print(f"  - CSV示例: {SAMPLE_CSV_FILE}")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    # 初始化模型
    model = initialize_model()
    
    # 确保索引存在
    create_index_if_not_exists()
    
    # 根据文件扩展名导入数据
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        print("处理JSON文件...")
        documents = import_json_file(file_path, model)
    elif ext.lower() == '.csv':
        print("处理CSV文件...")
        documents = import_csv_file(file_path, model)
    else:
        print(f"不支持的文件类型: {ext}. 请使用 .json 或 .csv 文件")
        sys.exit(1)
    
    print(f"从 {file_path} 中读取了 {len(documents)} 条文档，并添加了语义向量")
    bulk_import_to_elasticsearch(documents)
    
    print(f"\n您现在可以使用 semantic_search.py 进行语义搜索:")
    print(f"python semantic_search.py \"您的搜索查询\"")

if __name__ == "__main__":
    main() 