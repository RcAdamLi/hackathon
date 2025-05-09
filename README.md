# 本地开发工具集

本项目包含以下多个本地开发工具：

## 1. 本地知识库 (KB)

在`kb`文件夹中包含了一个基于Elasticsearch和Kibana的本地知识库系统，可以帮助您在本地环境中存储、检索和可视化数据。

### 使用方法

请参见 [kb/KB-README.md](kb/KB-README.md) 获取详细使用说明。

简要步骤：
1. 启动服务：`docker-compose up -d`
2. 导入示例数据：`cd kb && python import_data_to_kb.py sample_kb_data.json`
3. 搜索知识库：`cd kb && python search_kb.py 关键词`
4. 通过浏览器访问Kibana界面：http://localhost:5601

## 2. 本地Wiki (MediaWiki)

MediaWiki服务提供了一个本地的维基百科系统，可用于存储和组织知识。

### 访问方式

- URL: http://localhost:8080
- 数据库由MariaDB提供支持

## 3. Grafana监控面板

Grafana提供了一个强大的数据可视化和监控平台。

### 访问方式

- URL: http://localhost:3000 