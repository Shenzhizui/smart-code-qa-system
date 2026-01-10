#!/usr/bin/env python3
"""
处理大型GitHub仓库的脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 70)
    print("大型GitHub仓库处理工具")
    print("=" * 70)
    
    # 导入智能爬取器
    try:
        from src.crawler.smart_crawler import SmartGitHubCrawler
        print("  智能爬取器导入成功")
    except ImportError as e:
        print(f"  导入失败: {e}")
        print("请先创建 smart_crawler.py 文件")
        return
    
    # 初始化
    crawler = SmartGitHubCrawler(request_delay=0.5, max_issues_per_repo=100)
    
    if not crawler.is_connected():
        print("  GitHub未连接")
        return
    
    # 示例仓库（可以替换为你的目标仓库）
    large_repo = "Shenzhizui/smart-code-qa-system"  # 你自己的仓库
    
    print(f"\n  目标仓库: {large_repo}")
    print("-" * 50)
    
    # 分析大型仓库
    crawler.analyze_large_repository(large_repo)
    
    print(f"\n  开始智能抽样获取Issue...")
    
    # 获取智能样本
    sample_issues = crawler.get_issues_smart_sample(large_repo, sample_size=50)
    
    if sample_issues:
        print(f"\n  成功获取 {len(sample_issues)} 个Issue样本")
        
        # 保存样本数据
        import json
        os.makedirs("data/large_repo", exist_ok=True)
        
        # 转换为字典
        issues_data = []
        for issue in sample_issues:
            issue_dict = issue.to_dict()
            
            # 选择性获取评论（只获取前3个有评论的Issue）
            if issue.comments > 0 and len([i for i in issues_data if "comments_data" in i]) < 3:
                print(f"   获取Issue #{issue.number} 的评论...")
                comments = crawler.get_issue_comments(
                    large_repo, 
                    issue.number, 
                    max_comments=10
                )
                if comments:
                    issue_dict["comments_sample"] = [
                        {
                            "user": c.user,
                            "body_preview": c.body[:100] + "..." if len(c.body) > 100 else c.body,
                            "created_at": c.created_at
                        } for c in comments[:3]  # 只保存前3条评论
                    ]
            
            issues_data.append(issue_dict)
        
        # 保存到文件
        output_file = "data/large_repo/sample_issues.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(issues_data, f, ensure_ascii=False, indent=2)
        
        print(f"  样本数据已保存到: {output_file}")
        
        # 显示统计信息
        print(f"\n  样本统计:")
        print(f"   总Issue数: {len(sample_issues)}")
        
        issues_with_comments = [i for i in sample_issues if i.comments > 0]
        print(f"   有评论的Issue: {len(issues_with_comments)}")
        
        avg_comments = sum(i.comments for i in sample_issues) / len(sample_issues)
        print(f"   平均评论数: {avg_comments:.1f}")
        
        # 标签分布
        all_labels = []
        for issue in sample_issues:
            all_labels.extend(issue.labels)
        
        if all_labels:
            unique_labels = set(all_labels)
            print(f"   标签种类: {len(unique_labels)}")
    
    print("\n" + "=" * 70)
    print("  大型仓库处理完成")
    print("=" * 70)
    
    print("\n💡 后续建议:")
    print("1. 使用样本数据进行开发和测试")
    print("2. 需要完整数据时再分批获取")
    print("3. 重点关注有评论和重要标签的Issue")

if __name__ == "__main__":
    main()