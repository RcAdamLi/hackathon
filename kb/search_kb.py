#!/usr/bin/env python3
"""
从Elasticsearch知识库搜索内容
使用方法: python search_kb.py [搜索关键词]
"""

import sys
import json
import requests
import os
from datetime import datetime

# Elasticsearch配置
ES_HOST = "http://localhost:9200"
INDEX_NAME = "my_knowledge_base"

def search_knowledge_base(query, size=10):
    """
    在知识库中搜索内容
    
    参数:
    query (str): 搜索关键词
    size (int): 返回的最大结果数量
    
    返回:
    list: 匹配的文档列表
    """
    search_url = f"{ES_HOST}/{INDEX_NAME}/_search"
    
    # 构建搜索请求
    search_body = {
        "size": size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "content", "tags"],  # 标题字段权重更高
                "type": "best_fields",
                "fuzziness": "AUTO"  # 启用模糊搜索
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "content": {}
            },
            "pre_tags": ["<highlighted>"],
            "post_tags": ["</highlighted>"]
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
        highlights = hit.get('highlight', {})
        
        title = source.get('title', 'Untitled')
        content = source.get('content', '')
        tags = source.get('tags', [])
        date = source.get('date', '')
        source_name = source.get('source', '')
        
        # 如果有高亮内容，则使用高亮内容
        if 'title' in highlights and highlights['title']:
            title = highlights['title'][0].replace('<highlighted>', '\033[1;33m').replace('</highlighted>', '\033[0m')
        
        content_preview = content
        if 'content' in highlights and highlights['content']:
            content_preview = "..." + highlights['content'][0].replace('<highlighted>', '\033[1;33m').replace('</highlighted>', '\033[0m') + "..."
        elif len(content) > 200:
            content_preview = content[:200] + "..."
        
        # 格式化标签
        if isinstance(tags, list):
            tags_str = ", ".join(tags)
        else:
            tags_str = str(tags)
        
        formatted.append(
            f"\033[1;36m#{i} {title}\033[0m (评分: {score:.2f})\n"
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
        print(f"使用方法: {sys.argv[0]} [搜索关键词]")
        print("示例: python search_kb.py Docker")
        print("示例: python search_kb.py \"机器学习 算法\"")
        sys.exit(1)
    
    # 拼接所有参数作为搜索查询
    query = " ".join(sys.argv[1:])
    print(f"\n正在搜索: \"{query}\"...")
    
    # 检查索引是否存在
    try:
        response = requests.head(f"{ES_HOST}/{INDEX_NAME}")
        if response.status_code != 200:
            print(f"错误: 知识库索引 '{INDEX_NAME}' 不存在。")
            import_script = os.path.join(os.path.dirname(__file__), "import_data_to_kb.py")
            sample_data = os.path.join(os.path.dirname(__file__), "sample_kb_data.json")
            print(f"请先导入数据: python {import_script} {sample_data}")
            sys.exit(1)
    except Exception as e:
        print(f"错误: 无法连接到Elasticsearch: {e}")
        print(f"请确保Elasticsearch正在运行，并且可以通过 {ES_HOST} 访问")
        sys.exit(1)
    
    # 执行搜索
    results = search_knowledge_base(query)
    
    # 显示结果
    print(format_results(results))
    print(f"\n找到 {len(results)} 条匹配的结果。")

if __name__ == "__main__":
    main() 