#!/usr/bin/env python3
"""
Issue和PR数据处理模块
"""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IssueProcessor:
    """Issue和PR数据处理器"""
    
    def __init__(self):
        """初始化处理器"""
        pass
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取代码块
        
        Args:
            text: 包含代码块的文本
            
        Returns:
            代码块列表
        """
        if not text:
            return []
        
        code_blocks = []
        
        # 匹配Markdown代码块
        pattern = r'```(\w*)\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for language, code in matches:
            code_block = {
                "language": language or "text",
                "code": code.strip(),
                "lines": len(code.strip().split('\n'))
            }
            code_blocks.append(code_block)
        
        logger.info(f"提取代码块: {len(code_blocks)}个")
        return code_blocks
    
    def extract_links(self, text: str) -> List[Dict[str, str]]:
        """
        从文本中提取链接
        
        Args:
            text: 包含链接的文本
            
        Returns:
            链接列表
        """
        if not text:
            return []
        
        links = []
        
        # 匹配Markdown链接 [text](url)
        md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        md_matches = re.findall(md_pattern, text)
        
        for link_text, url in md_matches:
            links.append({
                "type": "markdown_link",
                "text": link_text,
                "url": url
            })
        
        # 匹配直接URL
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        url_matches = re.findall(url_pattern, text)
        
        for url in url_matches:
            links.append({
                "type": "direct_url",
                "text": url,
                "url": url
            })
        
        logger.info(f"提取链接: {len(links)}个")
        return links
    
    def extract_issue_references(self, text: str, repo_name: str) -> List[Dict[str, Any]]:
        """
        提取Issue/PR引用
        
        Args:
            text: 文本内容
            repo_name: 仓库名称
            
        Returns:
            引用列表
        """
        if not text:
            return []
        
        references = []
        
        # 匹配 #数字 格式的引用
        pattern = r'#(\d+)'
        matches = re.findall(pattern, text)
        
        for issue_num in matches:
            references.append({
                "type": "issue_reference",
                "reference": f"#{issue_num}",
                "number": int(issue_num),
                "repo": repo_name
            })
        
        # 匹配 user/repo#数字 格式的跨仓库引用
        cross_repo_pattern = r'([\w-]+/[\w-]+)#(\d+)'
        cross_matches = re.findall(cross_repo_pattern, text)
        
        for cross_repo, issue_num in cross_matches:
            references.append({
                "type": "cross_repo_reference",
                "reference": f"{cross_repo}#{issue_num}",
                "repo": cross_repo,
                "number": int(issue_num)
            })
        
        logger.info(f"提取Issue引用: {len(references)}个")
        return references
    
    def analyze_issue_timeline(self, created_at: str, 
                              updated_at: str, 
                              closed_at: Optional[str] = None) -> Dict[str, Any]:
        """
        分析Issue时间线
        
        Args:
            created_at: 创建时间
            updated_at: 更新时间
            closed_at: 关闭时间
            
        Returns:
            时间线分析结果
        """
        from datetime import datetime
        
        timeline = {
            "created_at": created_at,
            "updated_at": updated_at,
            "closed_at": closed_at
        }
        
        try:
            # 解析时间字符串
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            # 计算存活时间（从创建到更新）
            lifetime_days = (updated - created).days
            
            timeline["lifetime_days"] = lifetime_days
            
            if closed_at:
                closed = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
                # 计算解决时间（从创建到关闭）
                resolution_days = (closed - created).days
                timeline["resolution_days"] = resolution_days
                
                # 分类解决时间
                if resolution_days < 1:
                    timeline["resolution_speed"] = "超快 (<1天)"
                elif resolution_days < 7:
                    timeline["resolution_speed"] = "快速 (1-7天)"
                elif resolution_days < 30:
                    timeline["resolution_speed"] = "中等 (1-4周)"
                else:
                    timeline["resolution_speed"] = "慢 (>1个月)"
            
        except Exception as e:
            logger.warning(f"时间线分析失败: {e}")
        
        return timeline
    
    def calculate_engagement_score(self, 
                                  issue_body: str,
                                  comments_count: int,
                                  labels: List[str]) -> Dict[str, Any]:
        """
        计算Issue参与度分数
        
        Args:
            issue_body: Issue正文
            comments_count: 评论数量
            labels: 标签列表
            
        Returns:
            参与度分析结果
        """
        score = 0
        details = {}
        
        # 1. 正文长度分数
        body_length = len(issue_body) if issue_body else 0
        if body_length > 1000:
            score += 30
            details["body_length_score"] = "详细 (30分)"
        elif body_length > 500:
            score += 20
            details["body_length_score"] = "中等 (20分)"
        elif body_length > 100:
            score += 10
            details["body_length_score"] = "简短 (10分)"
        else:
            details["body_length_score"] = "简略 (0分)"
        
        # 2. 评论数量分数
        if comments_count > 20:
            score += 40
            details["comments_score"] = "热烈讨论 (40分)"
        elif comments_count > 10:
            score += 30
            details["comments_score"] = "活跃讨论 (30分)"
        elif comments_count > 5:
            score += 20
            details["comments_score"] = "一般讨论 (20分)"
        elif comments_count > 0:
            score += 10
            details["comments_score"] = "少量讨论 (10分)"
        else:
            details["comments_score"] = "无讨论 (0分)"
        
        # 3. 标签分数
        important_labels = {"bug", "enhancement", "feature", "critical", "security"}
        label_score = 0
        for label in labels:
            if label.lower() in important_labels:
                label_score += 5
        
        score += label_score
        details["labels_score"] = f"标签分 ({label_score}分)"
        
        # 4. 包含代码块加分
        code_blocks = self.extract_code_blocks(issue_body)
        if code_blocks:
            score += 15
            details["code_blocks_score"] = "含代码示例 (15分)"
        else:
            details["code_blocks_score"] = "无代码示例 (0分)"
        
        # 总分和评级
        details["total_score"] = score
        
        if score >= 80:
            details["engagement_level"] = "非常高"
        elif score >= 60:
            details["engagement_level"] = "高"
        elif score >= 40:
            details["engagement_level"] = "中等"
        elif score >= 20:
            details["engagement_level"] = "低"
        else:
            details["engagement_level"] = "非常低"
        
        return details
    
    def create_issue_summary(self, issue: Dict[str, Any]) -> str:
        """
        创建Issue摘要
        
        Args:
            issue: Issue数据
            
        Returns:
            摘要文本
        """
        title = issue.get("title", "无标题")
        number = issue.get("number", "?")
        user = issue.get("user", "匿名")
        state = issue.get("state", "未知")
        
        # 构建摘要
        summary = f"Issue #{number}: {title}\n"
        summary += f"状态: {state} | 创建者: {user}\n"
        
        if "body" in issue and issue["body"]:
            body_preview = issue["body"][:200].replace('\n', ' ')
            summary += f"内容预览: {body_preview}...\n"
        
        if "labels" in issue and issue["labels"]:
            summary += f"标签: {', '.join(issue['labels'][:5])}"
            if len(issue["labels"]) > 5:
                summary += f" 等{len(issue['labels'])}个"
        
        return summary

def test_issue_processor():
    """测试Issue处理器"""
    print("=" * 60)
    print("Issue处理器测试")
    print("=" * 60)
    
    processor = IssueProcessor()
    
    # 测试数据
    test_text = """
    这是一个测试Issue内容。
    
    代码示例：
    ```python
    def hello():
        print("Hello World")
    ```
    
    这里有一个链接：[GitHub](https://github.com)
    还有一个直接链接：https://google.com
    
    引用其他Issue: #123 和 #456
    跨仓库引用：owner/repo#789
    """
    
    # 测试代码块提取
    print("\n1. 测试代码块提取...")
    code_blocks = processor.extract_code_blocks(test_text)
    print(f"   找到 {len(code_blocks)} 个代码块")
    for block in code_blocks:
        print(f"   语言: {block['language']}, 行数: {block['lines']}")
    
    # 测试链接提取
    print("\n2. 测试链接提取...")
    links = processor.extract_links(test_text)
    print(f"   找到 {len(links)} 个链接")
    for link in links[:3]:
        print(f"   类型: {link['type']}, URL: {link['url'][:50]}...")
    
    # 测试Issue引用提取
    print("\n3. 测试Issue引用提取...")
    refs = processor.extract_issue_references(test_text, "test/repo")
    print(f"   找到 {len(refs)} 个引用")
    for ref in refs:
        print(f"   类型: {ref['type']}, 引用: {ref['reference']}")
    
    # 测试时间线分析
    print("\n4. 测试时间线分析...")
    timeline = processor.analyze_issue_timeline(
        "2024-01-01T00:00:00Z",
        "2024-01-10T00:00:00Z",
        "2024-01-08T00:00:00Z"
    )
    print(f"   存活天数: {timeline.get('lifetime_days', 'N/A')}")
    print(f"   解决天数: {timeline.get('resolution_days', 'N/A')}")
    print(f"   解决速度: {timeline.get('resolution_speed', 'N/A')}")
    
    # 测试参与度分析
    print("\n5. 测试参与度分析...")
    engagement = processor.calculate_engagement_score(
        issue_body="详细的问题描述" * 50,  # 长文本
        comments_count=15,
        labels=["bug", "enhancement", "test"]
    )
    print(f"   总分: {engagement.get('total_score', 0)}")
    print(f"   参与度: {engagement.get('engagement_level', '未知')}")
    for key, value in engagement.items():
        if key not in ["total_score", "engagement_level"]:
            print(f"   {key}: {value}")
    
    # 测试摘要生成
    print("\n6. 测试摘要生成...")
    test_issue = {
        "number": 123,
        "title": "测试Issue标题",
        "state": "open",
        "user": "testuser",
        "body": "这是一个测试Issue内容，用于测试摘要生成功能。",
        "labels": ["bug", "high-priority"]
    }
    summary = processor.create_issue_summary(test_issue)
    print(f"   摘要:\n{summary}")
    
    print("\n" + "=" * 60)
    print("✅ Issue处理器测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_issue_processor()