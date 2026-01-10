"""
文本嵌入模型模块
使用 sentence-transformers 库，支持离线模式和镜像源
"""
import os
import sys
from typing import List, Union
import numpy as np

# ============ 关键设置：强制使用镜像源 ============
# 必须在导入任何 huggingface 相关模块之前设置
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 添加当前目录到路径，确保可以导入其他模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("  sentence-transformers 不可用，将使用离线模式")


class TextEmbeddingModel:
    """文本嵌入模型类"""
    
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):
        """
        初始化嵌入模型
        
        Args:
            model_name: 模型名称，默认使用小型英文模型
                        也可以使用：
                        - 'BAAI/bge-small-zh' (中文优化)
                        - 'all-MiniLM-L6-v2' (英文)
                        - 'paraphrase-multilingual-MiniLM-L12-v2' (多语言)
        """
        self.model_name = model_name
        
        print(f"正在加载嵌入模型: {model_name}")
        print(f"使用镜像源: {os.environ.get('HF_ENDPOINT', '默认')}")
        
        # 检查模型是否在本地缓存中
        self._check_local_cache()
        
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # 尝试加载模型
                self.model = SentenceTransformer(
                    model_name,
                    cache_folder="./models",
                    device='cpu'
                )
                print(f"  模型加载成功！")
                
                # 测试获取维度
                test_embedding = self.model.encode(["测试文本"])
                self.dimensions = test_embedding.shape[1]
                print(f"  嵌入维度: {self.dimensions}")
            else:
                raise ImportError("sentence-transformers 未安装")
                
        except Exception as e:
            print(f"  模型加载失败: {e}")
            print("\n 创建离线回退模型...")
            self._create_fallback_model()
    
    def _check_local_cache(self):
        """检查本地模型缓存"""
        cache_dir = "./models"
        if os.path.exists(cache_dir):
            # 检查是否有已下载的模型
            import glob
            model_pattern = f"models--sentence-transformers--{self.model_name.replace('/', '--')}"
            model_path = os.path.join(cache_dir, model_pattern)
            
            if os.path.exists(model_path):
                print(f"  发现本地缓存模型: {model_path}")
                return model_path
            else:
                print(f"  本地缓存中没有模型: {self.model_name}")
        else:
            print(f"  模型缓存目录不存在: {cache_dir}")
            os.makedirs(cache_dir, exist_ok=True)
            print(f"  已创建缓存目录: {cache_dir}")
        
        return None
    
    def _create_fallback_model(self):
        """创建离线回退模型"""
        print(" 使用回退模型（离线模式）")
        
        class FallbackModel:
            def __init__(self, dim=384):
                self.dim = dim
                import numpy as np
                self.np = np
            
            def encode(self, texts, **kwargs):
                if isinstance(texts, str):
                    texts = [texts]
                
                embeddings = []
                for text in texts:
                    # 基于文本的确定性伪随机向量
                    import hashlib
                    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
                    self.np.random.seed(seed)
                    vec = self.np.random.randn(self.dim)
                    # 归一化
                    norm = self.np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    embeddings.append(vec)
                
                return self.np.array(embeddings)
        
        self.model = FallbackModel(384)
        self.dimensions = 384
        self.model_name = "fallback-offline-model"
        print("  回退模型创建成功")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        获取单个文本的嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        return self.model.encode(text)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        获取多个文本的嵌入向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            嵌入向量矩阵
        """
        return self.model.encode(texts)
    
    def compute_similarity(self, query: str, sentences: List[str]) -> List[float]:
        """
        计算查询文本与多个句子的相似度
        
        Args:
            query: 查询文本
            sentences: 句子列表
            
        Returns:
            相似度列表
        """
        # 获取嵌入
        query_embedding = self.get_embedding(query)
        sentence_embeddings = self.get_embeddings(sentences)
        
        # 计算余弦相似度
        similarities = []
        query_norm = np.linalg.norm(query_embedding)
        
        for emb in sentence_embeddings:
            sentence_norm = np.linalg.norm(emb)
            if query_norm > 0 and sentence_norm > 0:
                similarity = np.dot(query_embedding, emb) / (query_norm * sentence_norm)
                similarities.append(float(similarity))
            else:
                similarities.append(0.0)
        
        return similarities


# 测试函数
def test_embedding_model():
    """测试嵌入模型"""
    print(" 测试嵌入模型")
    print("=" * 60)
    
    try:
        embedder = TextEmbeddingModel()
        
        # 测试中文文本
        texts = ["Python编程语言", "向量数据库ChromaDB", "大型语言模型LLM"]
        embeddings = embedder.get_embeddings(texts)
        
        print(f"  模型: {embedder.model_name}")
        print(f"  维度: {embedder.dimensions}")
        print(f"  测试文本: {texts}")
        print(f"  嵌入形状: {embeddings.shape}")
        
        # 测试相似度
        query = "编程语言Python"
        similarities = embedder.compute_similarity(query, texts)
        
        print(f"\n  相似度测试:")
        print(f"   查询: '{query}'")
        for text, sim in zip(texts, similarities):
            print(f"   '{text}': {sim:.4f}")
        
        return True
        
    except Exception as e:
        print(f"  测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_model():
    """测试嵌入模型 - 供外部调用"""
    print(" 测试嵌入模型（外部调用）")
    print("=" * 50)
    
    try:
        embedder = TextEmbeddingModel()
        
        print(f"  模型: {embedder.model_name}")
        print(f"  维度: {embedder.dimensions}")
        
        # 测试基本功能
        texts = ["测试文本1", "测试文本2", "测试文本3"]
        embeddings = embedder.get_embeddings(texts)
        
        print(f"  批量处理 {len(texts)} 个文本")
        print(f"  嵌入形状: {embeddings.shape}")
        
        # 测试相似度
        query = "测试"
        similarities = embedder.compute_similarity(query, texts)
        
        print(f"  查询: '{query}'")
        for i, (text, sim) in enumerate(zip(texts, similarities), 1):
            print(f"   文本{i}: '{text}' - 相似度: {sim:.4f}")
        
        print("\n  嵌入模型测试完成！")
        return True
        
    except Exception as e:
        print(f"  测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# 在文件末尾添加导出
__all__ = ["TextEmbeddingModel", "test_embedding_model"]

if __name__ == "__main__":
    test_embedding_model()