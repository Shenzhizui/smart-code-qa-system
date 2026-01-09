"""
健壮的嵌入模型 - 自动处理网络问题
"""
import os
import sys
from typing import List, Union
import numpy as np

# 强制设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

class RobustEmbeddingModel:
    """健壮的嵌入模型，自动处理各种异常"""
    
    def __init__(self, model_name: str = None):
        """
        初始化嵌入模型
        
        Args:
            model_name: 模型名称或路径，None则自动选择
        """
        self.model = None
        self.model_name = model_name or self._select_best_model()
        self.dimensions = 384  # 默认维度
        
        print(f"🔧 初始化嵌入模型: {self.model_name}")
        
        try:
            self._load_model()
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("🔄 创建离线回退模型...")
            self._create_fallback_model()
    
    def _select_best_model(self):
        """选择最佳可用模型"""
        # 优先级：本地模型 > 小型模型 > 中文模型
        local_models = [
            "./models/paraphrase-MiniLM-L3-v2",
            "./models/text2vec-base-chinese", 
            "./models/minimal_model"
        ]
        
        import os
        for model_path in local_models:
            if os.path.exists(model_path):
                print(f"✅ 发现本地模型: {model_path}")
                return model_path
        
        # 没有本地模型，选择小型在线模型
        return "paraphrase-MiniLM-L3-v2"
    
    def _load_model(self):
        """加载模型"""
        from sentence_transformers import SentenceTransformer
        
        print(f"📥 正在加载模型: {self.model_name}")
        
        # 设置重试和超时
        import requests
        import urllib3
        
        # 禁用警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 加载模型
        self.model = SentenceTransformer(
            self.model_name,
            cache_folder="./models",
            device='cpu'
        )
        
        # 测试获取维度
        test_embedding = self.model.encode(["test"])
        self.dimensions = test_embedding.shape[1]
        
        print(f"✅ 模型加载成功！")
        print(f"✅ 嵌入维度: {self.dimensions}")
    
    def _create_fallback_model(self):
        """创建回退模型"""
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
    
    def get_embedding(self, text: str) -> np.ndarray:
        """获取单个文本嵌入"""
        return self.model.encode(text)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """获取批量文本嵌入"""
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

# 主函数：测试模型
def test_robust_model():
    """测试健壮模型"""
    print("🧪 测试健壮嵌入模型")
    print("=" * 50)
    
    model = RobustEmbeddingModel()
    
    # 测试
    texts = ["hello world", "this is a test", "vector database"]
    embeddings = model.get_embeddings(texts)
    
    print(f"✅ 模型名称: {model.model_name}")
    print(f"✅ 嵌入维度: {model.dimensions}")
    print(f"✅ 批量处理: {len(texts)} 个文本")
    print(f"✅ 嵌入形状: {embeddings.shape}")
    
    # 测试相似度
    query = "test world"
    sentences = ["hello world", "database test", "unrelated topic"]
    
    similarities = model.compute_similarity(query, sentences)
    
    print(f"\n✅ 相似度测试:")
    print(f"   查询: '{query}'")
    for i, (sentence, sim) in enumerate(zip(sentences, similarities), 1):
        print(f"   句子{i}: '{sentence}' - 相似度: {sim:.4f}")
    
    return model

if __name__ == "__main__":
    test_robust_model()