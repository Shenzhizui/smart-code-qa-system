#!/usr/bin/env python3
"""
Day 1 演示脚本：GitHub爬取模块演示
"""

import sys
import os
from pathlib import Path

# ========== 修复导入路径 ==========
# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def day1_demo():
    """Day 1演示"""
    print("=" * 60)
    print("Day 1: GitHub爬取模块演示")
    print("=" * 60)
    
    try:
        from src.crawler.github_crawler import GitHubCrawler
        print(" GitHubCrawler导入成功")
    except ImportError as e:
        print(f"导入失败: {e}")
        print("请确保项目结构正确，或运行: pip install -r requirements.txt")
        return
    
    crawler = GitHubCrawler()
    
    if not crawler.is_connected():
        print("GitHub未连接")
        print("请检查 .env 文件中的GITHUB_TOKEN")
        return
    
    if not crawler.test_connection():
        return
    
    # 测试GitHub官方示例仓库
    test_repo = "octocat/Hello-World"
    
    print(f"\n获取仓库信息: {test_repo}")
    repo_info = crawler.get_repository_info(test_repo)
    
    if repo_info:
        print(f"仓库: {repo_info.full_name}")
        print(f"描述: {repo_info.description}")
        print(f"语言: {repo_info.language}")
        print(f"Stars: {repo_info.stars}")
        print(f"Forks: {repo_info.forks}")
    else:
        print("获取仓库信息失败")
    
    print(f"\n获取README...")
    readme = crawler.get_readme(test_repo)
    if readme:
        print(f"README长度: {len(readme)} 字符")
        print(f"   预览: {readme[:100]}...")
    else:
        print("未找到README")
    
    # 可选：测试目录内容获取（Day 2功能）
    print(f"\n获取目录内容...")
    contents = crawler.get_directory_contents(test_repo)
    if contents:
        print(f"获取到 {len(contents)} 个条目")
        for i, item in enumerate(contents[:3]):  # 只显示前3个
            type_icon = "" if item.type == "dir" else ""
            print(f"   {type_icon} {item.name} ({item.type}, {item.size} bytes)")
    else:
        print("未获取到目录内容")
    
    print("\n" + "=" * 60)
    print(" Day 1演示完成")
    print("=" * 60)

def main():
    """主函数"""
    print("Day 1演示脚本 - GitHub爬取模块")
    print("-" * 40)
    print("功能包括:")
    print("1. GitHub连接测试")
    print("2. 仓库信息获取")
    print("3. README文件获取")
    print("4. 目录内容预览")
    print("-" * 40)
    
    day1_demo()

if __name__ == "__main__":
    main()