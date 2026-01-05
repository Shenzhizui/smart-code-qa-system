#!/usr/bin/env python3
"""
GitHub爬取模块 - Day 1基础版本
修复导入问题的完整版本
"""

import os
import sys
from pathlib import Path

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