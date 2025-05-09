# 本地知识库 (KB) 使用指南

本项目提供了一个基于Elasticsearch和Kibana的本地知识库系统，可以帮助您在本地环境中存储、检索和可视化数据。

## 环境要求

- Docker
- Docker Compose
- Python 3.6+（可选，用于运行辅助脚本）

## 启动服务

使用以下命令启动所有服务：

```bash
docker-compose up -d
```

## 访问知识库

启动后，您可以通过以下方式访问服务：

1. **Elasticsearch API**：
   - URL: http://localhost:9200
   - 这是知识库的后端存储，您可以通过REST API直接与其交互

2. **Kibana界面**：
   - URL: http://localhost:5601
   - 这是知识库的可视化界面，您可以在这里创建索引模式、搜索数据和创建数据可视化

## 辅助工具

本项目提供了几个Python脚本，帮助您更方便地使用知识库。要使用这些脚本，请先安装依赖：

```bash
pip install -r kb_requirements.txt
```

### 导入数据工具

#### 基本导入工具

使用 `import_data_to_kb.py` 脚本可以批量导入数据到知识库：

```bash
# 导入JSON数据
python import_data_to_kb.py sample_kb_data.json

# 导入CSV数据
python import_data_to_kb.py sample_kb_data.csv
```

#### 语义向量导入工具（高级）

使用 `semantic_import.py` 脚本可以批量导入数据并添加语义向量，支持语义搜索：

```bash
# 导入JSON数据并添加语义向量
python semantic_import.py sample_kb_data.json

# 导入CSV数据并添加语义向量
python semantic_import.py sample_kb_data.csv
```

**注意**：语义导入需要下载模型，首次运行可能需要一些时间。

示例数据文件已包含在项目中：
- `sample_kb_data.json` - JSON格式的示例数据
- `sample_kb_data.csv` - CSV格式的示例数据

### 搜索工具

#### 关键词搜索

使用 `search_kb.py` 脚本可以快速搜索知识库：

```bash
python search_kb.py 关键词
```

例如：

```bash
python search_kb.py Docker
python search_kb.py "机器学习 算法"
```

#### 语义搜索（高级）

使用 `semantic_search.py` 脚本可以进行基于语义的搜索：

```bash
python semantic_search.py "搜索查询"
```

例如：

```bash
python semantic_search.py "如何部署应用？"
python semantic_search.py "什么是向量数据库？"
```

语义搜索不仅仅查找包含特定关键词的文档，而是理解查询的含义，并找到语义上最相关的内容。这对于自然语言查询特别有用，可以找到没有包含查询中确切词语但意思相关的文档。

## 将数据添加到知识库

除了使用辅助工具，您还可以通过以下方式添加数据到Elasticsearch：

### 1. 使用Elasticsearch REST API

```bash
# 创建索引
curl -X PUT "localhost:9200/my_knowledge_base"

# 添加文档
curl -X POST "localhost:9200/my_knowledge_base/_doc" -H "Content-Type: application/json" -d'
{
  "title": "示例文档",
  "content": "这是一个测试文档的内容",
  "tags": ["测试", "示例"],
  "date": "2023-06-01"
}'
```

### 2. 通过Kibana界面

1. 访问 http://localhost:5601
2. 进入 "Dev Tools" 部分
3. 使用控制台执行上述相同的Elasticsearch命令

## 搜索知识库

### 使用Elasticsearch API搜索：

```bash
# 基本搜索
curl -X GET "localhost:9200/my_knowledge_base/_search" -H "Content-Type: application/json" -d'
{
  "query": {
    "match": {
      "content": "搜索关键词"
    }
  }
}'
```

### 使用Kibana搜索：

1. 访问 http://localhost:5601
2. 创建索引模式 (Index Pattern)
3. 使用 "Discover" 部分进行搜索和浏览

## 语义搜索与关键词搜索对比

| 特性 | 关键词搜索 | 语义搜索 |
|-----|----------|---------|
| 搜索机制 | 基于词语匹配 | 基于语义相似度 |
| 查询方式 | 精确关键词 | 自然语言问题或描述 |
| 处理同义词 | 不支持（除非手动设置） | 自动支持 |
| 理解上下文 | 有限 | 较好 |
| 查询效果示例 | "Docker容器" 只会返回包含"Docker"或"容器"的文档 | "如何隔离应用环境" 可能返回关于Docker的文档，即使没有提到这些确切词语 |

## 数据持久化

所有数据都存储在Docker卷中，即使容器重启，数据也不会丢失：
- 关键词搜索数据存储在`elasticsearch-data`卷中
- 语义搜索的向量数据也存储在相同的卷中，但使用不同的索引

## 关闭服务

要关闭所有服务，请运行：

```bash
docker-compose down
```

如果您想同时删除所有数据卷（注意：这将删除所有存储的数据），请运行：

```bash
docker-compose down -v
``` 