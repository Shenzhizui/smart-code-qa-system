#!/usr/bin/env python3
"""
数据集成器 - 将Day 2和Day 3的实际数据集成到向量存储
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = Path(current_dir).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"🔧 项目根目录: {project_root}")

# 设置HuggingFace镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


class DataIntegrator:
    """数据集成器"""
    
    def __init__(self, collection_name: str = "smart_code_qa_system"):
        """初始化数据集成器"""
        self.collection_name = collection_name
        
        try:
            from src.vector_store.indexer import DataIndexer
            self.indexer = DataIndexer(collection_name)
            print(f"✅ 数据索引器初始化成功")
        except ImportError as e:
            print(f"❌ 导入失败: {e}")
            sys.exit(1)
        
        self.data_dir = project_root / "data"
        
        print(f"🔧 初始化数据集成器")
        print(f"   集合名称: {collection_name}")
        print(f"   数据目录: {self.data_dir}")
        
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)
    
    def load_json_file(self, filepath: Path, default_data: List = None) -> List:
        """安全加载JSON文件"""
        if default_data is None:
            default_data = []
        
        if not filepath.exists():
            return default_data
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"   ⚠ 文件为空: {filepath.name}")
                    return default_data
                
                data = json.loads(content)
                
                # 确保返回的是列表
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # 如果是字典，转换为列表
                    return [data]
                else:
                    print(f"   ⚠ 文件格式不是列表或字典: {filepath.name}")
                    return default_data
                    
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {filepath.name} - {e}")
            # 尝试读取原始内容查看问题
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    print(f"   原始内容前100字符: {raw_content[:100]}")
            except:
                pass
            return default_data
        except Exception as e:
            print(f"   ❌ 读取文件失败: {filepath.name} - {e}")
            return default_data
    
    def load_day2_code_data(self, repo_name: str = "smart-code-qa") -> List[Dict[str, Any]]:
        """
        加载Day 2的代码数据
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            代码数据列表
        """
        print(f"\n📁 加载Day 2代码数据...")
        
        # 检查常见的数据文件
        data_files = [
            self.data_dir / "demo2_code.json",
            self.data_dir / "code_files.json",
            self.data_dir / "demo_code_data.json",
        ]
        
        all_code_files = []
        
        for filepath in data_files:
            if filepath.exists():
                print(f"   发现文件: {filepath.name}")
                data = self.load_json_file(filepath)
                
                if data:
                    print(f"   读取到 {len(data)} 条记录")
                    
                    # 转换数据格式
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            # 创建标准化的代码文件数据
                            code_file = {
                                "path": item.get("path", f"file_{i}.py"),
                                "content": item.get("content", "# 示例代码"),
                                "language": item.get("language", self._detect_language(item.get("path", ""))),
                                "name": item.get("name", Path(item.get("path", "")).name),
                                "repo_name": repo_name,
                                "size": len(item.get("content", ""))
                            }
                            all_code_files.append(code_file)
        
        if not all_code_files:
            print("   ⚠ 未找到代码数据文件，创建示例数据...")
            all_code_files = self._create_sample_code_data(repo_name)
        
        print(f"   ✅ 总共加载 {len(all_code_files)} 个代码文件")
        return all_code_files
    
    def load_day3_issue_data(self, repo_name: str = "smart-code-qa") -> List[Dict[str, Any]]:
        """
        加载Day 3的Issue数据
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            Issue数据列表
        """
        print(f"\n📝 加载Day 3 Issue数据...")
        
        data_files = [
            self.data_dir / "demo3_issues.json",
            self.data_dir / "issues.json",
        ]
        
        all_issues = []
        
        for filepath in data_files:
            if filepath.exists():
                print(f"   发现文件: {filepath.name}")
                data = self.load_json_file(filepath)
                
                if data:
                    print(f"   读取到 {len(data)} 条记录")
                    
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            # 创建标准化的Issue数据
                            # 处理user字段
                            user_data = item.get("user", {})
                            if isinstance(user_data, str):
                                user_data = {"login": user_data}
                            elif not isinstance(user_data, dict):
                                user_data = {"login": "unknown"}
                            
                            # 处理labels字段
                            labels = item.get("labels", [])
                            if isinstance(labels, str):
                                labels = [{"name": label.strip()} for label in labels.split(",") if label.strip()]
                            elif not isinstance(labels, list):
                                labels = []
                            
                            issue = {
                                "title": item.get("title", f"Issue {i}"),
                                "body": item.get("body", item.get("description", "问题描述")),
                                "html_url": item.get("html_url", f"https://github.com/{repo_name}/issues/{i}"),
                                "number": item.get("number", i),
                                "state": item.get("state", "open"),
                                "user": user_data,
                                "repo_name": repo_name,
                                "created_at": item.get("created_at", "2024-01-01T00:00:00Z"),
                                "comments": item.get("comments", 0),
                                "labels": labels
                            }
                            all_issues.append(issue)
        
        if not all_issues:
            print("   ⚠ 未找到Issue数据文件，创建示例数据...")
            all_issues = self._create_sample_issue_data(repo_name)
        
        print(f"   ✅ 总共加载 {len(all_issues)} 个Issue")
        return all_issues
    
    def load_day3_pr_data(self, repo_name: str = "smart-code-qa") -> List[Dict[str, Any]]:
        """
        加载Day 3的PR数据
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            PR数据列表
        """
        print(f"\n🔀 加载Day 3 PR数据...")
        
        data_files = [
            self.data_dir / "demo3_prs.json",
            self.data_dir / "prs.json",
        ]
        
        all_prs = []
        
        for filepath in data_files:
            if filepath.exists():
                print(f"   发现文件: {filepath.name}")
                data = self.load_json_file(filepath)
                
                if data:
                    print(f"   读取到 {len(data)} 条记录")
                    
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            # 创建标准化的PR数据
                            # 处理user字段
                            user_data = item.get("user", {})
                            if isinstance(user_data, str):
                                user_data = {"login": user_data}
                            elif not isinstance(user_data, dict):
                                user_data = {"login": "unknown"}
                            
                            # 处理merged字段
                            merged = item.get("merged", False)
                            if isinstance(merged, str):
                                merged = merged.lower() in ["true", "yes", "1"]
                            
                            pr = {
                                "title": item.get("title", f"PR {i}"),
                                "body": item.get("body", item.get("description", "PR描述")),
                                "html_url": item.get("html_url", f"https://github.com/{repo_name}/pull/{i}"),
                                "number": item.get("number", i),
                                "state": item.get("state", "open"),
                                "user": user_data,
                                "repo_name": repo_name,
                                "created_at": item.get("created_at", "2024-01-01T00:00:00Z"),
                                "merged": merged,
                                "comments": item.get("comments", 0)
                            }
                            all_prs.append(pr)
        
        if not all_prs:
            print("   ⚠ 未找到PR数据文件，创建示例数据...")
            all_prs = self._create_sample_pr_data(repo_name)
        
        print(f"   ✅ 总共加载 {len(all_prs)} 个PR")
        return all_prs
    
    def load_readme_data(self, repo_name: str = "smart-code-qa") -> List[Dict[str, Any]]:
        """
        加载README数据
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            README数据列表
        """
        print(f"\n📖 加载README数据...")
        
        readmes = []
        
        # 1. 首先尝试加载项目README.md
        readme_path = project_root / "README.md"
        if readme_path.exists():
            print(f"   发现项目README.md文件")
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    readmes.append({
                        "path": "README.md",
                        "content": content,
                        "repo_name": repo_name
                    })
                print(f"   成功读取项目README.md")
            except Exception as e:
                print(f"   读取README.md失败: {e}")
        
        # 2. 尝试加载数据目录中的README文件
        readme_files = [
            self.data_dir / "readme.json",
            self.data_dir / "repo_info.json"
        ]
        
        for filepath in readme_files:
            if filepath.exists():
                print(f"   发现README数据文件: {filepath.name}")
                data = self.load_json_file(filepath)
                
                if data:
                    for item in data:
                        if isinstance(item, dict):
                            content = item.get("content", item.get("description", ""))
                            if content:
                                readmes.append({
                                    "path": "README.md",
                                    "content": content,
                                    "repo_name": repo_name
                                })
        
        if not readmes:
            print("   ⚠ 未找到README数据，创建示例数据...")
            readmes = self._create_sample_readme_data(repo_name)
        
        print(f"   ✅ 总共加载 {len(readmes)} 个README")
        return readmes
    
    def _detect_language(self, filepath: str) -> str:
        """根据文件扩展名检测编程语言"""
        if not filepath:
            return "unknown"
        
        ext = Path(filepath).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.md': 'markdown',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json'
        }
        
        return language_map.get(ext, 'unknown')
    
    def _create_sample_code_data(self, repo_name: str) -> List[Dict[str, Any]]:
        """创建示例代码数据"""
        print("   创建示例代码数据...")
        
        return [
            {
                "path": "src/main.py",
                "content": "print('Hello World')",
                "language": "python",
                "name": "main.py",
                "repo_name": repo_name,
                "size": 100
            }
        ]
    
    def _create_sample_issue_data(self, repo_name: str) -> List[Dict[str, Any]]:
        """创建示例Issue数据"""
        print("   创建示例Issue数据...")
        
        return [
            {
                "title": "示例Issue",
                "body": "这是一个示例Issue",
                "html_url": f"https://github.com/{repo_name}/issues/1",
                "number": 1,
                "state": "open",
                "user": {"login": "testuser"},
                "repo_name": repo_name,
                "created_at": "2024-01-01T00:00:00Z",
                "comments": 0,
                "labels": []
            }
        ]
    
    def _create_sample_pr_data(self, repo_name: str) -> List[Dict[str, Any]]:
        """创建示例PR数据"""
        print("   创建示例PR数据...")
        
        return [
            {
                "title": "示例PR",
                "body": "这是一个示例PR",
                "html_url": f"https://github.com/{repo_name}/pull/1",
                "number": 1,
                "state": "open",
                "user": {"login": "contributor"},
                "repo_name": repo_name,
                "created_at": "2024-01-01T00:00:00Z",
                "merged": False,
                "comments": 0
            }
        ]
    
    def _create_sample_readme_data(self, repo_name: str) -> List[Dict[str, Any]]:
        """创建示例README数据"""
        print("   创建示例README数据...")
        
        return [
            {
                "path": "README.md",
                "content": "# 示例项目\n\n这是一个示例项目。",
                "repo_name": repo_name
            }
        ]
    
    def integrate_all_data(self, repo_name: str = "smart-code-qa"):
        """集成所有数据"""
        print("\n" + "=" * 60)
        print("🚀 开始集成所有数据")
        print("=" * 60)
        
        try:
            # 1. 加载数据
            print("\n📥 加载数据...")
            
            code_files = self.load_day2_code_data(repo_name)
            issues = self.load_day3_issue_data(repo_name)
            prs = self.load_day3_pr_data(repo_name)
            readmes = self.load_readme_data(repo_name)
            
            print(f"\n📊 数据统计:")
            print(f"   代码文件: {len(code_files)} 个")
            print(f"   Issues: {len(issues)} 个")
            print(f"   Pull Requests: {len(prs)} 个")
            print(f"   README文件: {len(readmes)} 个")
            total = len(code_files) + len(issues) + len(prs) + len(readmes)
            print(f"   总计: {total} 个文档")
            
            # 2. 索引数据
            print("\n📤 索引数据到向量存储...")
            
            # 索引代码文件
            if code_files:
                print("   索引代码文件...")
                self.indexer.index_code_files(code_files)
                print("   ✅ 代码文件索引完成")
            
            # 索引Issues
            if issues:
                print("   索引Issues...")
                self.indexer.index_issues(issues)
                print("   ✅ Issues索引完成")
            
            # 索引PRs
            if prs:
                print("   索引Pull Requests...")
                self.indexer.index_pull_requests(prs)
                print("   ✅ Pull Requests索引完成")
            
            # 索引README
            if readmes:
                print("   索引README文件...")
                # 使用临时方法添加README
                for readme in readmes:
                    doc = {
                        "text": f"README文件: {readme.get('path', 'README.md')}\n内容:\n{readme.get('content', '')[:500]}",
                        "metadata": {
                            "type": "readme",
                            "source": readme.get('path', 'README.md'),
                            "repository": repo_name,
                            "file_name": "README.md"
                        }
                    }
                    # 直接使用向量存储
                    self.indexer.vector_store.add_documents([doc])
                print("   ✅ README文件索引完成")
            
            # 3. 验证集成
            print("\n🔍 验证数据集成...")
            vector_store = self.indexer.get_vector_store()
            info = vector_store.get_collection_info()
            
            print(f"\n✅ 数据集成完成！")
            print(f"   集合名称: {info['collection_name']}")
            print(f"   总文档数: {info['document_count']}")
            
            # 4. 简单搜索测试
            print("\n🧪 简单搜索测试...")
            test_queries = ["代码", "Issue", "PR", "README"]
            
            for query in test_queries:
                results = vector_store.search(query, n_results=1)
                if results:
                    print(f"   搜索 '{query}': 找到 {len(results)} 个结果")
                else:
                    print(f"   搜索 '{query}': 无结果")
            
            # 5. 保存集成信息
            print("\n💾 保存集成信息...")
            integration_info = {
                "collection_name": self.collection_name,
                "repo_name": repo_name,
                "code_files_count": len(code_files),
                "issues_count": len(issues),
                "prs_count": len(prs),
                "readmes_count": len(readmes),
                "total_documents": info['document_count'],
                "integration_time": datetime.now().isoformat()
            }
            
            info_file = self.data_dir / f"integration_{repo_name.replace('/', '_')}.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(integration_info, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 集成信息已保存到: {info_file}")
            
            print("\n" + "=" * 60)
            print("🎉 数据集成完成！")
            print("=" * 60)
            
            return integration_info
            
        except Exception as e:
            print(f"\n❌ 数据集成过程中出错: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """主函数"""
    print("🤖 数据集成器 - 修复版")
    print("=" * 60)
    
    try:
        # 先创建集成器
        integrator = DataIntegrator(collection_name="integrated_data")
        
        # 集成数据
        result = integrator.integrate_all_data(repo_name="smart-code-qa")
        
        print("\n📋 集成完成！")
        print(f"   总文档数: {result['total_documents']}")
        print("\n🚀 下一步:")
        print("1. 查看向量存储: chroma_data/ 目录")
        print("2. 运行问答测试")
        print("3. 开始Day 5开发")
        
    except Exception as e:
        print(f"\n❌ 集成失败: {e}")
        print("\n💡 调试建议:")
        print("1. 检查data目录是否有数据文件")
        print("2. 手动创建示例数据文件")
        print("3. 运行简化测试")
        
        # 提供创建示例数据的选项
        create_sample = input("\n是否创建示例数据文件？(y/n): ").strip().lower()
        if create_sample == 'y':
            create_sample_data()
            print("✅ 示例数据已创建，请重新运行集成器")


def create_sample_data():
    """创建示例数据文件"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 创建代码数据
    code_data = [
        {
            "path": "src/main.py",
            "content": "def main():\n    print('Hello World')",
            "language": "python",
            "name": "main.py",
            "repo_name": "test-repo",
            "size": 50
        }
    ]
    
    with open(data_dir / "demo2_code.json", "w", encoding="utf-8") as f:
        json.dump(code_data, f, indent=2)
    
    # 创建Issue数据
    issue_data = [
        {
            "title": "测试Issue",
            "body": "这是一个测试Issue",
            "html_url": "https://github.com/test/issues/1",
            "number": 1,
            "state": "open",
            "user": {"login": "testuser"},
            "repo_name": "test-repo",
            "created_at": "2024-01-01T00:00:00Z",
            "comments": 0,
            "labels": []
        }
    ]
    
    with open(data_dir / "demo3_issues.json", "w", encoding="utf-8") as f:
        json.dump(issue_data, f, indent=2)
    
    # 创建PR数据
    pr_data = [
        {
            "title": "测试PR",
            "body": "这是一个测试PR",
            "html_url": "https://github.com/test/pull/1",
            "number": 1,
            "state": "open",
            "user": {"login": "contributor"},
            "repo_name": "test-repo",
            "created_at": "2024-01-01T00:00:00Z",
            "merged": False,
            "comments": 0
        }
    ]
    
    with open(data_dir / "demo3_prs.json", "w", encoding="utf-8") as f:
        json.dump(pr_data, f, indent=2)
    
    print("示例数据文件已创建在 data/ 目录")


if __name__ == "__main__":
    main()