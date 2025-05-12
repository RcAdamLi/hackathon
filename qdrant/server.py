#!/usr/bin/env python3
import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import numpy as np
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Qdrant MCP Server")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接到本地Qdrant服务器
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
client = QdrantClient(host=qdrant_host, port=qdrant_port)

# 加载文本嵌入模型
model_name = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)

# 集合名称
COLLECTION_NAME = "cars"

# 数据模型
class StoreRequest(BaseModel):
    information: str
    metadata: Optional[Dict[str, Any]] = Field(default=None)

class FindRequest(BaseModel):
    query: str

class StoreResponse(BaseModel):
    status: str
    id: str

class FindResponse(BaseModel):
    results: List[Dict[str, Any]]

@app.get("/")
async def root():
    return {"message": "欢迎使用Qdrant MCP服务器"}

@app.post("/qdrant-store", response_model=StoreResponse)
async def store_information(request: StoreRequest):
    try:
        # 生成嵌入向量
        embedding = model.encode(request.information).tolist()
        
        # 生成唯一ID
        import uuid
        doc_id = str(uuid.uuid4())
        
        # 准备元数据
        metadata = request.metadata or {}
        metadata["text"] = request.information
        
        # 存储到Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                {
                    "id": doc_id,
                    "vector": embedding,
                    "payload": metadata
                }
            ]
        )
        
        return {"status": "success", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存储失败: {str(e)}")

@app.post("/qdrant-find", response_model=FindResponse)
async def find_information(request: FindRequest):
    try:
        # 生成查询向量
        query_vector = model.encode(request.query).tolist()
        
        # 在Qdrant中搜索
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=5
        )
        
        # 格式化结果
        results = []
        for scored_point in search_result:
            result = {
                "id": scored_point.id,
                "score": scored_point.score,
                "content": scored_point.payload.get("text", ""),
                "metadata": {k: v for k, v in scored_point.payload.items() if k != "text"}
            }
            results.append(result)
            
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.on_event("startup")
async def startup_event():
    # 检查集合是否存在，不存在则创建
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": model.get_sentence_embedding_dimension(),
                "distance": "Cosine"
            }
        )
        print(f"创建了新集合: {COLLECTION_NAME}")
    else:
        print(f"集合 {COLLECTION_NAME} 已存在")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 