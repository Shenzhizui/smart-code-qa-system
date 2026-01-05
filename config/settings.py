# config/settings.py - 最简单版本
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 基础配置
PROJECT_NAME = "智能代码仓库问答系统"
VERSION = "1.0.0"
DESCRIPTION = "基于LLM和向量数据库的代码仓库语义问答系统"

# 服务器配置
HOST = "127.0.0.1"
PORT = 8000
DEBUG = True

# GitHub配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# 模型配置
EMBEDDING_MODEL = "BAAI/bge-small-zh"
LLM_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2048

# 向量数据库配置
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_data"
CHROMA_COLLECTION_NAME = "code_repository"

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

# 自动创建目录
create_directories()

print("=" * 50)
print(f"{PROJECT_NAME} v{VERSION}")
print("=" * 50)