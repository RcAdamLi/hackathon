#!/usr/bin/env python3
"""
基于ChromaDB向量数据库的知识库系统 - 轻量级实现
使用方法: 
  - 导入数据: python chroma_kb.py import kb/sample_kb_data.json
  - 搜索知识库: python chroma_kb.py search "您的查询"
"""

import sys
import os
import json
import csv
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# 配置
COLLECTION_NAME = "knowledge_base"
DB_PATH = "./chroma_db"

# 样例数据文件路径
SAMPLE_JSON_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.json")
SAMPLE_CSV_FILE = os.path.join(os.path.dirname(__file__), "sample_kb_data.csv")

def initialize_client():
    """初始化ChromaDB客户端"""
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)
    return client

def initialize_embedding_function():
    """初始化嵌入函数"""
    try:
        print(f"正在加载语义模型...")
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        print(f"模型加载完成")
        return sentence_transformer_ef
    except Exception as e:
        print(f"加载模型失败: {e}")
        sys.exit(1)

def get_or_create_collection(client, embedding_function):
    """获取或创建集合"""
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        return collection
    except Exception as e:
        print(f"创建集合失败: {e}")
        sys.exit(1)

def import_json_file(file_path, collection):
    """从JSON文件导入数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            documents = data
        else:
            documents = [data]
            
        print(f"从 {file_path} 中读取了 {len(documents)} 条文档")
        
        # 准备导入数据
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            # 生成唯一ID
            doc_id = f"doc_{i}_{int(datetime.now().timestamp())}"
            ids.append(doc_id)
            
            # 组合标题和内容
            if 'title' in doc and 'content' in doc:
                text = f"{doc['title']}\n\n{doc['content']}"
            else:
                text = str(doc.get('content', ''))
            texts.append(text)
            
            # 转换标签为字符串以兼容ChromaDB
            if 'tags' in doc and isinstance(doc['tags'], list):
                doc['tags_str'] = ", ".join(doc['tags'])
            
            # 添加导入日期
            doc['import_date'] = datetime.now().isoformat()
            
            # 准备元数据 (只保留基本标量类型)
            metadata = {
                'title': doc.get('title', ''),
                'tags_str': doc.get('tags_str', ''),
                'date': doc.get('date', ''),
                'source': doc.get('source', ''),
                'import_date': doc['import_date']
            }
            metadatas.append(metadata)
        
        # 批量添加到ChromaDB
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"成功导入 {len(documents)} 条文档到 '{COLLECTION_NAME}' 集合")
        return len(documents)
    
    except Exception as e:
        print(f"读取或导入JSON文件失败: {e}")
        sys.exit(1)

def import_csv_file(file_path, collection):
    """从CSV文件导入数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
        
        print(f"从 {file_path} 中读取了 {len(documents)} 条文档")
        
        # 准备导入数据
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            # 生成唯一ID
            doc_id = f"doc_{i}_{int(datetime.now().timestamp())}"
            ids.append(doc_id)
            
            # 组合标题和内容
            if 'title' in doc and 'content' in doc:
                text = f"{doc['title']}\n\n{doc['content']}"
            else:
                text = str(doc.get('content', ''))
            texts.append(text)
            
            # 处理标签
            if 'tags' in doc and isinstance(doc['tags'], str):
                doc['tags_str'] = doc['tags']  # 保持原始标签字符串
            
            # 添加导入日期
            doc['import_date'] = datetime.now().isoformat()
            
            # 准备元数据 (只保留基本标量类型)
            metadata = {
                'title': doc.get('title', ''),
                'tags_str': doc.get('tags_str', doc.get('tags', '')),
                'date': doc.get('date', ''),
                'source': doc.get('source', ''),
                'import_date': doc['import_date']
            }
            metadatas.append(metadata)
        
        # 批量添加到ChromaDB
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"成功导入 {len(documents)} 条文档到 '{COLLECTION_NAME}' 集合")
        return len(documents)
    
    except Exception as e:
        print(f"读取或导入CSV文件失败: {e}")
        sys.exit(1)

def search_knowledge_base(query, collection, limit=10):
    """执行语义搜索"""
    # 执行搜索
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

def format_results(results):
    """格式化搜索结果以便显示"""
    if not results or len(results["documents"][0]) == 0:
        return "未找到匹配的结果。"
    
    formatted = []
    
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
        title = metadata.get('title', 'Untitled')
        tags_str = metadata.get('tags_str', '')
        date = metadata.get('date', '')
        source = metadata.get('source', '')
        
        # 计算余弦相似度（距离转换为相似度）
        similarity = (1 - distance) * 100  # 转换为百分比
        
        # 提取内容（移除标题）
        content = doc
        if title in content:
            content = content.replace(title, "", 1).strip()
        
        # 截取内容预览
        content_preview = content
        if len(content) > 200:
            content_preview = content[:200] + "..."
        
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
    embedding_function = initialize_embedding_function()
    collection = get_or_create_collection(client, embedding_function)
    
    # 根据文件扩展名导入数据
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        import_json_file(file_path, collection)
    elif ext.lower() == '.csv':
        import_csv_file(file_path, collection)
    else:
        print(f"不支持的文件类型: {ext}. 请使用 .json 或 .csv 文件")
        sys.exit(1)

def search(query):
    """搜索知识库"""
    try:
        client = initialize_client()
        embedding_function = initialize_embedding_function()
        
        # 检查集合是否存在
        try:
            collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=embedding_function
            )
        except Exception:
            print(f"错误: 集合 '{COLLECTION_NAME}' 不存在")
            print(f"请先导入数据: python chroma_kb.py import {SAMPLE_JSON_FILE}")
            sys.exit(1)
        
        print(f"\n正在搜索: \"{query}\"...")
        results = search_knowledge_base(query, collection)
        
        print(format_results(results))
        print(f"\n找到 {len(results['documents'][0])} 条匹配的结果。")
    
    except Exception as e:
        print(f"搜索过程中出错: {e}")
        sys.exit(1)

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