# Qdrant知识库系统

这是一个基于Qdrant向量数据库的本地知识库系统，专为语义搜索而设计。

## 功能特点

- 支持语义搜索（不仅仅是关键词匹配）
- 轻量级部署（仅需一个容器）
- 支持JSON和CSV数据导入
- 高性能向量检索
- 完全本地部署，数据隐私有保障

## 使用方法

### 启动服务

```bash
# 使用Docker Compose启动Qdrant服务
docker-compose up -d
```

或者使用主项目的docker-compose.yml启动：

```bash
# 在项目根目录执行
docker-compose up -d qdrant
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 导入数据

```bash
# 导入JSON数据
python qdrant_kb.py import sample_kb_data.json

# 导入CSV数据
python qdrant_kb.py import sample_kb_data.csv
```

### 搜索知识库

```bash
# 语义搜索
python qdrant_kb.py search "您的自然语言查询"
```

## 示例

```bash
# 查询Docker相关信息
python qdrant_kb.py search "容器技术有什么优势？"

# 查询向量数据库
python qdrant_kb.py search "什么是向量相似度检索？"
```

## 文件说明

- `qdrant_kb.py` - 主程序，包含导入和搜索功能
- `docker-compose.yml` - Docker Compose配置文件
- `requirements.txt` - Python依赖
- `sample_kb_data.json` - 示例JSON数据
- `sample_kb_data.csv` - 示例CSV数据 