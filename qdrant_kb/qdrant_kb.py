#!/usr/bin/env python3
"""
基于Qdrant向量数据库的知识库系统
使用方法: 
  - 导入数据: python qdrant_kb.py import sample_kb_data.json
  - 搜索知识库: python qdrant_kb.py search "您的查询"
"""

import sys
import os
import json
import csv
from datetime import datetime
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# 配置
COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 384  # paraphrase-multilingual-MiniLM-L12-v2 模型的向量维度

# 样例数据文件路径
SAMPLE_JSON_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.json")
SAMPLE_CSV_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.csv")

def initialize_client():
    """初始化Qdrant客户端"""
    try:
        # 优先尝试连接到Docker容器
        client = QdrantClient(host="localhost", port=6333)
        # 测试连接
        client.get_collections()
        print("已连接到Qdrant服务器")
        return client
    except Exception as e:
        print(f"无法连接到Qdrant服务器: {e}")
        print("尝试使用本地存储...")
        # 使用本地存储
        client = QdrantClient(path="./qdrant_data")
        return client

def initialize_model():
    """初始化语义模型"""
    try:
        print(f"正在加载语义模型...")
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print(f"模型加载完成")
        return model
    except Exception as e:
        print(f"加载模型失败: {e}")
        sys.exit(1)

def create_collection_if_not_exists(client):
    """创建Qdrant集合，如果不存在"""
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if COLLECTION_NAME not in collection_names:
        print(f"创建集合 '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"集合 '{COLLECTION_NAME}' 创建成功")
    else:
        print(f"集合 '{COLLECTION_NAME}' 已存在")

def import_json_file(file_path, model, client):
    """从JSON文件导入数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            documents = data
        else:
            documents = [data]
            
        print(f"从 {file_path} 中读取了 {len(documents)} 条文档")
        
        # 准备批量导入的点
        points = []
        
        for i, doc in enumerate(documents):
            # 组合标题和内容以创建更丰富的嵌入
            text_for_embedding = f"{doc.get('title', '')} {doc.get('content', '')}"
            # 生成向量嵌入
            embedding = model.encode(text_for_embedding).tolist()
            
            # 添加导入日期
            doc['import_date'] = datetime.now().isoformat()
            
            # 创建点
            point = PointStruct(
                id=i,
                vector=embedding,
                payload=doc
            )
            points.append(point)
        
        # 批量上传到Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        print(f"成功导入 {len(points)} 条文档到 '{COLLECTION_NAME}' 集合")
        return len(points)
    
    except Exception as e:
        print(f"读取或导入JSON文件失败: {e}")
        sys.exit(1)

def import_csv_file(file_path, model, client):
    """从CSV文件导入数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
        
        print(f"从 {file_path} 中读取了 {len(documents)} 条文档")
        
        # 准备批量导入的点
        points = []
        
        for i, doc in enumerate(documents):
            # 处理标签（如果是逗号分隔的字符串）
            if 'tags' in doc and isinstance(doc['tags'], str):
                doc['tags'] = [tag.strip() for tag in doc['tags'].split(',')]
            
            # 组合标题和内容以创建更丰富的嵌入
            text_for_embedding = f"{doc.get('title', '')} {doc.get('content', '')}"
            
            # 生成向量嵌入
            embedding = model.encode(text_for_embedding).tolist()
            
            # 添加导入日期
            doc['import_date'] = datetime.now().isoformat()
            
            # 创建点
            point = PointStruct(
                id=i,
                vector=embedding,
                payload=doc
            )
            points.append(point)
        
        # 批量上传到Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        print(f"成功导入 {len(points)} 条文档到 '{COLLECTION_NAME}' 集合")
        return len(points)
    
    except Exception as e:
        print(f"读取或导入CSV文件失败: {e}")
        sys.exit(1)

def search_knowledge_base(query, model, client, limit=10):
    """执行语义搜索"""
    # 为查询生成向量嵌入
    query_vector = model.encode(query).tolist()
    
    # 执行搜索
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    return search_result

def format_results(results):
    """格式化搜索结果以便显示"""
    if not results:
        return "未找到匹配的结果。"
    
    formatted = []
    for i, result in enumerate(results, 1):
        score = result.score
        payload = result.payload
        
        title = payload.get('title', 'Untitled')
        content = payload.get('content', '')
        tags = payload.get('tags', [])
        date = payload.get('date', '')
        source = payload.get('source', '')
        
        # 截取内容预览
        content_preview = content
        if len(content) > 200:
            content_preview = content[:200] + "..."
        
        # 格式化标签
        if isinstance(tags, list):
            tags_str = ", ".join(tags)
        else:
            tags_str = str(tags)
        
        # 计算相似度（假设使用余弦相似度，范围0-1）
        similarity = score * 100  # 转换为百分比
        
        formatted.append(
            f"\033[1;36m#{i} {title}\033[0m (相似度: {similarity:.1f}%)\n"
            f"{content_preview}\n"
            f"\033[0;32m标签:\033[0m {tags_str}\n"
            f"\033[0;32m日期:\033[0m {date}  \033[0;32m来源:\033[0m {source}\n"
            f"{'='*80}"
        )
    
    return "\n".join(formatted)

def import_data(file_path):
    """导入数据到知识库"""
    client = initialize_client()
    model = initialize_model()
    create_collection_if_not_exists(client)
    
    # 根据文件扩展名导入数据
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        import_json_file(file_path, model, client)
    elif ext.lower() == '.csv':
        import_csv_file(file_path, model, client)
    else:
        print(f"不支持的文件类型: {ext}. 请使用 .json 或 .csv 文件")
        sys.exit(1)

def search(query):
    """搜索知识库"""
    client = initialize_client()
    model = initialize_model()
    
    # 检查集合是否存在
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if COLLECTION_NAME not in collection_names:
        print(f"错误: 集合 '{COLLECTION_NAME}' 不存在")
        print(f"请先导入数据: python qdrant_kb.py import {SAMPLE_JSON_FILE}")
        sys.exit(1)
    
    print(f"\n正在搜索: \"{query}\"...")
    results = search_knowledge_base(query, model, client)
    
    print(format_results(results))
    print(f"\n找到 {len(results)} 条匹配的结果。")

def print_usage():
    """打印使用帮助"""
    print("使用方法:")
    print(f"  导入数据: python {sys.argv[0]} import [文件路径]")
    print(f"  搜索知识库: python {sys.argv[0]} search \"查询内容\"")
    print("")
    print("示例:")
    print(f"  python {sys.argv[0]} import {SAMPLE_JSON_FILE}")
    print(f"  python {sys.argv[0]} search \"Docker的优势是什么\"")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "import":
        if len(sys.argv) != 3:
            print(f"使用方法: python {sys.argv[0]} import [文件路径]")
            print(f"示例: python {sys.argv[0]} import {SAMPLE_JSON_FILE}")
            sys.exit(1)
        
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        
        import_data(file_path)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print(f"使用方法: python {sys.argv[0]} search \"查询内容\"")
            print(f"示例: python {sys.argv[0]} search \"Docker的优势是什么\"")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        search(query)
    
    else:
        print(f"未知命令: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main() 