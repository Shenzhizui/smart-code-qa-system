"""
文本嵌入模型模块 - 最终版
使用 sentence-transformers 库
"""
import os
import sys
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# ============ 关键设置：强制使用镜像源 ============
# 必须在导入任何 huggingface 相关模块之前设置
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 如果需要代理，可以在这里设置（如果有的话）
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

print(f"🔧 嵌入模型设置: HF_ENDPOINT={os.environ.get('HF_ENDPOINT')}")


class TextEmbeddingModel:
    """文本嵌入模型类"""
    
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):
        """
        初始化嵌入模型
        
        Args:
            model_name: 模型名称，默认使用小型英文模型
        """
        self.model_name = model_name
        
        print(f"🔧 正在加载嵌入模型: {model_name}")
        print(f"   使用镜像源: {os.environ.get('HF_ENDPOINT', '默认')}")
        
        try:
            # 加载模型，指定缓存目录
            self.model = SentenceTransformer(
                model_name,
                cache_folder="./models",  # 本地缓存目录
                device='cpu'  # 使用CPU
            )
            print(f"✅ 模型加载成功！")
            
            # 测试模型获取维度
            test_embedding = self.model.encode(["测试文本"])
            self.dimensions = test_embedding.shape[1]
            print(f"✅ 嵌入维度: {self.dimensions}")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("\n🔄 检查模型是否已下载...")
            
            # 检查模型是否已在缓存中
            model_path = f"./models/models--sentence-transformers--{model_name.replace('/', '--')}"
            if os.path.exists(model_path):
                print(f"✅ 发现本地缓存模型: {model_path}")
                print("🔄 尝试从本地缓存加载...")
                try:
                    # 尝试从本地路径加载
                    self.model = SentenceTransformer(model_path, device='cpu')
                    test_embedding = self.model.encode(["测试文本"])
                    self.dimensions = test_embedding.shape[1]
                    print(f"✅ 从本地缓存加载成功！")
                    print(f"✅ 嵌入维度: {self.dimensions}")
                    return
                except Exception as e2:
                    print(f"❌ 本地缓存加载失败: {e2}")
            
            print("🔄 创建离线回退模型...")
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """创建离线回退模型"""
        print("⚠️ 使用回退模型（离线模式）")
        
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
        print("✅ 回退模型创建成功")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """获取单个文本的嵌入向量"""
        return self.model.encode(text)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """获取多个文本的嵌入向量"""
        return self.model.encode(texts)
    
    def compute_similarity(self, query: str, sentences: List[str]) -> List[float]:
        """计算相似度"""
        query_embedding = self.get_embedding(query)
        sentence_embeddings = self.get_embeddings(sentences)
        
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


# 测试代码
if __name__ == "__main__":
    print("🧪 测试嵌入模型...")
    embedder = TextEmbeddingModel()
    
    # 测试中文文本
    texts = ["Python编程语言", "向量数据库ChromaDB", "大型语言模型LLM"]
    embeddings = embedder.get_embeddings(texts)
    
    print(f"✅ 模型: {embedder.model_name}")
    print(f"✅ 维度: {embedder.dimensions}")
    print(f"✅ 测试文本: {texts}")
    print(f"✅ 嵌入形状: {embeddings.shape}")