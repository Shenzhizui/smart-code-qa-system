# 第1周工作总结：项目初始化与环境搭建

## 📅 时间范围
2025年9月1日 - 2025年9月7日

## 🎯 本周目标
完成项目基础环境搭建，验证所有核心依赖的正确安装。

## ✅ 已完成任务

### 1. 项目环境搭建
- [x] 创建项目目录：`smart-code-qa-system`
- [x] 创建Python虚拟环境：`python -m venv venv`
- [x] 配置VSCode开发环境
- [x] 激活虚拟环境并确认工作正常

### 2. 核心依赖安装
- [x] **sentence-transformers==2.2.2** - 嵌入模型库
- [x] **chromadb==0.4.0** - 向量数据库
- [x] **llama-index==0.10.0** - 检索增强生成框架
- [x] **fastapi==0.99.** - Web框架
- [x] **PyGithub==2.1.1** - GitHub API客户端
- [x] **python-dotenv==1.0.0** - 环境变量管理
- [x] **pydantic==2.5.0** - 数据验证
- [x] **uvicorn[standard]==0.24.0** - ASGI服务器

### 3. 项目结构创建
smart-code-qa-system/
├── .env # 环境变量配置
├── .env.example # 环境变量模板
├── requirements.txt # Python依赖列表
├── config/ # 配置模块
│ ├── init.py
│ └── settings.py # 应用配置
├── src/ # 源代码
│ ├── init.py
│ ├── crawler/ # 数据爬取模块
│ ├── vector_store/ # 向量存储模块
│ ├── qa_engine/ # 问答引擎
│ ├── auth/ # 权限控制
│ ├── im_bot/ # IM集成
│ └── web/ # Web接口
├── tests/ # 测试代码
├── docs/ # 文档
├── scripts/ # 工具脚本
├── data/ # 数据存储
├── logs/ # 日志文件
├── temp/ # 临时文件
└── chroma_data/ # 向量数据库存储

### 4. 配置文件创建
#### **config/settings.py**
```python
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


```

#### **.env.example**

```
# 智能代码仓库问答系统环境变量

# 服务器配置
HOST=127.0.0.1
PORT=8000
DEBUG=True

# GitHub配置（必需）
# 获取token: https://github.com/settings/tokens 
GITHUB_TOKEN=your_github_token_here

# 模型配置
EMBEDDING_MODEL=BAAI/bge-small-zh
LLM_MODEL=gpt-3.5-turbo

# 数据库配置
CHROMA_PERSIST_DIR=./chroma_data
```

#### **requirements.txt**

```
sentence-transformers==2.2.2
chromadb==0.4.0
llama-index==0.10.0
fastapi==0.104.1
PyGithub==2.1.1
python-dotenv==1.0.0
pydantic==2.5.0
uvicorn[standard]==0.24.0
beautifulsoup4==4.12.2
markdown==3.5.1
requests==2.31.0
```

### 5. 环境验证测试

**验证结果**

```
============================================================
智能代码仓库问答系统 - 环境测试
============================================================
Python版本: 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]
工作目录: D:\Graduation Project\smart-code-qa-system
测试关键模块:
  ✅ sentence_transformers
  ✅ chromadb
  ✅ llama_index
  ✅ fastapi
  ✅ github
============================================================
测试完成
============================================================
```

### 6. 关键问题与解决方案

#### 问题1：sentence-transformers网络连接失败

- **症状**：ProtocolError: Connection aborted
- **原因**：网络连接不稳定，无法从HuggingFace下载模型
- **解决方案**：暂时跳过，后续使用离线模式或本地缓存

#### 问题2：配置文件导入错误

- **症状**：module 'config.settings' has no attribute 'PROJECT_NAME'
- **原因**：settings.py文件格式错误或缓存问题
- **解决方案**：重新创建settings.py，清除Python模块缓存

#### 问题3：虚拟环境激活问题

- **症状**：无法激活虚拟环境
- **原因**：Windows路径问题
- **解决方案**：使用`venv\Scripts\activate.bat`而不是`source venv/bin/activate`

## 🎓 本周学习重点

1. **Python虚拟环境管理**
   - 理解虚拟环境的作用：隔离项目依赖
   - 掌握创建和激活虚拟环境的方法
   - 学习在VSCode中配置Python解释器
2. **项目结构设计**
   - 学习模块化项目组织
   - 理解`__init__.py`的作用
   - 掌握合理的目录结构划分
3. **依赖管理**
   - 使用`requirements.txt`管理依赖
   - 理解版本兼容性问题
   - 掌握使用国内镜像加速安装
4. **环境变量配置**
   - 学习使用`python-dotenv`管理敏感信息
   - 理解环境变量在部署中的重要性
   - 掌握GitHub Token的获取和配置
5. **错误调试**
   - 学习阅读Python错误信息
   - 掌握基本的调试技巧
   - 理解模块导入路径问题

## 📈 技术决策与理由

### 1. 技术栈选择

表格

| 技术                  | 版本    | 选择理由                       |
| :-------------------- | :------ | :----------------------------- |
| sentence-transformers | 2.2.2   | 提供高质量句子嵌入，支持多语言 |
| chromadb              | 0.4.0   | 轻量级向量数据库，易于集成     |
| llama-index           | 0.10.0  | 强大的RAG框架，简化开发        |
| fastapi               | 0.104.1 | 高性能Web框架，自动生成API文档 |
| PyGithub              | 2.1.1   | 官方推荐的GitHub API客户端     |

### 2. 模型选择

- **嵌入模型**：BAAI/bge-small-zh
  - **理由**：专门优化的中文嵌入模型，体积小，性能好
  - **替代方案**：all-MiniLM-L6-v2（英文）

### 3. 开发环境

- **操作系统**：Windows 10/11
- **Python版本**：3.11.9
- **IDE**：VSCode
- **包管理**：pip + 国内镜像源

## 🔧 遇到的问题与解决方案记录

### 问题记录表

表格

复制

| 问题             | 解决方案                          | 学习点                 |
| :--------------- | :-------------------------------- | :--------------------- |
| 依赖版本冲突     | 固定关键依赖版本，使用兼容组合    | 理解Python依赖解析机制 |
| 网络连接超时     | 使用国内镜像源，分步安装          | 国内开发环境优化       |
| 模块导入错误     | 检查`__init__.py`，确认Python路径 | Python模块系统理解     |
| 环境变量加载失败 | 使用绝对路径，检查文件编码        | 跨平台环境变量管理     |

## 📝 代码质量保证

### 1. 代码规范

- 使用PEP 8编码规范
- 添加适当的类型提示
- 编写清晰的文档字符串

### 2. 错误处理

- 使用`try-except`处理可能失败的操作
- 添加详细的日志记录
- 提供有意义的错误信息

### 3. 可维护性

- 模块化设计，高内聚低耦合
- 清晰的函数和变量命名
- 适当的代码注释

## 🚀 下一步计划

### 第2周：GitHub数据爬取模块开发（9月8日-9月14日）

- **Day 1**：GitHub API基础，获取仓库信息
- **Day 2**：文件列表获取，代码文件下载
- **Day 3**：Issue和PR数据获取
- **Day 4**：数据清洗和预处理
- **Day 5**：数据存储和序列化
- **Day 6**：增量更新机制
- **Day 7**：模块集成测试

### 技术学习重点

- GitHub REST API使用
- 异步编程和速率限制处理
- 数据清洗和分块算法
- JSON序列化和文件操作

## 📁 重要文件清单

### 必须保留的文件

- **config/settings.py** - 应用配置
- **.env** - 环境变量（不提交到Git）
- **.env.example** - 环境变量模板
- **requirements.txt** - 依赖列表
- **docs/week1_summary.md** - 本周工作总结

### 可以删除的临时文件

- 各种`test_*.py`测试脚本
- `fix_*.py`修复脚本
- `*.bat`批处理文件

## 💡 经验教训

### 成功经验

- **从小开始**：从最小可行系统开始，逐步扩展
- **版本控制**：及时提交代码，添加有意义的提交信息
- **文档记录**：边开发边记录，避免遗忘

### 改进点

- **网络问题预案**：为网络依赖准备离线方案
- **错误处理**：更完善的错误处理和用户提示
- **自动化脚本**：编写更多自动化脚本减少手动操作

**总结**：第1周成功搭建了开发环境，验证了核心功能，为后续开发奠定了坚实基础。虽然遇到一些网络和配置问题，但都找到了解决方案，积累了宝贵的调试经验。
