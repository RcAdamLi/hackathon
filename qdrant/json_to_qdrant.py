#!/usr/bin/env python3
import os
import json
import argparse
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import uuid
from tqdm import tqdm

def load_data_from_json(json_path, text_field=None):
    """从普通JSON文件加载数据"""
    print(f"正在从 {json_path} 加载数据...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        
        # 处理JSON数组
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # 如果指定了text_field且该字段存在
                    if text_field and text_field in item:
                        text_content = item[text_field]
                    # 如果没有指定text_field或字段不存在，则自动生成描述
                    else:
                        # 自动生成描述文本
                        text_content = generate_description(item)
                    
                    doc = {
                        "text": text_content,
                        "metadata": {}
                    }
                    # 将所有字段作为元数据
                    for key, value in item.items():
                        if key != text_field:  # 如果有text_field，就不再重复添加
                            doc["metadata"][key] = value
                    documents.append(doc)
        
        # 处理包含items/data数组的JSON对象
        elif isinstance(data, dict):
            # 尝试常见的数组字段名
            array_fields = ["items", "data", "documents", "entries", "results", "records"]
            found_array = False
            
            for field in array_fields:
                if field in data and isinstance(data[field], list):
                    found_array = True
                    for item in data[field]:
                        if isinstance(item, dict):
                            # 如果指定了text_field且该字段存在
                            if text_field and text_field in item:
                                text_content = item[text_field]
                            # 如果没有指定text_field或字段不存在，则自动生成描述
                            else:
                                text_content = generate_description(item)
                            
                            doc = {
                                "text": text_content,
                                "metadata": {}
                            }
                            # 将所有字段作为元数据
                            for key, value in item.items():
                                if key != text_field:  # 如果有text_field，就不再重复添加
                                    doc["metadata"][key] = value
                            documents.append(doc)
                    break
            
            # 如果没有找到数组，但整个对象有价值，则直接处理这个对象
            if not found_array:
                if text_field and text_field in data:
                    text_content = data[text_field]
                else:
                    text_content = generate_description(data)
                
                doc = {
                    "text": text_content,
                    "metadata": {}
                }
                for key, value in data.items():
                    if key != text_field:
                        doc["metadata"][key] = value
                documents.append(doc)
        
        print(f"成功加载了 {len(documents)} 条数据")
        return documents
    except Exception as e:
        print(f"加载JSON数据时出错: {str(e)}")
        return []

def generate_description(item):
    """为JSON对象自动生成描述文本"""
    # 尝试提取常见的标识字段
    name = item.get('name', '')
    brand = item.get('brand', '')
    model = item.get('model', '')
    title = item.get('title', '')
    
    # 尝试汽车数据特有的组合
    if brand and model:
        car_type = item.get('type', '')
        powertrain = item.get('powertrain', [])
        if isinstance(powertrain, list) and powertrain:
            powertrain_text = ', '.join(powertrain)
        else:
            powertrain_text = str(powertrain)
        
        description = f"{brand} {model} - {car_type}. 动力系统: {powertrain_text}. "
        
        # 添加关键卖点
        selling_points = item.get('key_selling_points', [])
        if isinstance(selling_points, list) and selling_points:
            description += "卖点: " + ', '.join(selling_points[:3]) + ". "
        elif isinstance(selling_points, dict):
            # 处理嵌套卖点
            points = []
            for category, cat_points in selling_points.items():
                if isinstance(cat_points, list) and cat_points:
                    points.extend(cat_points[:2])
            if points:
                description += "卖点: " + ', '.join(points[:3]) + ". "
        
        return description
    
    # 通用情况
    if name:
        return f"项目: {name}. " + json.dumps(item, ensure_ascii=False)[:200]
    elif title:
        return f"标题: {title}. " + json.dumps(item, ensure_ascii=False)[:200]
    else:
        # 返回前200个字符的JSON文本作为描述
        return json.dumps(item, ensure_ascii=False)[:500]

def import_to_qdrant(documents, collection_name="knowledge_base", host="localhost", port=6333):
    """将文档导入到Qdrant"""
    if not documents:
        print("没有数据可导入")
        return
    
    print(f"正在连接到 Qdrant ({host}:{port})...")
    client = QdrantClient(host=host, port=port)
    
    # 加载嵌入模型
    print("正在加载嵌入模型...")
    model_name = "fast-paraphrase-multilingual-minilm-l12-v2"  # 修改为与错误消息中一致的向量名称
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # 实际模型名称不变
    vector_size = model.get_sentence_embedding_dimension()
    
    # 检查集合是否存在，不存在则创建
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if collection_name not in collection_names:
        print(f"正在创建集合 {collection_name}...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                model_name: {  # 使用命名向量格式
                    "size": vector_size,
                    "distance": "Cosine"
                }
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
            "vector": {model_name: embedding},  # 使用命名向量格式
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
    parser = argparse.ArgumentParser(description="从普通JSON文件导入数据到Qdrant向量数据库")
    parser.add_argument("--file", type=str, required=True, help="要导入的JSON文件路径")
    parser.add_argument("--text_field", type=str, help="JSON中包含文本内容的字段名(可选)")
    parser.add_argument("--host", type=str, default="localhost", help="Qdrant服务器主机名")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant服务器端口")
    parser.add_argument("--collection", type=str, default="knowledge_base", help="Qdrant集合名称")
    
    args = parser.parse_args()
    
    # 加载数据
    documents = load_data_from_json(args.file, args.text_field)
    
    # 导入到Qdrant
    if documents:
        import_to_qdrant(documents, args.collection, args.host, args.port)
    else:
        print("没有找到可导入的数据，请检查JSON文件格式")

if __name__ == "__main__":
    main() 