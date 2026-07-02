#!/bin/bash
# 深视新闻 AI 写稿助手 — 一键启动脚本
# 使用方法：在终端中运行 bash start.sh

echo "📝 深视新闻 AI 写稿助手"
echo "========================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    echo "   下载地址：https://www.python.org/downloads/"
    read -p "按回车退出..."
    exit 1
fi

# 检查并安装依赖
echo "📦 检查依赖..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   正在安装 Streamlit..."
    pip3 install streamlit requests -q
fi
echo "   ✅ 依赖就绪"
echo ""

# 启动
echo "🚀 启动中..."
echo "   浏览器将自动打开。如未打开，手动访问：http://localhost:8501"
echo "   按 Ctrl+C 停止服务"
echo ""

streamlit run app.py --server.headless true
