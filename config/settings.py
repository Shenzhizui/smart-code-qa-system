# config/settings.py - 修复版本
import os
from pathlib import Path
from dotenv import load_dotenv  # 添加这行

# 加载环境变量 - 添加这行
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== 基础配置 ====================
PROJECT_NAME = "智能代码仓库问答系统"
VERSION = "1.0.0"
DESCRIPTION = "基于LLM和向量数据库的代码仓库语义问答系统"

# ==================== 服务器配置 ====================
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# ==================== GitHub配置 ====================
# 修复这里：确保从环境变量读取
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ==================== 模型配置 ====================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# ==================== 向量数据库配置 ====================
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_data")))
CHROMA_COLLECTION_NAME = "code_repository"

# ==================== 函数定义 ====================
def create_directories():
    """创建必要的目录"""
    directories = [
        CHROMA_PERSIST_DIR,
        BASE_DIR / "data",
        BASE_DIR / "logs",
        BASE_DIR / "temp",
        BASE_DIR / "uploads"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True, parents=True)
        print(f"创建目录: {directory}")
    
    return True

# ==================== 初始化 ====================
# 自动创建目录
create_directories()

# 打印配置摘要
print("=" * 50)
print(f"{PROJECT_NAME} v{VERSION}")
print("=" * 50)
print(f"GitHub Token: {'已配置' if GITHUB_TOKEN and GITHUB_TOKEN != 'your_github_token_here' else '未配置'}")
print(f"主机: {HOST}:{PORT}")
print(f"调试模式: {DEBUG}")
print("=" * 50)