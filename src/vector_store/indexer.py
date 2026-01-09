"""
数据索引器 - 将GitHub数据转换为向量存储格式
"""
import os
import sys
import json
from typing import List, Dict, Any

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from .chroma_store import ChromaVectorStore
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from src.vector_store.chroma_store import ChromaVectorStore


class DataIndexer:
    """数据索引器，负责将GitHub数据转换为向量存储格式"""
    
    def __init__(self, collection_name: str = "code_repository"):
        """
        初始化索引器
        
        Args:
            collection_name: 集合名称
        """
        self.vector_store = ChromaVectorStore(collection_name)
        print(f"✅ 数据索引器初始化完成")
        print(f"   集合名称: {collection_name}")
    
    def index_code_files(self, code_files_data: List[Dict[str, Any]]):
        """
        索引代码文件数据
        
        Args:
            code_files_data: 代码文件数据列表
        """
        if not code_files_data:
            print("⚠️ 没有代码文件数据可索引")
            return
        
        print(f"📁 开始索引 {len(code_files_data)} 个代码文件...")
        
        documents = []
        for file_data in code_files_data:
            # 构建文档
            text = self._prepare_code_text(file_data)
            metadata = {
                "type": "code_file",
                "source": file_data.get("path", "unknown"),
                "language": file_data.get("language", "unknown"),
                "file_name": file_data.get("name", "unknown"),
                "repository": file_data.get("repo_name", "unknown"),
                "size": file_data.get("size", 0)
            }
            
            documents.append({
                "text": text,
                "metadata": metadata
            })
        
        # 添加到向量存储
        self.vector_store.add_documents(documents)
        print(f"✅ 代码文件索引完成: {len(documents)} 个文件")
    
    def index_issues(self, issues_data: List[Dict[str, Any]]):
        """
        索引Issue数据
        
        Args:
            issues_data: Issue数据列表
        """
        if not issues_data:
            print("⚠️ 没有Issue数据可索引")
            return
        
        print(f"📝 开始索引 {len(issues_data)} 个Issues...")
        
        documents = []
        for issue_data in issues_data:
            # 构建文档
            text = self._prepare_issue_text(issue_data)
            metadata = {
                "type": "issue",
                "source": issue_data.get("html_url", "unknown"),
                "issue_number": issue_data.get("number", 0),
                "state": issue_data.get("state", "unknown"),
                "creator": issue_data.get("user", {}).get("login", "unknown"),
                "repository": issue_data.get("repo_name", "unknown"),
                "created_at": issue_data.get("created_at", ""),
                "comments_count": issue_data.get("comments", 0)
            }
            
            # 添加标签信息
            if issue_data.get("labels"):
                metadata["labels"] = json.dumps([label.get("name", "") for label in issue_data["labels"]])
            
            documents.append({
                "text": text,
                "metadata": metadata
            })
        
        # 添加到向量存储
        self.vector_store.add_documents(documents)
        print(f"✅ Issues索引完成: {len(documents)} 个Issue")
    
    def index_pull_requests(self, prs_data: List[Dict[str, Any]]):
        """
        索引Pull Request数据
        
        Args:
            prs_data: PR数据列表
        """
        if not prs_data:
            print("⚠️ 没有PR数据可索引")
            return
        
        print(f"🔀 开始索引 {len(prs_data)} 个Pull Requests...")
        
        documents = []
        for pr_data in prs_data:
            # 构建文档
            text = self._prepare_pr_text(pr_data)
            metadata = {
                "type": "pull_request",
                "source": pr_data.get("html_url", "unknown"),
                "pr_number": pr_data.get("number", 0),
                "state": pr_data.get("state", "unknown"),
                "creator": pr_data.get("user", {}).get("login", "unknown"),
                "repository": pr_data.get("repo_name", "unknown"),
                "created_at": pr_data.get("created_at", ""),
                "merged": "true" if pr_data.get("merged", False) else "false",
                "comments_count": pr_data.get("comments", 0)
            }
            
            documents.append({
                "text": text,
                "metadata": metadata
            })
        
        # 添加到向量存储
        self.vector_store.add_documents(documents)
        print(f"✅ Pull Requests索引完成: {len(documents)} 个PR")
    
    def index_readme_files(self, readme_data: List[Dict[str, Any]]):
        """
        索引README文件数据
        
        Args:
            readme_data: README数据列表
        """
        if not readme_data:
            print("⚠️ 没有README数据可索引")
            return
        
        print(f"📖 开始索引 {len(readme_data)} 个README文件...")
        
        documents = []
        for readme in readme_data:
            text = self._prepare_readme_text(readme)
            metadata = {
                "type": "readme",
                "source": readme.get("path", "unknown"),
                "repository": readme.get("repo_name", "unknown"),
                "file_name": "README.md"
            }
            
            documents.append({
                "text": text,
                "metadata": metadata
            })
        
        self.vector_store.add_documents(documents)
        print(f"✅ README文件索引完成: {len(documents)} 个文件")
    
    def _prepare_code_text(self, file_data: Dict[str, Any]) -> str:
        """准备代码文件文本"""
        content = file_data.get("content", "")
        language = file_data.get("language", "")
        path = file_data.get("path", "")
        
        # 构建有意义的文本表示
        text = f"代码文件: {path}\n"
        text += f"编程语言: {language}\n"
        if content:
            text += f"内容:\n{content[:1000]}\n"  # 限制内容长度
        else:
            text += "内容: [空]\n"
        
        return text
    
    def _prepare_issue_text(self, issue_data: Dict[str, Any]) -> str:
        """准备Issue文本"""
        title = issue_data.get("title", "")
        body = issue_data.get("body", "")
        labels = issue_data.get("labels", [])
        
        # 构建有意义的文本表示
        text = f"Issue: {title}\n"
        
        # 添加标签信息
        if labels:
            label_names = [label.get("name", "") for label in labels]
            text += f"标签: {', '.join(label_names)}\n"
        
        if body:
            text += f"描述:\n{body[:2000]}\n"  # 限制内容长度
        else:
            text += "描述: [空]\n"
        
        return text
    
    def _prepare_pr_text(self, pr_data: Dict[str, Any]) -> str:
        """准备Pull Request文本"""
        title = pr_data.get("title", "")
        body = pr_data.get("body", "")
        
        # 构建有意义的文本表示
        text = f"Pull Request: {title}\n"
        
        if body:
            text += f"描述:\n{body[:2000]}\n"  # 限制内容长度
        else:
            text += "描述: [空]\n"
        
        return text
    
    def _prepare_readme_text(self, readme_data: Dict[str, Any]) -> str:
        """准备README文本"""
        content = readme_data.get("content", "")
        path = readme_data.get("path", "")
        
        text = f"README文件: {path}\n"
        if content:
            text += f"内容:\n{content[:3000]}\n"  # 限制内容长度
        else:
            text += "内容: [空]\n"
        
        return text
    
    def get_vector_store(self) -> ChromaVectorStore:
        """获取向量存储实例"""
        return self.vector_store


# 测试函数
def test_data_indexer():
    """测试数据索引器"""
    print("🧪 测试数据索引器")
    print("=" * 60)
    
    try:
        # 创建索引器
        indexer = DataIndexer("test_indexer")
        
        # 模拟代码文件数据
        code_files = [
            {
                "path": "src/main.py",
                "content": "def main():\n    print('Hello World')",
                "language": "python",
                "name": "main.py",
                "repo_name": "test_repo",
                "size": 100
            }
        ]
        
        # 模拟Issue数据
        issues = [
            {
                "title": "测试Issue",
                "body": "这是一个测试Issue",
                "html_url": "https://github.com/test/repo/issues/1",
                "number": 1,
                "state": "open",
                "user": {"login": "test_user"},
                "repo_name": "test_repo",
                "created_at": "2024-01-01T00:00:00Z",
                "comments": 0,
                "labels": [{"name": "bug"}, {"name": "test"}]
            }
        ]
        
        # 模拟PR数据
        prs = [
            {
                "title": "测试PR",
                "body": "这是一个测试Pull Request",
                "html_url": "https://github.com/test/repo/pull/1",
                "number": 1,
                "state": "open",
                "user": {"login": "test_user"},
                "repo_name": "test_repo",
                "created_at": "2024-01-01T00:00:00Z",
                "merged": False,
                "comments": 0
            }
        ]
        
        # 测试索引
        print("1. 索引代码文件...")
        indexer.index_code_files(code_files)
        
        print("\n2. 索引Issues...")
        indexer.index_issues(issues)
        
        print("\n3. 索引Pull Requests...")
        indexer.index_pull_requests(prs)
        
        # 获取向量存储
        vector_store = indexer.get_vector_store()
        info = vector_store.get_collection_info()
        
        print(f"\n📊 索引完成:")
        print(f"   集合名称: {info['collection_name']}")
        print(f"   文档数量: {info['document_count']}")
        
        # 测试搜索
        print("\n4. 测试搜索...")
        results = vector_store.search("测试Issue", n_results=1)
        if results:
            print(f"✅ 搜索成功，找到 {len(results)} 个结果")
        else:
            print("⚠️  未找到结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_data_indexer()