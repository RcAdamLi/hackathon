# Qdrant MCP 服务器

这个目录包含连接到本地Qdrant向量数据库的MCP服务器。

## 功能

- 连接到本地Qdrant实例
- 提供存储和检索向量数据的API
- 支持知识库查询功能
- 提供导入数据到Qdrant的工具

## 使用方法

1. 先确保Docker和docker-compose已安装
2. 运行 `docker-compose up -d` 启动Qdrant服务
3. 使用 `python3 qdrant/import_data.py` 导入示例数据
4. 启动MCP服务器 `python3 qdrant/server.py` 