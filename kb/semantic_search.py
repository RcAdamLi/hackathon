#!/usr/bin/env python3
"""
基于语义的知识库搜索工具
使用方法: python semantic_search.py [搜索查询]
"""

import sys
import os
import json
import requests
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Elasticsearch配置
ES_HOST = "http://localhost:9200"
INDEX_NAME = "my_knowledge_base_semantic"

# 向量嵌入模型
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 多语言模型，支持中文

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

def index_documents_from_source():
    """从原始知识库索引获取文档并添加向量嵌入"""
    model = initialize_model()
    
    # 从原始索引获取所有文档
    search_url = f"{ES_HOST}/my_knowledge_base/_search"
    search_body = {
        "size": 1000,  # 获取最多1000个文档
        "query": {
            "match_all": {}
        }
    }
    
    try:
        response = requests.post(search_url, json=search_body)
        if response.status_code != 200:
            print(f"获取原始文档失败: {response.text}")
            return
        
        results = response.json()
        if 'hits' not in results or 'hits' not in results['hits']:
            print("原始索引中未找到文档")
            return
        
        documents = results['hits']['hits']
        print(f"从原始索引中获取了 {len(documents)} 个文档")
        
        # 为每个文档创建向量嵌入
        for doc in documents:
            source = doc['_source']
            # 组合标题和内容以创建更丰富的嵌入
            text_for_embedding = f"{source.get('title', '')} {source.get('content', '')}"
            # 生成向量嵌入
            embedding = model.encode(text_for_embedding).tolist()
            
            # 添加向量嵌入到文档
            source['embedding'] = embedding
            
            # 索引文档到新的语义索引
            doc_id = doc['_id']
            index_doc_url = f"{ES_HOST}/{INDEX_NAME}/_doc/{doc_id}"
            
            response = requests.put(index_doc_url, json=source)
            if response.status_code not in [200, 201]:
                print(f"索引文档失败: {response.text}")
            
        print(f"成功为 {len(documents)} 个文档添加了语义向量")
        
    except Exception as e:
        print(f"处理文档时出错: {e}")
        sys.exit(1)

def semantic_search(query, model, size=10):
    """执行语义搜索"""
    # 为查询生成向量嵌入
    query_embedding = model.encode(query).tolist()
    
    # 构建语义搜索请求
    search_url = f"{ES_HOST}/{INDEX_NAME}/_search"
    search_body = {
        "size": size,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        },
        "_source": ["title", "content", "tags", "date", "source"]
    }
    
    try:
        response = requests.post(search_url, json=search_body)
        
        if response.status_code != 200:
            print(f"搜索请求失败: {response.text}")
            return []
        
        results = response.json()
        
        if 'hits' not in results or 'hits' not in results['hits']:
            print("未找到结果")
            return []
        
        return results['hits']['hits']
    
    except Exception as e:
        print(f"搜索过程中出错: {e}")
        return []

def format_results(hits):
    """格式化搜索结果以便显示"""
    if not hits:
        return "未找到匹配的结果。"
    
    formatted = []
    for i, hit in enumerate(hits, 1):
        source = hit.get('_source', {})
        score = hit.get('_score', 0)
        
        title = source.get('title', 'Untitled')
        content = source.get('content', '')
        tags = source.get('tags', [])
        date = source.get('date', '')
        source_name = source.get('source', '')
        
        # 截取内容预览
        content_preview = content
        if len(content) > 200:
            content_preview = content[:200] + "..."
        
        # 格式化标签
        if isinstance(tags, list):
            tags_str = ", ".join(tags)
        else:
            tags_str = str(tags)
        
        # 计算相似度分数（余弦相似度的范围是-1到1，我们将其转换为0-100%的相似度）
        similarity = ((score - 1.0) * 100) if score > 1.0 else 0
        
        formatted.append(
            f"\033[1;36m#{i} {title}\033[0m (相似度: {similarity:.1f}%)\n"
            f"{content_preview}\n"
            f"\033[0;32m标签:\033[0m {tags_str}\n"
            f"\033[0;32m日期:\033[0m {date}  \033[0;32m来源:\033[0m {source_name}\n"
            f"{'='*80}"
        )
    
    return "\n".join(formatted)

def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 2:
        print(f"使用方法: {sys.argv[0]} [搜索查询]")
        print("示例: python semantic_search.py \"什么是向量数据库？\"")
        print("示例: python semantic_search.py \"如何使用Docker部署应用\"")
        sys.exit(1)
    
    # 检查语义索引是否存在
    try:
        response = requests.head(f"{ES_HOST}/{INDEX_NAME}")
        if response.status_code != 200:
            print(f"语义索引 '{INDEX_NAME}' 不存在，正在创建...")
            create_index_if_not_exists()
            print("正在为文档添加语义向量...")
            index_documents_from_source()
    except Exception as e:
        print(f"错误: 无法连接到Elasticsearch: {e}")
        print(f"请确保Elasticsearch正在运行，并且可以通过 {ES_HOST} 访问")
        sys.exit(1)
    
    # 初始化模型
    model = initialize_model()
    
    # 拼接所有参数作为搜索查询
    query = " ".join(sys.argv[1:])
    print(f"\n正在进行语义搜索: \"{query}\"...")
    
    # 执行语义搜索
    results = semantic_search(query, model)
    
    # 显示结果
    print(format_results(results))
    print(f"\n找到 {len(results)} 条语义相关的结果。")

if __name__ == "__main__":
    main() 