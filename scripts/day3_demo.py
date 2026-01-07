#!/usr/bin/env python3
"""
Day 3 演示脚本 - 修复版本（避免无限循环）
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 70)
    print("Day 3 演示：GitHub Issue与PR数据获取（修复版）")
    print("=" * 70)
    
    # 1. 初始化组件
    print("\n1. 初始化组件...")
    try:
        from src.crawler.github_crawler import GitHubCrawler
        crawler = GitHubCrawler()
        print("✅ GitHubCrawler初始化成功")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return
    
    # 2. 测试连接
    print("\n2. 测试GitHub连接...")
    if not crawler.is_connected():
        print("❌ GitHub未连接，请检查GITHUB_TOKEN配置")
        return
    
    if not crawler.test_connection():
        print("❌ GitHub连接测试失败")
        return
    
    # 3. 选择测试仓库
    test_repo = "octocat/Hello-World"  # GitHub官方示例仓库（小型）
    print(f"\n3. 测试仓库: {test_repo}")
    
    # 4. 获取仓库信息
    print("\n4. 获取仓库信息...")
    repo_info = crawler.get_repository_info(test_repo)
    if repo_info:
        print(f"   ✅ 仓库: {repo_info.full_name}")
        print(f"      描述: {repo_info.description}")
        print(f"      Stars: {repo_info.stars}")
        print(f"      Forks: {repo_info.forks}")
    else:
        print("   ❌ 获取仓库信息失败")
    
    # 5. 安全获取Issue列表（严格限制数量）
    print("\n5. 获取Issue列表（限制10个）...")
    issues = crawler.get_issues(test_repo, state="all", limit=10)
    
    if issues:
        print(f"   ✅ 获取到 {len(issues)} 个Issue")
        
        # 显示前3个Issue
        print("   前3个Issue:")
        for i, issue in enumerate(issues[:3]):
            pr_mark = " (PR)" if issue.is_pull_request else ""
            print(f"   #{issue.number}{pr_mark}: {issue.title[:50]}...")
            print(f"      状态: {issue.state}, 评论: {issue.comments}")
    else:
        print("   ❌ 未获取到Issue")
    
    # 6. 选择性获取评论（只获取前2个有评论的Issue）
    print("\n6. 选择性获取评论...")
    
    if issues:
        # 只找有评论的Issue
        issues_with_comments = [i for i in issues if i.comments > 0][:2]
        
        if issues_with_comments:
            print(f"   找到 {len(issues_with_comments)} 个有评论的Issue")
            
            for i, issue in enumerate(issues_with_comments):
                print(f"\n   [{i+1}/{len(issues_with_comments)}] 获取Issue #{issue.number}的评论...")
                
                comments = crawler.get_issue_comments(test_repo, issue.number, max_comments=3)
                
                if comments:
                    print(f"      ✅ 获取到 {len(comments)} 条评论")
                    for j, comment in enumerate(comments[:2]):  # 只显示前2条
                        print(f"         {j+1}. {comment.user}: {comment.body[:50]}...")
                else:
                    print(f"      ⚠ 未获取到评论或没有评论")
        else:
            print("   ⚠ 没有找到有评论的Issue")
    
    # 7. 获取PR数据（限制数量）
    print("\n7. 获取Pull Request数据（限制5个）...")
    prs = crawler.get_pull_requests(test_repo, state="all", limit=5)
    
    if prs:
        print(f"   ✅ 获取到 {len(prs)} 个Pull Request")
        
        # 显示统计
        merged_count = sum(1 for pr in prs if pr.merged)
        print(f"      已合并: {merged_count}")
        print(f"      未合并: {len(prs) - merged_count}")
        
        if prs:
            pr = prs[0]
            print(f"      示例PR: #{pr.number} - {pr.title[:50]}...")
            print(f"          变更: +{pr.additions}/-{pr.deletions} ({pr.changed_files}个文件)")
    else:
        print("   ❌ 未获取到PR")
    
    # 8. 保存数据
    print("\n8. 保存数据到文件...")
    try:
        # 保存Issue数据
        if issues:
            issues_data = []
            for issue in issues[:5]:  # 只保存前5个
                issue_dict = issue.to_dict()
                issues_data.append(issue_dict)
            
            output_file = "data/day3_demo_issues.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(issues_data, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ Issue数据已保存到 {output_file}")
        
        # 保存PR数据
        if prs:
            prs_data = []
            for pr in prs[:3]:  # 只保存前3个
                prs_data.append(pr.to_dict())
            
            output_file = "data/day3_demo_prs.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(prs_data, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ PR数据已保存到 {output_file}")
    
    except Exception as e:
        print(f"   ⚠ 保存数据时出错: {e}")
    
    # 9. 运行简单的仓库分析
    print("\n9. 运行仓库分析...")
    if issues:
        open_count = sum(1 for i in issues if i.state == "open")
        closed_count = sum(1 for i in issues if i.state == "closed")
        pr_count = sum(1 for i in issues if i.is_pull_request)
        
        print(f"   总Issue数: {len(issues)}")
        print(f"   开启状态: {open_count} ({open_count/len(issues)*100:.1f}%)")
        print(f"   关闭状态: {closed_count} ({closed_count/len(issues)*100:.1f}%)")
        print(f"   PR数量: {pr_count} ({pr_count/len(issues)*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ Day 3 演示完成！")
    print("=" * 70)
    
    print("\n📊 安全完成的功能:")
    print("1. ✅ GitHub连接测试")
    print("2. ✅ 仓库信息获取")
    print("3. ✅ Issue数据获取（限制数量）")
    print("4. ✅ 评论选择性获取")
    print("5. ✅ PR数据获取（限制数量）")
    print("6. ✅ 数据保存到文件")
    print("7. ✅ 简单统计分析")

    print("\n🚀 下一步:")
    print("1. 运行测试: python tests/test_day2.py")
    print("2. 提交代码: git add . && git commit -m 'Day 3完成'")
    print("3. 准备Day 4: 数据向量化与向量数据库存储")
    
    print("\n⚠ 注意: 为避免无限循环，所有获取操作都有严格的数量限制")

if __name__ == "__main__":
    main()