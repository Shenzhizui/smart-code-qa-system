#!/usr/bin/env python3
"""
demo1 演示脚本：GitHub爬取模块演示
"""

import sys
import os
import json
from pathlib import Path

# ========== 修复导入路径 ==========
# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def demo1():
    """demo1演示"""
    print("=" * 60)
    print("demo1: GitHub爬取模块演示")
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
            type_icon = "[DIR]" if item.type == "dir" else "[FILE]"
            print(f"   {type_icon} {item.name} ({item.type}, {item.size} bytes)")
    else:
        print("未获取到目录内容")
    
    # 保存数据到JSON文件
    print("\n保存数据到JSON文件...")
    try:
        demo1_data = {}
        
        # 保存仓库信息
        if repo_info:
            demo1_data["repository"] = {
                "full_name": repo_info.full_name,
                "name": repo_info.name,
                "description": repo_info.description,
                "owner": repo_info.owner,
                "language": repo_info.language,
                "stars": repo_info.stars,
                "forks": repo_info.forks,
                "url": repo_info.url,
                "created_at": repo_info.created_at,
                "updated_at": repo_info.updated_at
            }
        
        # 保存README内容
        if readme:
            demo1_data["readme"] = {
                "content": readme,
                "length": len(readme)
            }
        
        # 保存目录内容
        if contents:
            demo1_data["directory_contents"] = []
            for item in contents[:10]:  # 只保存前10个
                demo1_data["directory_contents"].append({
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "sha": item.sha,
                    "url": item.url
                })
        
        # 保存到文件
        output_file = "data/demo1_repository.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(demo1_data, f, ensure_ascii=False, indent=2)
        
        print(f"  数据已保存到 {output_file}")
        
    except Exception as e:
        print(f"  保存数据时出错: {e}")
    
    print("\n" + "=" * 60)
    print(" demo1演示完成")
    print("=" * 60)

def main():
    """主函数"""
    print("demo1演示脚本 - GitHub爬取模块")
    print("-" * 40)
    print("功能包括:")
    print("1. GitHub连接测试")
    print("2. 仓库信息获取")
    print("3. README文件获取")
    print("4. 目录内容预览")
    print("-" * 40)
    
    demo1()

if __name__ == "__main__":
    main()