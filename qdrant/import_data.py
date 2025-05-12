#!/usr/bin/env python3
import os
import json
import argparse
from tqdm import tqdm
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import uuid
import csv
import pandas as pd

def load_data_from_csv(csv_path):
    """从CSV文件加载数据"""
    print(f"正在从 {csv_path} 加载数据...")
    
    try:
        df = pd.read_csv(csv_path)
        documents = []
        
        # 检查必要的列是否存在
        if 'text' not in df.columns:
            print("错误: CSV文件必须包含'text'列")
            return []
        
        for _, row in df.iterrows():
            doc = {
                "text": row['text'],
                "metadata": {}
            }
            
            # 将其他列作为元数据
            for col in df.columns:
                if col != 'text':
                    doc["metadata"][col] = row[col]
            
            documents.append(doc)
        
        print(f"成功加载了 {len(documents)} 条数据")
        return documents
    except Exception as e:
        print(f"加载CSV数据时出错: {str(e)}")
        return []

def load_data_from_jsonl(jsonl_path):
    """从JSONL文件加载数据"""
    print(f"正在从 {jsonl_path} 加载数据...")
    
    documents = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if isinstance(item, dict) and "text" in item:
                        doc = {
                            "text": item["text"],
                            "metadata": {}
                        }
                        # 将除text外的所有字段作为元数据
                        for key, value in item.items():
                            if key != "text":
                                doc["metadata"][key] = value
                        documents.append(doc)
        
        print(f"成功加载了 {len(documents)} 条数据")
        return documents
    except Exception as e:
        print(f"加载JSONL数据时出错: {str(e)}")
        return []

def load_data_from_text(text_path):
    """从纯文本文件加载数据，每行作为一条记录"""
    print(f"正在从 {text_path} 加载数据...")
    
    documents = []
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if line.strip():
                    doc = {
                        "text": line.strip(),
                        "metadata": {
                            "line_number": i + 1,
                            "source_file": os.path.basename(text_path)
                        }
                    }
                    documents.append(doc)
        
        print(f"成功加载了 {len(documents)} 条数据")
        return documents
    except Exception as e:
        print(f"加载文本数据时出错: {str(e)}")
        return []

def create_sample_data(num_samples=10):
    """创建示例数据"""
    print(f"正在创建 {num_samples} 条示例数据...")
    
    sample_texts = [
        "人工智能是计算机科学的一个分支，它致力于开发能够执行通常需要人类智能的任务的系统。",
        "机器学习是人工智能的一个子领域，它使系统能够自动地从经验中学习和改进，而无需明确编程。",
        "深度学习是机器学习的一种技术，它使用多层神经网络来模仿人脑的学习过程。",
        "自然语言处理(NLP)是AI的一个领域，专注于使计算机能够理解、解释和生成人类语言。",
        "计算机视觉是AI的一个领域，专注于使计算机能够从图像和视频中获取信息并理解视觉世界。",
        "向量数据库如Qdrant专门为高效存储和检索向量嵌入而设计，支持相似性搜索和语义搜索。",
        "语义搜索使用文本的含义而非关键词匹配来查找相关信息，提供更好的搜索体验。",
        "嵌入是将文本、图像或其他数据转换为数字向量的过程，这些向量捕获了数据的语义信息。",
        "大语言模型(LLM)如GPT-4和Claude是AI系统，能够生成类似人类的文本，翻译语言，并回答问题。",
        "知识库是一个集中的存储库，包含应用程序需要的所有信息和知识，通常用于支持AI应用程序。"
    ]
    
    documents = []
    for i, text in enumerate(sample_texts[:num_samples]):
        doc = {
            "text": text,
            "metadata": {
                "id": i,
                "category": "AI概念",
                "is_sample": True
            }
        }
        documents.append(doc)
    
    print(f"成功创建了 {len(documents)} 条示例数据")
    return documents

def import_to_qdrant(documents, collection_name="knowledge_base", host="localhost", port=6333):
    """将文档导入到Qdrant"""
    if not documents:
        print("没有数据可导入")
        return
    
    print(f"正在连接到 Qdrant ({host}:{port})...")
    client = QdrantClient(host=host, port=port)
    
    # 加载嵌入模型
    print("正在加载嵌入模型...")
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    model = SentenceTransformer(model_name)
    vector_size = model.get_sentence_embedding_dimension()
    
    # 检查集合是否存在，不存在则创建
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if collection_name not in collection_names:
        print(f"正在创建集合 {collection_name}...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "size": vector_size,
                "distance": "Cosine"
            }
        )
    
    # 准备批量导入的数据
    print("正在生成嵌入向量...")
    points = []
    
    for doc in tqdm(documents):
        text = doc["text"]
        embedding = model.encode(text).tolist()
        point_id = str(uuid.uuid4())
        
        payload = doc.get("metadata", {})
        payload["text"] = text
        
        points.append({
            "id": point_id,
            "vector": embedding,
            "payload": payload
        })
    
    # 批量导入数据
    print(f"正在导入 {len(points)} 个点到 Qdrant...")
    batch_size = 100
    for i in tqdm(range(0, len(points), batch_size)):
        batch = points[i:i+batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )
    
    print(f"成功导入了 {len(points)} 条数据到 {collection_name} 集合")

def main():
    parser = argparse.ArgumentParser(description="导入数据到Qdrant向量数据库")
    parser.add_argument("--file", type=str, help="要导入的数据文件路径 (CSV, JSONL, 或纯文本)")
    parser.add_argument("--file_type", type=str, choices=["csv", "jsonl", "txt", "sample"], 
                        help="文件类型 (csv, jsonl, txt) 或使用'sample'创建示例数据")
    parser.add_argument("--host", type=str, default="localhost", help="Qdrant服务器主机名")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant服务器端口")
    parser.add_argument("--collection", type=str, default="knowledge_base", help="Qdrant集合名称")
    parser.add_argument("--samples", type=int, default=10, help="使用sample选项时创建的示例数量")
    
    args = parser.parse_args()
    
    # 如果没有提供参数，使用交互模式
    if not args.file and not args.file_type:
        print("没有提供数据文件，使用示例数据...")
        args.file_type = "sample"
    
    # 加载数据
    documents = []
    if args.file_type == "csv" and args.file:
        documents = load_data_from_csv(args.file)
    elif args.file_type == "jsonl" and args.file:
        documents = load_data_from_jsonl(args.file)
    elif args.file_type == "txt" and args.file:
        documents = load_data_from_text(args.file)
    elif args.file_type == "sample":
        documents = create_sample_data(args.samples)
    else:
        print("请提供有效的文件路径和类型")
        return
    
    # 导入到Qdrant
    import_to_qdrant(documents, args.collection, args.host, args.port)

if __name__ == "__main__":
    main() 