#!/usr/bin/env python3
"""
Day 4 演示脚本：数据向量化与ChromaDB存储
在项目根目录运行：python scripts/day4_demo.py
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 设置HuggingFace镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

def main():
    print("=" * 70)
    print("Day 4 演示：数据向量化与ChromaDB存储")
    print("=" * 70)
    
    # 1. 初始化嵌入模型
    print("\n1. 初始化嵌入模型...")
    try:
        from src.vector_store.embedding import TextEmbeddingModel
        embedder = TextEmbeddingModel()
        print(f"  嵌入模型加载成功: {embedder.model_name}")
        print(f"   维度: {embedder.dimensions}")
        
        # 测试嵌入
        test_text = "基于LLM的智能代码问答系统"
        embedding = embedder.get_embedding(test_text)
        print(f"   测试文本: '{test_text}'")
        print(f"   向量形状: {embedding.shape}")
        
    except ImportError as e:
        print(f"  导入失败: {e}")
        return
    
    # 2. 初始化ChromaDB向量存储
    print("\n2. 初始化ChromaDB向量存储...")
    try:
        from src.vector_store.chroma_store import ChromaVectorStore
        
        # 使用演示专用集合
        vector_store = ChromaVectorStore("day4_demo_collection")
        print(f"  ChromaDB初始化成功")
        print(f"   存储路径: {vector_store.persist_dir}")
        print(f"   集合名称: {vector_store.collection.name}")
        
    except Exception as e:
        print(f"  ChromaDB初始化失败: {e}")
        return
    
    # 3. 准备演示数据
    print("\n3. 准备演示数据...")
    demo_documents = [
        {
            "text": "Python是一种解释型、高级别的通用编程语言。由Guido van Rossum创建，第一版发布于1991年。",
            "metadata": {
                "type": "language",
                "category": "programming",
                "source": "wikipedia",
                "year": 1991,
                "creator": "Guido van Rossum"
            }
        },
        {
            "text": "ChromaDB是一个开源的嵌入向量数据库，专为AI应用设计。它支持快速的相似性搜索和元数据过滤。",
            "metadata": {
                "type": "database",
                "category": "vector_store",
                "source": "official",
                "language": "Python",
                "purpose": "AI applications"
            }
        },
        {
            "text": "GitHub是一个基于Git的代码托管平台，用于版本控制和协作。它让开发者能够共同参与项目。",
            "metadata": {
                "type": "platform",
                "category": "code_hosting",
                "source": "company",
                "founded": 2008,
                "users": "数百万开发者"
            }
        },
        {
            "text": "FastAPI是一个现代、快速的Web框架，用于基于标准Python类型提示构建API。它具有自动文档生成。",
            "metadata": {
                "type": "framework",
                "category": "web",
                "source": "open_source",
                "language": "Python",
                "features": "自动文档、验证"
            }
        },
        {
            "text": "机器学习是人工智能的一个分支，使计算机能够从数据中学习并做出预测或决策，而无需明确编程。",
            "metadata": {
                "type": "technology",
                "category": "ai",
                "source": "academic",
                "applications": "预测、分类、推荐"
            }
        }
    ]
    
    print(f"  准备了 {len(demo_documents)} 个演示文档")
    for i, doc in enumerate(demo_documents, 1):
        doc_type = doc["metadata"]["type"]
        print(f"   文档{i}: {doc_type} - {doc['text'][:50]}...")
    
    # 4. 添加文档到向量存储
    print("\n4. 添加文档到向量存储...")
    vector_store.add_documents(demo_documents)
    print(f"  成功添加 {len(demo_documents)} 个文档")
    
    # 5. 演示语义搜索
    print("\n5. 演示语义搜索...")
    test_queries = [
        ("什么是Python？", "查询编程语言"),
        ("向量数据库功能", "查询数据库功能"),
        ("代码托管服务", "查询代码平台"),
        ("Web开发框架", "查询Web框架"),
        ("人工智能技术", "查询AI技术")
    ]
    
    for query, description in test_queries:
        print(f"\n {description}")
        print(f"   查询: '{query}'")
        
        results = vector_store.search(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                doc = result['document']
                if len(doc) > 60:
                    doc = doc[:60] + "..."
                
                print(f"   结果{i}: {doc}")
                print(f"       相似度: {result['score']:.4f}")
                print(f"       类型: {result['metadata'].get('type')}")
        else:
            print("   未找到相关结果")
    
    # 6. 演示元数据过滤
    print("\n6. 演示元数据过滤搜索...")
    print("   查询: 'Python相关技术'")
    print("   过滤条件: type='language' OR type='framework'")
    
    # 注意：ChromaDB的过滤语法
    try:
        results = vector_store.search(
            "Python相关技术", 
            n_results=3,
            filter_metadata={"$or": [{"type": "language"}, {"type": "framework"}]}
        )
        
        if results:
            print(f"   找到 {len(results)} 个过滤结果:")
            for result in results:
                doc_type = result['metadata'].get('type', '未知')
                doc_preview = result['document']
                if len(doc_preview) > 60:
                    doc_preview = doc_preview[:60] + "..."
                print(f"      - {doc_type}: {doc_preview}")
        else:
            print("     未找到过滤结果")
    except Exception as e:
        print(f"     过滤搜索失败（可能是语法问题）: {e}")
        # 尝试简单的过滤
        try:
            results = vector_store.search("Python", n_results=3)
            if results:
                print(f"   找到 {len(results)} 个相关结果（无过滤）")
        except:
            pass
    
    # 7. 初始化数据索引器
    print("\n7. 初始化数据索引器...")
    try:
        from src.vector_store.indexer import DataIndexer
        
        indexer = DataIndexer("day4_demo_indexer")
        print("  数据索引器初始化成功")
        
        # 显示支持的数据类型
        print("\n  支持的数据类型:")
        print("   • 代码文件 (.py, .js, .java, .cpp 等)")
        print("   • GitHub Issues (问题跟踪)")
        print("   • Pull Requests (代码合并请求)")
        print("   • README文档 (项目说明)")
        print("   • 代码注释 (函数和类文档)")
        
    except Exception as e:
        print(f"  数据索引器初始化失败: {e}")
    
    # 8. 演示模拟数据索引
    print("\n8. 演示模拟数据索引...")
    try:
        # 模拟代码文件
        code_files = [
            {
                "path": "examples/demo.py",
                "content": """
                # 示例代码文件
                def greet(name: str) -> str:
                    \"\"\"
                    问候函数
                    
                    Args:
                        name: 用户名
                        
                    Returns:
                        问候语
                    \"\"\"
                    return f"Hello, {name}!"
                """,
                "language": "python",
                "name": "demo.py",
                "repo_name": "demo-repo",
                "size": 512
            }
        ]
        
        # 模拟Issue
        issues = [
            {
                "title": "示例Issue：问候函数需要国际化",
                "body": "当前greet函数只支持英文问候，需要添加多语言支持。",
                "html_url": "https://github.com/demo/repo/issues/1",
                "number": 1,
                "state": "open",
                "user": {"login": "demo-user"},
                "repo_name": "demo-repo",
                "created_at": "2024-01-20T10:00:00Z",
                "comments": 3,
                "labels": [{"name": "enhancement"}, {"name": "i18n"}]
            }
        ]
        
        print("   索引代码文件...")
        indexer.index_code_files(code_files)
        
        print("   索引Issues...")
        indexer.index_issues(issues)
        
        print("  模拟数据索引完成")
        
        # 演示搜索
        vector_store = indexer.get_vector_store()
        results = vector_store.search("国际化", n_results=1)
        
        if results:
            print(f"   搜索'国际化'找到结果，相似度: {results[0]['score']:.4f}")
        
    except Exception as e:
        print(f"  模拟数据索引失败: {e}")
    
    # 9. 保存和显示统计信息
    print("\n9. 保存和显示统计信息...")
    try:
        # 获取集合信息
        info = vector_store.get_collection_info()
        
        print(f"    向量存储统计:")
        print(f"   集合名称: {info['collection_name']}")
        print(f"   文档数量: {info['document_count']}")
        
        # 保存演示结果
        demo_results = {
            "embedding_model": embedder.model_name,
            "embedding_dimensions": embedder.dimensions,
            "chromadb_collection": vector_store.collection.name,
            "document_count": info['document_count'],
            "test_queries": test_queries
        }
        
        output_file = "data/demo4_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(demo_results, f, ensure_ascii=False, indent=2)
        
        print(f"   演示结果已保存到 {output_file}")
        
    except Exception as e:
        print(f"     保存统计信息时出错: {e}")
    
    # 10. 清理演示数据（可选）
    print("\n10. 清理演示数据（可选）...")
    cleanup = input("   是否清理演示数据？(Y/N): ").strip().lower()
    
    if cleanup == 'Y':
        try:
            vector_store.reset_collection()
            print("   演示数据已清理")
        except Exception as e:
            print(f"     清理数据时出错: {e}")
    else:
        print("   演示数据已保留")
    
    print("\n" + "=" * 70)
    print("  Day 4 演示完成！")
    print("=" * 70)
    
    print("\n 完成的功能:")
    print("1. 嵌入模型初始化与测试")
    print("2. ChromaDB向量存储初始化")
    print("3. 文档向量化与存储")
    print("4. 语义搜索功能演示")
    print("5. 元数据过滤搜索（基础）")
    print("6. 数据索引器初始化")
    print("7. 模拟数据索引流程")
    print("8. 结果保存与统计")
    
    print("\n  下一步:")
    print("1. 运行完整测试: python test_day4.py")
    print("2. 集成Day 2的代码数据")
    print("3. 集成Day 3的Issue和PR数据")
    print("4. 准备Day 5：问答引擎开发")
    
    print("\n  创建的目录和文件:")
    print(f"   • chroma_data/ - ChromaDB存储目录")
    print(f"   • models/ - 模型缓存目录")
    print(f"   • data/demo4_results.json - 演示结果")

if __name__ == "__main__":
    main()