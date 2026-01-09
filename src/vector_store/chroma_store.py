"""
ChromaDB向量存储模块
"""
import os
import sys
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  chromadb 不可用")

try:
    from .embedding import TextEmbeddingModel
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from src.vector_store.embedding import TextEmbeddingModel


class ChromaVectorStore:
    """ChromaDB向量存储类"""
    
    def __init__(self, collection_name: str = "code_repository", persist_dir: str = None):
        """
        初始化向量存储
        
        Args:
            collection_name: 集合名称
            persist_dir: 持久化目录路径
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb 未安装，请运行: pip install chromadb")
        
        # 设置持久化目录
        if persist_dir is None:
            # 使用项目根目录下的 chroma_data 目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.persist_dir = os.path.join(project_root, "chroma_data")
        else:
            self.persist_dir = persist_dir
            
        # 确保目录存在
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # 初始化嵌入模型
        self.embedder = TextEmbeddingModel()
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(
                anonymized_telemetry=False,  # 禁用遥测
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection(collection_name)
        
        print(f"✅ ChromaDB向量存储初始化完成")
        print(f"   存储路径: {self.persist_dir}")
        print(f"   集合名称: {collection_name}")
        print(f"   嵌入维度: {self.embedder.dimensions}")
    
    def _get_or_create_collection(self, name: str):
        """获取或创建集合"""
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(name=name)
            print(f"📂 加载现有集合: {name}")
            return collection
        except Exception:
            # 创建新集合
            print(f"🆕 创建新集合: {name}")
            return self.client.create_collection(
                name=name,
                metadata={"description": "智能代码仓库问答系统向量存储"},
                embedding_function=None  # 我们使用自己的嵌入函数
            )
    
    def _generate_id(self, content: str, source: str) -> str:
        """
        为文档生成唯一ID
        
        Args:
            content: 文档内容
            source: 文档来源（如文件路径、Issue URL等）
            
        Returns:
            唯一ID字符串
        """
        # 使用内容哈希和源信息生成ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        return f"{content_hash}_{source_hash}"
    
    def add_documents(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        """
        添加文档到向量存储
        
        Args:
            documents: 文档列表，每个文档是字典，包含：
                - text: 文本内容
                - metadata: 元数据（如文件路径、类型等）
            batch_size: 批量添加大小
        """
        if not documents:
            print("⚠️ 没有文档可添加")
            return
        
        print(f"📥 开始添加 {len(documents)} 个文档到向量存储...")
        
        # 分批处理
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            print(f"   处理批次 {batch_num}/{total_batches} ({len(batch)} 个文档)")
            
            # 准备数据
            texts = []
            metadatas = []
            ids = []
            
            for doc in batch:
                text = doc.get("text", "").strip()
                metadata = doc.get("metadata", {})
                
                if not text:
                    continue
                
                # 生成ID
                source = metadata.get("source", "unknown")
                doc_id = self._generate_id(text, source)
                
                # 添加时间戳
                metadata["added_at"] = datetime.now().isoformat()
                
                texts.append(text)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            if texts:
                # 获取嵌入向量
                embeddings = self.embedder.get_embeddings(texts)
                
                # 添加到集合
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                print(f"   ✅ 批次 {batch_num} 添加成功")
        
        print(f"🎉 所有文档添加完成！共添加 {len(documents)} 个文档")
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            搜索结果列表
        """
        # 获取查询嵌入
        query_embedding = self.embedder.get_embedding(query)
        
        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                distance = results["distances"][0][i]
                # 计算相似度，确保在0-1范围内
                # ChromaDB返回的是距离（欧氏距离），需要转换为相似度
                if isinstance(distance, (int, float)):
                    # 欧氏距离转相似度：相似度 = 1 / (1 + 距离)
                    score = 1.0 / (1.0 + float(distance))
                    # 确保在0-1之间
                    score = max(0.0, min(1.0, score))
                else:
                    score = 0.0
                
                result = {
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": distance,
                    "score": score  # 使用计算后的相似度
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        count = self.collection.count()
        
        return {
            "collection_name": self.collection.name,
            "document_count": count,
            "embedding_dimension": self.embedder.dimensions
        }
    
    def reset_collection(self, collection_name: str = None):
        """重置集合（清空数据）"""
        if collection_name:
            self.collection = self._get_or_create_collection(collection_name)
        else:
            self.collection.delete()
            self.collection = self._get_or_create_collection(self.collection.name)
        print("🔄 集合已重置")


# 测试函数
def test_chroma_store():
    """测试ChromaDB存储"""
    print("🧪 测试ChromaDB向量存储")
    print("=" * 60)
    
    try:
        # 创建测试集合
        store = ChromaVectorStore("test_collection")
        
        # 添加测试文档
        test_documents = [
            {
                "text": "Python是一种高级编程语言",
                "metadata": {"type": "language", "source": "test"}
            },
            {
                "text": "ChromaDB是向量数据库",
                "metadata": {"type": "database", "source": "test"}
            },
            {
                "text": "机器学习是人工智能的分支",
                "metadata": {"type": "ai", "source": "test"}
            }
        ]
        
        store.add_documents(test_documents)
        
        # 测试搜索
        query = "编程语言"
        results = store.search(query, n_results=2)
        
        print(f"✅ 查询: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                doc_preview = result['document']
                if len(doc_preview) > 50:
                    doc_preview = doc_preview[:50] + "..."
                
                print(f"   结果{i}: {doc_preview}")
                print(f"       相似度: {result['score']:.4f}")
                print(f"       类型: {result['metadata'].get('type', 'unknown')}")
        else:
            print("   未找到相关结果")
        
        # 获取集合信息
        info = store.get_collection_info()
        print(f"\n📊 集合信息:")
        print(f"   名称: {info['collection_name']}")
        print(f"   文档数: {info['document_count']}")
        print(f"   维度: {info['embedding_dimension']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_chroma_store()