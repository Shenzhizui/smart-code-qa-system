# 智能代码问答系统

基于LLM与向量数据库的智能代码仓库语义问答系统设计与实现

## 🎯 项目简介

本项目是一个智能代码问答系统，能够理解代码仓库的语义内容，回答开发者关于代码、Issues、Pull Requests等的问题。系统通过GitHub API获取数据，使用向量数据库存储语义向量，实现智能语义搜索和问答功能。

## ✨ 核心功能

### 1. **多源数据采集**
   - GitHub代码文件获取
   - Issues和Pull Requests数据爬取
   - README和文档内容提取

### 2. **智能向量化**
   - 文本嵌入模型（sentence-transformers）
   - 语义向量生成与存储
   - 支持离线模式和镜像源

### 3. **语义搜索**
   - 基于向量相似度的语义搜索
   - 多类型文档检索
   - 元数据过滤支持

### 4. **问答系统**
   - 智能问题理解
   - 上下文感知答案生成
   - 多源信息融合

## 🏗️ 技术架构
智能代码问答系统
├── 数据层 (Data Layer)
│ ├── GitHub API爬取器
│ ├── 代码文件处理器
│ └── Issue/PR解析器
├── 向量层 (Vector Layer)
│ ├── 文本嵌入模型
│ ├── ChromaDB向量存储
│ └── 数据索引器
├── 检索层 (Retrieval Layer)
│ ├── 语义搜索引擎
│ ├── 相似度计算
│ └── 结果排序
└── 应用层 (Application Layer)
├── 问答引擎
├── Web API接口
└── 用户界面

## 📦 技术栈

- **编程语言**: Python 3.11
- **AI模型**: sentence-transformers (paraphrase-MiniLM-L3-v2)
- **向量数据库**: ChromaDB
- **Web框架**: FastAPI (计划)
- **前端**: Streamlit/React (计划)
- **GitHub API**: PyGithub
- **数据处理**: Pandas, NumPy
- **开发工具**: VSCode, Git, Windows 10/11

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Git
- GitHub账号（用于API访问）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/Shenzhizui/smart-code-qa-system.git
   cd smart-code-qa-system
   python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    pip install -r requirements.txt
    # 创建 .env 文件
   echo "GITHUB_TOKEN=你的GitHub_Token" > .env
## Day 1: GitHub基础爬取
python scripts/day1_demo.py

## Day 2: 代码文件获取
python scripts/day2_demo.py

## Day 3: Issue和PR数据
python scripts/day3_demo.py

## Day 4: 数据向量化与存储
python scripts/day4_demo.py
smart-code-qa-system/
├── src/                    # 源代码
│   ├── crawler/           # 爬取器模块
│   │   ├── github_crawler.py
│   │   ├── data_processor.py
│   │   └── issue_processor.py
│   ├── vector_store/      # 向量存储模块
│   │   ├── embedding.py
│   │   ├── chroma_store.py
│   │   ├── indexer.py
│   │   └── data_integrator.py
│   ├── qa_engine/         # 问答引擎（待开发）
│   ├── auth/              # 认证模块（待开发）
│   └── web/               # Web模块（待开发）
├── scripts/               # 演示脚本
│   ├── day1_demo.py
│   ├── day2_demo.py
│   ├── day3_demo.py
│   ├── day4_demo.py
│   └── qa_test_integrated.py
├── tests/                 # 测试文件
│   ├── test_day1.py
│   ├── test_day2.py
│   ├── test_day3.py
│   └── test_day4.py
├── data/                  # 数据存储
│   ├── *.json            # 数据文件
│   └── integration_*.json # 集成信息
├── models/               # 模型缓存
├── chroma_data/          # 向量数据库
├── requirements.txt      # 依赖列表
├── .env                 # 环境变量
└── README.md            # 项目说明

# 📚 开发进展

## ✅ 已完成

Day 1: GitHub爬取器基础框架

Day 2: 代码文件获取与处理

Day 3: Issue和PR数据获取

Day 4: 数据向量化与存储

文本嵌入模型实现

ChromaDB向量存储

数据索引器

实际数据集成

## 🚧 进行中

Day 5: 问答引擎设计与实现

Day 6: Web API接口开发

Day 7: 前端界面开发

Day 8: 系统集成与测试

## 🧪 测试

bash

### 运行所有测试
python -m pytest tests/

### 运行特定测试
python tests/test_day1.py
python tests/test_day2.py
python tests/test_day3.py
python tests/test_day4.py