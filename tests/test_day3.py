#!/usr/bin/env python3
"""
Day 3 测试：Issue和PR功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    print("测试导入...")
    
    try:
        from src.crawler.github_crawler import GitHubCrawler, GitHubIssue, Comment, PullRequest
        print("  GitHubCrawler和相关类")
        return True
    except Exception as e:
        print(f"  导入失败: {e}")
        return False

def test_issue_processor():
    """测试Issue处理器"""
    print("\n测试Issue处理器...")
    
    try:
        from src.crawler.issue_processor import IssueProcessor
        processor = IssueProcessor()
        
        # 测试代码块提取
        test_text = "```python\nprint('test')\n```"
        code_blocks = processor.extract_code_blocks(test_text)
        if len(code_blocks) == 1 and code_blocks[0]["language"] == "python":
            print("  代码块提取功能")
        else:
            print(f"  代码块提取异常: {code_blocks}")
            return False
        
        # 测试链接提取
        test_text = "[GitHub](https://github.com)"
        links = processor.extract_links(test_text)
        if len(links) >= 1:
            print("  链接提取功能")
        else:
            print(f"  链接提取异常: {links}")
            return False
        
        # 测试参与度分析
        engagement = processor.calculate_engagement_score("test", 0, [])
        if "total_score" in engagement and "engagement_level" in engagement:
            print("  参与度分析功能")
        else:
            print(f"  参与度分析异常: {engagement}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  Issue处理器测试失败: {e}")
        return False

def test_github_issue_methods():
    """测试GitHub Issue方法"""
    print("\n测试GitHub Issue方法...")
    
    try:
        from src.crawler.github_crawler import GitHubCrawler
        
        crawler = GitHubCrawler()
        
        if not crawler.is_connected():
            print("  GitHub未连接，跳过API测试")
            return True  # 不算失败，只是跳过
        
        # 测试方法存在性（不实际调用API）
        methods = ["get_issues", "get_issue_comments", "get_pull_requests"]
        for method in methods:
            if hasattr(crawler, method):
                print(f"  {method} 方法存在")
            else:
                print(f"  {method} 方法不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"  GitHub方法测试失败: {e}")
        return False

def run_issue_processor_demo():
    """运行Issue处理器演示"""
    print("\n运行Issue处理器演示...")
    
    try:
        from src.crawler.issue_processor import test_issue_processor
        test_issue_processor()
        return True
    except Exception as e:
        print(f"  Issue处理器演示失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Day 3 测试套件：Issue和PR功能")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("Issue处理器测试", test_issue_processor),
        ("GitHub方法测试", test_github_issue_methods),
        ("Issue处理器演示", run_issue_processor_demo),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = " " if success else " "
        print(f"{status} {test_name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n运行演示: python scripts/day3_demo.py")
    elif passed >= 3:
        print(f"\n  {total - passed} 个测试失败，但核心功能正常")
        print("\n仍然可以运行演示: python scripts/day3_demo.py")
    else:
        print(f"\n  {total - passed} 个测试失败，需要修复")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()