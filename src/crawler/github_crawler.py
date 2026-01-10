#!/usr/bin/env python3
"""
GitHub爬取模块 - 优化版本
包含速率控制、缓存和性能优化
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

# ========== 修复导入路径 ==========
# 添加项目根目录到Python路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # src/crawler -> src -> project_root
sys.path.insert(0, str(project_root))

# 现在可以导入config模块
try:
    from config.settings import GITHUB_TOKEN
    print(f"  从config.settings导入成功")
except ImportError as e:
    print(f" 导入config.settings失败: {e}")
    print("尝试直接从环境变量读取...")
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

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

@dataclass  
class GitHubIssue:
    """GitHub Issue数据类"""
    number: int
    title: str
    body: str
    state: str  # 'open', 'closed'
    created_at: str
    updated_at: str
    user: str  # 创建者
    closed_at: Optional[str] = None
    assignees: List[str] = None
    labels: List[str] = None
    comments: int = 0
    url: str = ""
    is_pull_request: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if self.assignees is None:
            self.assignees = []
        if self.labels is None:
            self.labels = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
            "user": self.user,
            "assignees": self.assignees,
            "labels": self.labels,
            "comments": self.comments,
            "url": self.url,
            "is_pull_request": bool(self.is_pull_request) if self.is_pull_request is not None else False
        }
    
    def to_text_for_embedding(self) -> str:
        """转换为适合向量化的文本格式"""
        text = f"Issue #{self.number}: {self.title}\n"
        text += f"状态: {self.state}\n"
        text += f"创建者: {self.user}\n"
        text += f"创建时间: {self.created_at}\n"
        if self.body:
            # 限制内容长度，避免向量化文本过长
            body_preview = self.body[:500] + "..." if len(self.body) > 500 else self.body
            text += f"内容: {body_preview}\n"
        if self.labels:
            text += f"标签: {', '.join(self.labels[:5])}"  # 只显示前5个标签
            if len(self.labels) > 5:
                text += f" 等{len(self.labels)}个"
            text += "\n"
        if self.comments > 0:
            text += f"评论数量: {self.comments}\n"
        return text

@dataclass
class Comment:
    """评论数据类"""
    id: int
    user: str
    body: str
    created_at: str
    updated_at: str
    url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user": self.user,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "url": self.url
        }
    
    def to_text(self) -> str:
        """转换为文本"""
        return f"{self.user} 评论于 {self.created_at}:\n{self.body}"

@dataclass
class PullRequest(GitHubIssue):
    """Pull Request数据类(继承自Issue)"""
    merged: bool = False
    mergeable: bool = False
    mergeable_state: str = ""
    merged_at: Optional[str] = None
    merge_commit_sha: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    head_ref: str = ""  # 源分支
    base_ref: str = ""  # 目标分支
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，添加PR特有字段"""
        base_dict = super().to_dict()
        base_dict.update({
            "merged": self.merged,
            "mergeable": self.mergeable,
            "mergeable_state": self.mergeable_state,
            "merged_at": self.merged_at,
            "merge_commit_sha": self.merge_commit_sha,
            "additions": self.additions,
            "deletions": self.deletions,
            "changed_files": self.changed_files,
            "head_ref": self.head_ref,
            "base_ref": self.base_ref
        })
        return base_dict
    
    def to_text_for_embedding(self) -> str:
        """转换为适合向量化的文本格式"""
        base_text = super().to_text_for_embedding()
        base_text = base_text.replace("Issue #", "Pull Request #")
        
        pr_info = f"\nPull Request信息:\n"
        pr_info += f"状态: {'已合并' if self.merged else self.state}\n"
        if self.merged and self.merged_at:
            pr_info += f"合并时间: {self.merged_at}\n"
        pr_info += f"代码变更: +{self.additions} -{self.deletions} ({self.changed_files}个文件)\n"
        if self.head_ref and self.base_ref:
            pr_info += f"分支: {self.head_ref} → {self.base_ref}\n"
        
        return base_text + pr_info

class GitHubCrawler:
    """GitHub仓库爬取器（优化版本）"""
    
    def __init__(self, token: Optional[str] = None, request_delay: float = 0.3):
        """
        初始化爬取器
        
        Args:
            token: GitHub Token
            request_delay: 请求之间的延迟（秒），避免速率限制
        """
        self.token = token or GITHUB_TOKEN
        self.request_delay = request_delay
        self.comment_cache: Dict[str, List[Comment]] = {}  # 评论缓存
        self.issue_cache: Dict[str, List[GitHubIssue]] = {}  # Issue缓存
        self.pr_cache: Dict[str, List[PullRequest]] = {}  # PR缓存
        
        if not self.token or self.token == "your_github_token_here":
            logger.error("请配置GITHUB_TOKEN！")
            logger.error("编辑 .env 文件，设置你的GitHub Token")
            self.github = None
            return
        
        try:
            from github import Github
            self.github = Github(self.token, per_page=100)  # 每页100条
            logger.info("  GitHub API 初始化成功")
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
            logger.info(f"  GitHub连接成功: {user.login}")
            return True
        except Exception as e:
            logger.error(f" GitHub连接失败: {e}")
            return False
    
    def _add_delay(self):
        """添加请求延迟"""
        time.sleep(self.request_delay)
    
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
            
            logger.info(f"  获取仓库信息成功: {repo.full_name}")
            return info
            
        except Exception as e:
            logger.error(f" 获取仓库失败 {repo_name}: {e}")
            return None
    
    def get_readme(self, repo_name: str) -> Optional[str]:
        """获取README文件"""
        if not self.is_connected():
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8')
            logger.info(f"  找到README文件")
            return content
        except:
            logger.warning("未找到README文件")
            return None
    
    def get_directory_contents(self, repo_name: str, path: str = "") -> List[GitHubFile]:
        """获取目录下的文件和子目录列表"""
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
        """获取文件内容"""
        if not self.is_connected():
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            file = repo.get_contents(file_path)
            
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
    
    def get_code_files(self, repo_name: str, extensions: List[str] = None, 
                      max_files: int = 50) -> List[CodeFile]:
        """
        获取代码文件（限制数量避免过多）
        """
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts', '.md']
        
        all_files = self._get_all_files(repo_name)
        
        code_files = []
        count = 0
        
        for file_info in all_files:
            if count >= max_files:
                logger.info(f"已达到最大文件数限制: {max_files}")
                break
                
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
                        count += 1
                        
                        # 添加延迟，避免速率限制
                        if count % 10 == 0:
                            self._add_delay()
        
        logger.info(f"获取代码文件完成: {len(code_files)}个文件")
        return code_files
    
    def _get_all_files(self, repo_name: str, path: str = "") -> List[GitHubFile]:
        """递归获取所有文件"""
        files = self.get_directory_contents(repo_name, path)
        all_files = []
        
        for file_info in files:
            if file_info.type == "dir":
                sub_files = self._get_all_files(repo_name, file_info.path)
                all_files.extend(sub_files)
            else:
                all_files.append(file_info)
        
        return all_files
    
    def _get_language_from_extension(self, extension: str) -> str:
        """根据文件扩展名获取语言名称"""
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.go': 'Go', '.rs': 'Rust',
            '.ts': 'TypeScript', '.md': 'Markdown', '.html': 'HTML',
            '.css': 'CSS', '.json': 'JSON', '.yml': 'YAML', '.yaml': 'YAML',
            '.txt': 'Text',
        }
        return language_map.get(extension, 'Unknown')
    
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """获取仓库统计信息"""
        if not self.is_connected():
            return {}
        
        try:
            repo = self.github.get_repo(repo_name)
            
            all_files = self._get_all_files(repo_name)
            
            file_count = len([f for f in all_files if f.type == "file"])
            dir_count = len([f for f in all_files if f.type == "dir"])
            
            extensions = {}
            for file in all_files:
                if file.type == "file":
                    ext = os.path.splitext(file.name)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            code_files = self.get_code_files(repo_name, max_files=20)  # 限制数量
            
            stats = {
                "total_files": file_count,
                "total_directories": dir_count,
                "total_items": len(all_files),
                "code_files": len(code_files),
                "file_extensions": dict(sorted(extensions.items(), 
                                             key=lambda x: x[1], reverse=True)[:10]),
                "total_lines": sum(f.lines for f in code_files),
                "languages": list(set(f.language for f in code_files))
            }
            
            logger.info(f"获取仓库统计成功: {repo_name}")
            return stats
            
        except Exception as e:
            logger.error(f"获取仓库统计失败 {repo_name}: {e}")
            return {}

    def get_issues(self, repo_name: str, 
                   state: str = "open", 
                   limit: int = 30,  # 默认限制为30个
                   since: Optional[str] = None,
                   use_cache: bool = True) -> List[GitHubIssue]:
        """
        获取Issue列表（带缓存和限制）
        """
        cache_key = f"{repo_name}_{state}_{limit}"
        
        # 检查缓存
        if use_cache and cache_key in self.issue_cache:
            logger.info(f"从缓存获取Issue: {cache_key}")
            return self.issue_cache[cache_key]
        
        if not self.is_connected():
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            
            kwargs = {"state": state}
            if since:
                kwargs["since"] = since
            
            issues = repo.get_issues(**kwargs)
            
            issue_list = []
            count = 0
            
            for issue in issues:
                if count >= limit:
                    break
                
                # 添加延迟，避免速率限制
                if count > 0:
                    self._add_delay()
                
                # 检查是否为Pull Request
                is_pr = bool(hasattr(issue, 'pull_request') and issue.pull_request is not None)
                
                body_content = issue.body or ""
                closed_at_str = str(issue.closed_at) if issue.closed_at else None
                
                github_issue = GitHubIssue(
                    number=issue.number,
                    title=issue.title,
                    body=body_content,
                    state=issue.state,
                    created_at=str(issue.created_at),
                    updated_at=str(issue.updated_at),
                    closed_at=closed_at_str,
                    user=issue.user.login if issue.user else "Unknown",
                    assignees=[assignee.login for assignee in issue.assignees],
                    labels=[label.name for label in issue.labels],
                    comments=issue.comments,
                    url=issue.html_url,
                    is_pull_request=is_pr
                )
                
                issue_list.append(github_issue)
                count += 1
                
                # 显示进度
                if count % 10 == 0:
                    logger.info(f"已获取 {count} 个Issue...")
            
            # 缓存结果
            if use_cache:
                self.issue_cache[cache_key] = issue_list
            
            logger.info(f"获取Issue成功: {len(issue_list)}个{state}状态的Issue")
            return issue_list
            
        except Exception as e:
            logger.error(f"获取Issue失败 {repo_name}: {e}")
            return []
    
    def get_issue_comments(self, repo_name: str, issue_number: int,
                          max_comments: int = 20,  # 限制评论数量
                          use_cache: bool = True) -> List[Comment]:
        """
        获取Issue评论（带缓存和限制）
        """
        cache_key = f"{repo_name}#{issue_number}"
        
        # 检查缓存
        if use_cache and cache_key in self.comment_cache:
            logger.info(f"从缓存获取评论: {cache_key}")
            return self.comment_cache[cache_key]
        
        if not self.is_connected():
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            comments = issue.get_comments()
            
            comment_list = []
            count = 0
            
            for comment in comments:
                if count >= max_comments:
                    logger.info(f"达到最大评论数限制: {max_comments}")
                    break
                
                # 添加延迟，避免速率限制
                if count > 0:
                    self._add_delay()
                
                comment_data = Comment(
                    id=comment.id,
                    user=comment.user.login if comment.user else "",
                    body=comment.body or "",
                    created_at=str(comment.created_at),
                    updated_at=str(comment.updated_at),
                    url=comment.html_url
                )
                comment_list.append(comment_data)
                count += 1
            
            # 缓存结果
            if use_cache:
                self.comment_cache[cache_key] = comment_list
            
            logger.info(f"获取Issue评论成功: Issue #{issue_number} ({len(comment_list)}条评论)")
            return comment_list
            
        except Exception as e:
            logger.error(f"获取Issue评论失败 {repo_name}#{issue_number}: {e}")
            return []
    
    def get_issues_with_comments(self, repo_name: str, 
                                issue_limit: int = 10,
                                comment_limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取Issue及其评论（修复版本）
        """
        print(f"开始获取仓库 {repo_name} 的Issue和评论...")
        
        # 重要：先获取Issue列表，限制数量
        issues = self.get_issues(repo_name, state="all", limit=issue_limit)
        
        if not issues:
            print(" 没有获取到Issue数据")
            return []
        
        print(f"  获取到 {len(issues)} 个Issue")
        
        # 只处理有评论的Issue（最多5个）
        issues_with_comments = [i for i in issues if i.comments > 0][:5]
        
        if not issues_with_comments:
            print("没有找到有评论的Issue")
            return []
        
        print(f"将处理 {len(issues_with_comments)} 个有评论的Issue...")
        
        results = []
        
        for i, issue in enumerate(issues_with_comments):
            print(f"\n[{i+1}/{len(issues_with_comments)}] 处理Issue #{issue.number}...")
            print(f"   标题: {issue.title[:50]}...")
            print(f"   评论数: {issue.comments}")
            
            # 获取评论（限制数量）
            if issue.comments > 0:
                print(f"获取评论中...")
                comments = self.get_issue_comments(
                    repo_name, 
                    issue.number, 
                    max_comments=comment_limit
                )
                
                if comments:
                    print(f"     获取到 {len(comments)} 条评论")
                    
                    # 转换Issue为字典
                    issue_dict = issue.to_dict()
                    issue_dict["comments_data"] = [
                        {
                            "user": c.user,
                            "body": c.body[:100] + "..." if len(c.body) > 100 else c.body,
                            "created_at": c.created_at
                        } for c in comments
                    ]
                    results.append(issue_dict)
                else:
                    print("获取评论失败，可能没有评论或API限制")
            else:
                print("无评论，跳过")
        
        print(f"\n  完成! 共处理 {len(results)} 个Issue")
        return results
    
    def save_issues_to_json(self, issues: List[Dict[str, Any]], 
                           filename: str = "data/issues.json"):
        """保存Issue数据到JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(issues, f, ensure_ascii=False, indent=2)
            
            print(f"  Issue数据已保存到 {filename} (共 {len(issues)} 个)")
            return True
            
        except Exception as e:
            print(f" 保存Issue数据失败: {e}")
            return False
    
    def analyze_repository_issues(self, repo_name: str):
        """分析仓库的Issue状况（快速分析）"""
        print(f"\n  分析仓库 {repo_name} 的Issue状况...")
        
        # 只获取少量数据进行快速分析
        issues = self.get_issues(repo_name, state="all", limit=50, use_cache=True)
        
        if not issues:
            print(" 没有获取到Issue数据")
            return
        
        # 统计信息
        open_count = sum(1 for i in issues if i.state == "open")
        closed_count = sum(1 for i in issues if i.state == "closed")
        pr_count = sum(1 for i in issues if i.is_pull_request)
        total_comments = sum(i.comments for i in issues)
        
        # 标签统计
        all_labels = []
        for issue in issues:
            all_labels.extend(issue.labels)
        
        label_counts = {}
        for label in all_labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        print(f"   总Issue数: {len(issues)}")
        print(f"   开启状态: {open_count} ({open_count/len(issues)*100:.1f}%)")
        print(f"   关闭状态: {closed_count} ({closed_count/len(issues)*100:.1f}%)")
        print(f"   PR数量: {pr_count} ({pr_count/len(issues)*100:.1f}%)")
        print(f"   总评论数: {total_comments} (平均 {total_comments/len(issues):.1f}条/Issue)")
        print(f"   标签种类: {len(set(all_labels))}")
        
        # 显示最常见的标签
        if label_counts:
            top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            print("   最常见标签:")
            for label, count in top_labels:
                percentage = count / len(issues) * 100
                print(f"     - {label}: {count}次 ({percentage:.1f}%)")
    
    def get_pull_requests(self, repo_name: str,
                         state: str = "open",
                         limit: int = 20,  # 限制数量
                         use_cache: bool = True) -> List[PullRequest]:
        """
        获取Pull Request列表（带缓存和限制）
        """
        cache_key = f"{repo_name}_pr_{state}_{limit}"
        
        # 检查缓存
        if use_cache and cache_key in self.pr_cache:
            logger.info(f"从缓存获取PR: {cache_key}")
            return self.pr_cache[cache_key]
        
        if not self.is_connected():
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            pulls = repo.get_pulls(state=state, sort="created", direction="desc")
            
            pr_list = []
            count = 0
            
            for pr in pulls:
                if count >= limit:
                    break
                
                # 添加延迟，避免速率限制
                if count > 0:
                    self._add_delay()
                
                pull_request = PullRequest(
                    number=pr.number,
                    title=pr.title,
                    body=pr.body or "",
                    state=pr.state,
                    created_at=str(pr.created_at),
                    updated_at=str(pr.updated_at),
                    closed_at=str(pr.closed_at) if pr.closed_at else None,
                    user=pr.user.login if pr.user else "",
                    assignees=[assignee.login for assignee in pr.assignees],
                    labels=[label.name for label in pr.labels],
                    comments=pr.comments,
                    url=pr.html_url,
                    is_pull_request=True,
                    merged=pr.merged,
                    mergeable=pr.mergeable,
                    mergeable_state=pr.mergeable_state,
                    merged_at=str(pr.merged_at) if pr.merged_at else None,
                    merge_commit_sha=pr.merge_commit_sha,
                    additions=pr.additions,
                    deletions=pr.deletions,
                    changed_files=pr.changed_files,
                    head_ref=pr.head.ref if pr.head else "",
                    base_ref=pr.base.ref if pr.base else ""
                )
                
                pr_list.append(pull_request)
                count += 1
                
                # 显示进度
                if count % 5 == 0:
                    logger.info(f"已获取 {count} 个PR...")
            
            # 缓存结果
            if use_cache:
                self.pr_cache[cache_key] = pr_list
            
            logger.info(f"获取Pull Request成功: {len(pr_list)}个{state}状态的PR")
            return pr_list
            
        except Exception as e:
            logger.error(f"获取Pull Request失败 {repo_name}: {e}")
            return []
    
    def clear_cache(self):
        """清空所有缓存"""
        self.comment_cache.clear()
        self.issue_cache.clear()
        self.pr_cache.clear()
        print("  已清空所有缓存")

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub爬取模块 - 优化版本")
    print("=" * 60)
    print("此模块包含以下优化:")
    print("1. 速率控制（避免API限制）")
    print("2. 数据缓存（减少重复请求）")
    print("3. 数量限制（避免过多数据）")
    print("4. 进度显示（更好的用户体验）")
    print("=" * 60)