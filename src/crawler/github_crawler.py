#!/usr/bin/env python3
"""
GitHub爬取模块 - Day 1基础版本
修复导入问题的完整版本
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# ========== 修复导入路径 ==========
# 添加项目根目录到Python路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # src/crawler -> src -> project_root
sys.path.insert(0, str(project_root))

# 现在可以导入config模块
try:
    from config.settings import GITHUB_TOKEN
    print(f"✅ 从config.settings导入成功")
except ImportError as e:
    print(f"❌ 导入config.settings失败: {e}")
    print("尝试直接从环境变量读取...")
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

import logging
from typing import Optional
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RepositoryInfo:
    """仓库信息数据类"""
    name: str
    full_name: str
    description: str
    owner: str
    url: str
    stars: int
    forks: int
    created_at: str
    updated_at: str
    language: str

@dataclass
class GitHubFile:
    """GitHub文件数据类"""
    path: str
    name: str
    type: str  # 'file' 或 'dir'
    size: int
    sha: str
    url: str
    download_url: Optional[str] = None

@dataclass  
class CodeFile:
    """代码文件数据类"""
    path: str
    name: str
    content: str
    language: str
    size: int
    sha: str
    lines: int = 0

class GitHubCrawler:
    """GitHub仓库爬取器"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        if not self.token or self.token == "your_github_token_here":
            logger.error("请配置GITHUB_TOKEN！")
            logger.error("编辑 .env 文件，设置你的GitHub Token")
            self.github = None
            return
        
        try:
            from github import Github
            self.github = Github(self.token)
            logger.info("✅ GitHub API 初始化成功")
        except ImportError:
            logger.error("请安装PyGithub: pip install PyGithub==2.1.1")
            self.github = None
        except Exception as e:
            logger.error(f"GitHub初始化失败: {e}")
            self.github = None
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.github is not None
    
    def test_connection(self) -> bool:
        """测试GitHub连接"""
        if not self.is_connected():
            return False
        
        try:
            user = self.github.get_user()
            logger.info(f"✅ GitHub连接成功: {user.login}")
            return True
        except Exception as e:
            logger.error(f"❌ GitHub连接失败: {e}")
            return False
    
    def get_repository_info(self, repo_name: str) -> Optional[RepositoryInfo]:
        """获取仓库信息"""
        if not self.is_connected():
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            
            info = RepositoryInfo(
                name=repo.name,
                full_name=repo.full_name,
                description=repo.description or "无描述",
                owner=repo.owner.login,
                url=repo.html_url,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                created_at=str(repo.created_at),
                updated_at=str(repo.updated_at),
                language=repo.language or "未知"
            )
            
            logger.info(f"✅ 获取仓库信息成功: {repo.full_name}")
            return info
            
        except Exception as e:
            logger.error(f"❌ 获取仓库失败 {repo_name}: {e}")
            return None
    
    def get_readme(self, repo_name: str) -> Optional[str]:
        """获取README文件"""
        if not self.is_connected():
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8')
            logger.info(f"✅ 找到README文件")
            return content
        except:
            logger.warning("⚠ 未找到README文件")
            return None
        
    def get_directory_contents(self, repo_name: str, path: str = "") -> List[GitHubFile]:
        """
        获取目录下的文件和子目录列表
        Args:
            repo_name: 仓库名称（格式：owner/repo）
            path: 目录路径，空字符串表示根目录
            
        Returns:
            文件和目录列表
        """
        if not self.is_connected():
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            contents = repo.get_contents(path)
            
            files = []
            for item in contents:
                github_file = GitHubFile(
                    path=item.path,
                    name=item.name,
                    type=item.type,
                    size=item.size if hasattr(item, 'size') else 0,
                    sha=item.sha,
                    url=item.html_url,
                    download_url=item.download_url if hasattr(item, 'download_url') else None
                )
                files.append(github_file)
            
            logger.info(f"获取目录内容成功: {path or '根目录'} ({len(files)}个条目)")
            return files
            
        except Exception as e:
            logger.error(f"获取目录内容失败 {repo_name}/{path}: {e}")
            return []
    
    def get_file_content(self, repo_name: str, file_path: str) -> Optional[str]:
        """
        获取文件内容
        
        Args:
            repo_name: 仓库名称
            file_path: 文件路径
            
        Returns:
            文件内容字符串，失败返回None
        """
        if not self.is_connected():
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            file = repo.get_contents(file_path)
            
            # GitHub API返回的内容可能是base64编码的
            if hasattr(file, 'content'):
                if file.encoding == "base64":
                    import base64
                    content = base64.b64decode(file.content).decode('utf-8')
                else:
                    content = file.content
            else:
                content = file.decoded_content.decode('utf-8')
            
            logger.info(f"获取文件成功: {file_path} ({len(content)} 字符)")
            return content
            
        except Exception as e:
            logger.error(f"获取文件失败 {file_path}: {e}")
            return None
    
    def get_code_files(self, repo_name: str, extensions: List[str] = None) -> List[CodeFile]:
        """
        获取代码文件
        
        Args:
            repo_name: 仓库名称
            extensions: 文件扩展名列表，默认获取常见代码文件
            
        Returns:
            代码文件列表
        """
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts', '.md']
        
        # 递归获取所有文件
        all_files = self._get_all_files(repo_name)
        
        code_files = []
        for file_info in all_files:
            if file_info.type == "file":
                file_ext = os.path.splitext(file_info.name)[1].lower()
                if file_ext in extensions:
                    content = self.get_file_content(repo_name, file_info.path)
                    if content:
                        code_file = CodeFile(
                            path=file_info.path,
                            name=file_info.name,
                            content=content,
                            language=self._get_language_from_extension(file_ext),
                            size=file_info.size,
                            sha=file_info.sha,
                            lines=len(content.split('\n'))
                        )
                        code_files.append(code_file)
        
        logger.info(f"获取代码文件完成: {len(code_files)}个文件")
        return code_files
    
    def _get_all_files(self, repo_name: str, path: str = "") -> List[GitHubFile]:
        """
        递归获取所有文件
        
        Args:
            repo_name: 仓库名称
            path: 起始路径
            
        Returns:
            所有文件列表
        """
        files = self.get_directory_contents(repo_name, path)
        all_files = []
        
        for file_info in files:
            if file_info.type == "dir":
                # 递归获取子目录
                sub_files = self._get_all_files(repo_name, file_info.path)
                all_files.extend(sub_files)
            else:
                all_files.append(file_info)
        
        return all_files
    
    def _get_language_from_extension(self, extension: str) -> str:
        """
        根据文件扩展名获取语言名称
        
        Args:
            extension: 文件扩展名
            
        Returns:
            语言名称
        """
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.ts': 'TypeScript',
            '.md': 'Markdown',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.txt': 'Text',
        }
        
        return language_map.get(extension, 'Unknown')
    
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """
        获取仓库统计信息
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            统计信息字典
        """
        if not self.is_connected():
            return {}
        
        try:
            repo = self.github.get_repo(repo_name)
            
            # 获取所有文件
            all_files = self._get_all_files(repo_name)
            
            # 按类型统计
            file_count = len([f for f in all_files if f.type == "file"])
            dir_count = len([f for f in all_files if f.type == "dir"])
            
            # 按扩展名统计
            extensions = {}
            for file in all_files:
                if file.type == "file":
                    ext = os.path.splitext(file.name)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            # 获取代码文件
            code_files = self.get_code_files(repo_name)
            
            stats = {
                "total_files": file_count,
                "total_directories": dir_count,
                "total_items": len(all_files),
                "code_files": len(code_files),
                "file_extensions": dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]),
                "total_lines": sum(f.lines for f in code_files),
                "languages": list(set(f.language for f in code_files))
            }
            
            logger.info(f"获取仓库统计成功: {repo_name}")
            return stats
            
        except Exception as e:
            logger.error(f"获取仓库统计失败 {repo_name}: {e}")
            return {}

def day1_demo():
    """Day 1演示"""
    print("=" * 60)
    print("Day 1: GitHub爬取模块演示")
    print("=" * 60)
    
    crawler = GitHubCrawler()
    
    if not crawler.is_connected():
        print("❌ GitHub未连接")
        print("请检查 .env 文件中的GITHUB_TOKEN")
        return
    
    if not crawler.test_connection():
        return
    
    # 测试GitHub官方示例仓库
    test_repo = "octocat/Hello-World"
    
    print(f"\n获取仓库信息: {test_repo}")
    repo_info = crawler.get_repository_info(test_repo)
    
    if repo_info:
        print(f"✅ 仓库: {repo_info.full_name}")
        print(f"   描述: {repo_info.description}")
        print(f"   语言: {repo_info.language}")
        print(f"   Stars: {repo_info.stars}")
        print(f"   Forks: {repo_info.forks}")
    else:
        print("❌ 获取仓库信息失败")
    
    print(f"\n获取README...")
    readme = crawler.get_readme(test_repo)
    if readme:
        print(f"✅ README长度: {len(readme)} 字符")
        print(f"   预览: {readme[:100]}...")
    else:
        print("❌ 未找到README")
    
    print("\n" + "=" * 60)
    print("✅ Day 1演示完成")
    print("=" * 60)

if __name__ == "__main__":
    day1_demo()