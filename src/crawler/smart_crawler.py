#!/usr/bin/env python3
"""
智能GitHub爬取器 - 针对大型仓库优化
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from .github_crawler import GitHubCrawler, GitHubIssue

logger = logging.getLogger(__name__)

class SmartGitHubCrawler(GitHubCrawler):
    """智能GitHub爬取器（继承自基础爬取器）"""
    
    def __init__(self, token: Optional[str] = None, 
                 request_delay: float = 0.5,
                 max_issues_per_repo: int = 100):
        """
        初始化智能爬取器
        
        Args:
            max_issues_per_repo: 每个仓库最大Issue数量
        """
        super().__init__(token, request_delay)
        self.max_issues_per_repo = max_issues_per_repo
    
    def get_issues_smart_sample(self, repo_name: str, 
                               sample_size: int = 50) -> List[GitHubIssue]:
        """
        智能抽样获取Issue
        
        策略：
        1. 获取最近创建的Issue
        2. 获取评论最多的Issue
        3. 获取不同类型的Issue（bug/feature等）
        """
        print(f" 开始智能抽样获取 {repo_name} 的Issue...")
        print(f"   目标样本量: {sample_size}个")
        
        all_samples = []
        
        # 策略1：获取最近的Issue（30%）
        recent_count = int(sample_size * 0.3)
        print(f"   策略1: 获取最近 {recent_count} 个Issue...")
        recent_issues = self._get_recent_issues(repo_name, recent_count)
        all_samples.extend(recent_issues)
        
        # 策略2：获取评论最多的Issue（30%）
        commented_count = int(sample_size * 0.3)
        print(f"   策略2: 获取评论最多的 {commented_count} 个Issue...")
        commented_issues = self._get_most_commented_issues(repo_name, commented_count)
        all_samples.extend(commented_issues)
        
        # 策略3：获取特定标签的Issue（40%）
        labeled_count = sample_size - len(all_samples)
        if labeled_count > 0:
            print(f"   策略3: 获取重要标签的 {labeled_count} 个Issue...")
            target_labels = ["bug", "enhancement", "documentation", "help wanted"]
            labeled_issues = self._get_issues_by_labels(repo_name, target_labels, labeled_count)
            all_samples.extend(labeled_issues)
        
        # 去重
        unique_issues = self._deduplicate_issues(all_samples)
        
        print(f"  智能抽样完成: 获取 {len(unique_issues)} 个独特Issue")
        return unique_issues[:sample_size]
    
    def _get_recent_issues(self, repo_name: str, limit: int) -> List[GitHubIssue]:
        """获取最近的Issue"""
        try:
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state="all", sort="created", direction="desc")
            
            result = []
            count = 0
            
            for issue in issues:
                if count >= limit:
                    break
                
                if count > 0:
                    self._add_delay()
                
                result.append(self._convert_to_github_issue(issue))
                count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"获取最近Issue失败: {e}")
            return []
    
    def _get_most_commented_issues(self, repo_name: str, limit: int) -> List[GitHubIssue]:
        """获取评论最多的Issue"""
        try:
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state="all", sort="comments", direction="desc")
            
            result = []
            count = 0
            
            for issue in issues:
                if count >= limit:
                    break
                
                if count > 0:
                    self._add_delay()
                
                # 只取有评论的
                if issue.comments > 0:
                    result.append(self._convert_to_github_issue(issue))
                    count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"获取评论最多Issue失败: {e}")
            return []
    
    def _get_issues_by_labels(self, repo_name: str, 
                            target_labels: List[str], 
                            limit: int) -> List[GitHubIssue]:
        """按标签获取Issue"""
        all_issues = []
        
        for label in target_labels:
            if len(all_issues) >= limit:
                break
                
            try:
                query = f"repo:{repo_name} label:{label} is:issue"
                search_results = self.github.search_issues(query)
                
                for issue in search_results:
                    if len(all_issues) >= limit:
                        break
                    
                    all_issues.append(self._convert_to_github_issue(issue))
                    self._add_delay()
                    
            except Exception as e:
                logger.warning(f"搜索标签 {label} 失败: {e}")
                continue
        
        return all_issues[:limit]
    
    def _convert_to_github_issue(self, issue) -> GitHubIssue:
        """转换PyGithub Issue对象为GitHubIssue"""
        body_content = issue.body or ""
        closed_at_str = str(issue.closed_at) if issue.closed_at else None
        # 检查是否为Pull Request
        is_pr = bool(hasattr(issue, 'pull_request') and issue.pull_request is not None)
        
        return GitHubIssue(
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
    
    def _deduplicate_issues(self, issues: List[GitHubIssue]) -> List[GitHubIssue]:
        """去重Issue列表"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            if issue.number not in seen:
                seen.add(issue.number)
                unique_issues.append(issue)
        
        return unique_issues
    
    def analyze_large_repository(self, repo_name: str):
        """
        分析大型仓库的Issue概况
        """
        print(f"\n 分析大型仓库: {repo_name}")
        print("=" * 50)
        
        # 1. 获取仓库基本信息
        repo_info = self.get_repository_info(repo_name)
        if repo_info:
            print(f"仓库: {repo_info.full_name}")
            print(f"描述: {repo_info.description}")
            print(f"Stars: {repo_info.stars}, Forks: {repo_info.forks}")
        
        # 2. 获取少量样本进行分析
        print(f"\n 获取Issue样本进行分析...")
        sample_issues = self.get_issues_smart_sample(repo_name, sample_size=30)
        
        if not sample_issues:
            print(" 无法获取Issue样本")
            return
        
        # 3. 分析样本
        total_issues = len(sample_issues)
        open_count = sum(1 for i in sample_issues if i.state == "open")
        closed_count = total_issues - open_count
        pr_count = sum(1 for i in sample_issues if i.is_pull_request)
        
        print(f"\n 样本分析结果 (基于 {total_issues} 个样本):")
        print(f"   开启率: {open_count/total_issues*100:.1f}%")
        print(f"   关闭率: {closed_count/total_issues*100:.1f}%")
        print(f"   PR比例: {pr_count/total_issues*100:.1f}%")
        
        # 评论分析
        total_comments = sum(i.comments for i in sample_issues)
        avg_comments = total_comments / total_issues if total_issues > 0 else 0
        
        print(f"   平均评论数: {avg_comments:.1f}")
        
        # 标签分析
        all_labels = []
        for issue in sample_issues:
            all_labels.extend(issue.labels)
        
        if all_labels:
            label_counts = {}
            for label in all_labels:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   热门标签: {', '.join([f'{label}({count})' for label, count in top_labels])}")
        
        # 4. 估算总数
        print(f"\n 基于样本估算总体情况:")
        
        # 假设样本具有代表性，估算总体评论数
        estimated_total_comments = avg_comments * 2000 if avg_comments > 0 else 0
        print(f"   估算总评论数: {estimated_total_comments:,.0f}")
        
        # 建议的处理策略
        print(f"\n 建议处理策略:")
        print(f"   1. 使用智能抽样 (推荐 {min(100, total_issues*3)} 个样本)")
        print(f"   2. 重点关注有评论的Issue")
        print(f"   3. 按标签分类处理")
        print(f"   4. 分批处理，每次处理50-100个")