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
MODEL_NAME = "all-MiniLM-L6-v2"  # 与mcp.json配置一致
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 模型的向量维度

def initialize_model():
    """初始化语义模型"""
    try:
        print(f"正在加载语义模型...")
        model = SentenceTransformer(MODEL_NAME)
        print(f"模型加载完成")
        return model
    except Exception as e:
        print(f"加载模型失败: {e}")
        sys.exit(1) 