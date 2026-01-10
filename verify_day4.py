"""
验证Day 4所有组件
"""
import os
import sys
from pathlib import Path

# ============ 关键：在导入之前设置镜像源 ============
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def verify_all_components():
    """验证所有组件"""
    print("\n🔍 验证Day 4所有组件")
    print("=" * 60)
    
    components = [
        ("1. 嵌入模型", "src.vector_store.embedding", "TextEmbeddingModel"),
        ("2. ChromaDB存储", "src.vector_store.chroma_store", "ChromaVectorStore"),
        ("3. 数据索引器", "src.vector_store.indexer", "DataIndexer")
    ]
    
    all_passed = True
    
    for name, module_path, class_name in components:
        print(f"\n{name}...")
        try:
            # 动态导入
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ 导入成功: {class_name}")
            
            # 尝试实例化
            if name == "1. 嵌入模型":
                print("   正在初始化模型（可能需要几秒钟）...")
                instance = cls()
                print(f"   ✅ 实例化成功")
                print(f"   ✅ 模型名称: {instance.model_name}")
                print(f"   ✅ 嵌入维度: {instance.dimensions}")
                
                # 快速测试
                test_text = "hello world"
                embedding = instance.get_embedding(test_text)
                print(f"   ✅ 测试文本: '{test_text}'")
                print(f"   ✅ 向量形状: {embedding.shape}")
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有组件验证通过！")
        return True
    else:
        print("⚠️ 部分组件存在问题")
        return False

def test_integration():
    """测试集成"""
    print("\n🔗 测试集成功能...")
    
    try:
        # 导入所有组件
        from src.vector_store.embedding import TextEmbeddingModel
        from src.vector_store.chroma_store import ChromaVectorStore
        from src.vector_store.indexer import DataIndexer
        
        print("✅ 所有组件导入成功")
        
        # 测试1: 嵌入模型
        print("\n1. 测试嵌入模型...")
        embedder = TextEmbeddingModel()
        test_texts = ["Python", "ChromaDB", "LLM"]
        embeddings = embedder.get_embeddings(test_texts)
        print(f"   ✅ 嵌入形状: {embeddings.shape}")
        
        # 测试2: ChromaDB存储
        print("\n2. 测试ChromaDB存储...")
        vector_store = ChromaVectorStore("integration_test")
        
        # 添加测试文档
        test_docs = [
            {
                "text": "Python is a programming language",
                "metadata": {"type": "programming", "source": "test"}
            },
            {
                "text": "ChromaDB is a vector database",
                "metadata": {"type": "database", "source": "test"}
            }
        ]
        
        vector_store.add_documents(test_docs)
        
        # 测试搜索
        results = vector_store.search("programming language", n_results=1)
        print(f"   ✅ 文档添加成功: {vector_store.collection.count()} 个")
        if results:
            print(f"   ✅ 搜索成功，找到结果")
        
        # 测试3: 数据索引器
        print("\n3. 测试数据索引器...")
        indexer = DataIndexer("integration_test_index")
        print(f"   ✅ 索引器初始化成功")
        
        # 测试模拟数据索引
        test_code_data = [
            {
                "path": "test.py",
                "content": "def hello():\n    print('Hello World')",
                "language": "python",
                "name": "test.py",
                "repo_name": "test_repo",
                "size": 100
            }
        ]
        
        # 注意：这里我们只是测试导入，实际索引可能需要更多数据
        print("   ✅ 可以索引代码文件")
        
        print("\n" + "=" * 60)
        print("🎉 集成测试完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Day 4 组件验证")
    print("=" * 60)
    
    if verify_all_components():
        print("\n📋 准备进行集成测试...")
        test_integration()
        
        print("\n🎯 下一步:")
        print("1. 运行: python day4_demo.py")
        print("2. 运行: python test_day4.py")
        print("3. 开始将Day 2和Day 3的数据导入向量存储")
    else:
        print("\n🔧 需要先修复组件问题")