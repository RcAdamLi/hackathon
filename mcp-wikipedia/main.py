from mcp.server.fastmcp import FastMCP
import wikipedia
import os
import sys

mcp = FastMCP(
    "Wikipedia",
    dependencies=["wikipedia"],
)

# 设置自定义维基百科API URL（如果环境变量中定义了）
if "WIKIPEDIA_API_URL" in os.environ:
    # 直接修改API_URL属性
    wikipedia.API_URL = os.environ["WIKIPEDIA_API_URL"]

@mcp.tool()
def search(query: str):
    return wikipedia.search(query)

@mcp.tool()
def summary(query: str):
    return wikipedia.summary(query)

@mcp.tool()
def page(query: str):
    """获取维基百科页面的完整内容"""
    try:
        wiki_page = wikipedia.page(query)
        return {
            "title": wiki_page.title,
            "content": wiki_page.content,
            "url": wiki_page.url,
            "categories": wiki_page.categories
        }
    except wikipedia.exceptions.DisambiguationError as e:
        # 处理消歧义页面
        return {
            "error": "消歧义页面",
            "options": e.options,
            "message": "请选择以下选项之一并重新查询"
        }
    except wikipedia.exceptions.PageError:
        return {"error": "找不到页面", "message": f"找不到关于'{query}'的页面"}
    except Exception as e:
        return {"error": "未知错误", "message": str(e)}

@mcp.tool()
def random():
    return wikipedia.random()

@mcp.tool()
def set_lang(lang: str):
    wikipedia.set_lang(lang)
    return f"Language set to {lang}"

# 添加新工具以显示当前API URL
@mcp.tool()
def get_api_url():
    """获取当前使用的维基百科API URL"""
    return f"当前维基百科API URL: {wikipedia.API_URL}"

# 添加新工具以设置自定义API URL
@mcp.tool()
def set_api_url(url: str):
    """设置自定义维基百科API URL"""
    try:
        # 直接修改API_URL属性
        old_url = wikipedia.API_URL
        wikipedia.API_URL = url
        return f"维基百科API URL已从 {old_url} 更改为: {url}"
    except Exception as e:
        return f"设置API URL时出错: {str(e)}"

if __name__ == "__main__":
    # 检查是否指定了传输方式和端口
    transport = "stdio"  # 默认使用stdio
    port = 8000  # 默认端口
    host = "127.0.0.1"  # 默认主机
    
    # 解析命令行参数
    # 示例: python main.py sse 8000
    if len(sys.argv) >= 1:
        transport = sys.argv[1]
        
    print(f"启动维基百科MCP服务，传输方式: {transport}")
    mcp.run(transport=transport)