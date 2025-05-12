import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

def main():
    # 连接到Qdrant服务器
    client = QdrantClient(url="http://localhost:6333")
    print("已连接到Qdrant服务器")
    
    # 加载嵌入模型
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"加载嵌入模型: {model_name}")
    model = SentenceTransformer(model_name)
    
    # 检查集合是否存在
    try:
        collections_info = client.get_collections()
        collection_names = [c.name for c in collections_info.collections]
        print(f"服务器上的集合: {collection_names}")
        
        collection_name = "knowledge_base"
        
        if collection_name not in collection_names:
            print(f"警告: 集合 '{collection_name}' 不存在")
            should_create = input("是否创建此集合并添加示例数据? (y/n): ").lower() == 'y'
            if should_create:
                vector_size = model.get_sentence_embedding_dimension()
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config={"size": vector_size, "distance": "Cosine"}
                )
                print(f"已创建集合: {collection_name}")
                add_sample_data(client, model, collection_name)
            else:
                return
        
        # 检查集合是否为空
        try:
            # 尝试获取一个点来判断集合是否为空
            points = client.scroll(
                collection_name=collection_name,
                limit=1
            )[0]
            
            if not points:
                print(f"警告: 集合 '{collection_name}' 中没有数据点")
                should_add_data = input("是否要添加示例数据? (y/n): ").lower() == 'y'
                if should_add_data:
                    add_sample_data(client, model, collection_name)
        except Exception as e:
            print(f"检查集合数据时出错: {e}")
            should_add_data = input("是否要添加示例数据? (y/n): ").lower() == 'y'
            if should_add_data:
                add_sample_data(client, model, collection_name)
    
        # 交互式搜索
        while True:
            query = input("\n请输入搜索关键词 (输入'exit'退出): ")
            if query.lower() == 'exit':
                break
            
            try:
                search_results = search_qdrant(client, model, query, collection_name)
                
                if not search_results:
                    print("未找到相关结果")
            except Exception as e:
                print(f"搜索时出错: {e}")
    
    except Exception as e:
        print(f"连接Qdrant时出错: {e}")

def search_qdrant(client, model, query_text, collection_name="knowledge_base", limit=5):
    """在Qdrant中搜索"""
    # 生成查询文本的嵌入向量
    query_vector = model.encode(query_text).tolist()
    
    # 在Qdrant中搜索
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    
    # 打印结果
    print(f"\n搜索 '{query_text}' 的结果:")
    for idx, result in enumerate(search_result, 1):
        print(f"\n结果 #{idx} (相似度: {result.score:.4f})")
        
        # 尝试从payload中提取信息
        if result.payload:
            # 如果有text字段，优先显示
            if 'text' in result.payload:
                print(f"内容: {result.payload['text']}")
            
            # 显示其他元数据
            other_info = {k: v for k, v in result.payload.items() if k != 'text'}
            if other_info:
                print("其他信息:")
                for key, value in other_info.items():
                    print(f"  {key}: {value}")
        else:
            print("无附加信息")
    
    return search_result

def add_sample_data(client, model, collection_name):
    """添加示例数据到Qdrant"""
    # 准备示例数据
    texts = [
        "比亚迪（BYD）是中国领先的新能源汽车制造商，成立于1995年，总部位于深圳",
        "比亚迪秦Plus DM-i是一款插电式混合动力汽车，百公里油耗仅为3.8L",
        "比亚迪汉EV是比亚迪的旗舰纯电动轿车，最大续航里程可达700公里",
        "比亚迪唐DM是一款7座SUV，采用插电式混合动力系统",
        "比亚迪是全球最大的电动汽车制造商之一，2023年销量突破300万辆"
    ]
    
    metadata = [
        {"company": "BYD", "type": "company_info", "founded": "1995", "headquarters": "深圳"},
        {"company": "BYD", "model": "秦Plus DM-i", "type": "car_model", "category": "轿车", "powertrain": "插电混动"},
        {"company": "BYD", "model": "汉EV", "type": "car_model", "category": "轿车", "powertrain": "纯电动"},
        {"company": "BYD", "model": "唐DM", "type": "car_model", "category": "SUV", "powertrain": "插电混动"},
        {"company": "BYD", "type": "company_info", "year": "2023", "category": "销售数据"}
    ]
    
    # 为文本生成嵌入向量
    vectors = [model.encode(text).tolist() for text in texts]
    
    # 添加到Qdrant
    points = []
    for i, (vec, text, meta) in enumerate(zip(vectors, texts, metadata)):
        payload = {"text": text}
        payload.update(meta)
        points.append({"id": i, "vector": vec, "payload": payload})
    
    # 删除现有点（如果有）
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=None,  # 删除所有点
            wait=True
        )
    except Exception:
        pass  # 忽略删除错误
    
    # 添加新点
    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )
    
    print(f"成功添加 {len(texts)} 条BYD相关记录到 {collection_name} 集合")

if __name__ == "__main__":
    main()