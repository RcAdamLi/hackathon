#!/bin/bash
# 启动Qdrant和MCP服务的脚本

# 确保脚本可执行
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行或需要sudo权限。请启动Docker或使用sudo运行此脚本。"
    exit 1
fi

# 当前目录
SCRIPT_DIR=$(dirname "$(realpath "$0")")
WORKSPACE_DIR=$(dirname "$SCRIPT_DIR")

# 安装Python依赖
echo "安装Python依赖..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# 启动Docker服务
echo "启动Docker服务..."
cd "$WORKSPACE_DIR" && docker-compose up -d qdrant

# 等待Qdrant启动
echo "等待Qdrant启动..."
sleep 5

# 导入示例数据
echo "导入示例数据..."
python "$SCRIPT_DIR/import_data.py" --file_type sample --samples 10

# 启动MCP服务器
echo "启动MCP服务器..."
python "$SCRIPT_DIR/server.py" 