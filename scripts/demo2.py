#!/usr/bin/env python3
"""
 demo2 演示脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.github_crawler import GitHubCrawler
from src.crawler.data_processor import DataProcessor

def main():
    print("=" * 70)
    print(" demo2 演示：文件列表获取与代码下载")
    print("=" * 70)
    
    # 1. 初始化爬取器和处理器
    print("\n1. 初始化组件...")
    crawler = GitHubCrawler()
    
    if not crawler.is_connected():
        print("GitHub未连接")
        return
    
    if not crawler.test_connection():
        return
    
    processor = DataProcessor(chunk_size=400, chunk_overlap=50)
    print("组件初始化成功")
    
    # 2. 测试仓库
    test_repo = "octocat/Hello-World"  # GitHub官方示例仓库
    print(f"\n2. 测试仓库: {test_repo}")
    
    # 3. 获取目录内容
    print("\n3. 获取目录内容...")
    contents = crawler.get_directory_contents(test_repo)
    
    if contents:
        print(f"获取到 {len(contents)} 个条目")
        
        # 显示前5个
        print("   前5个条目:")
        for i, item in enumerate(contents[:5]):
            type_icon = "" if item.type == "dir" else ""
            print(f"   {type_icon} {item.name} ({item.type}, {item.size} bytes)")
    else:
        print("未获取到目录内容")
        return
    
    # 4. 获取文件内容
    print("\n4. 获取文件内容...")
    # 查找第一个文件
    first_file = next((item for item in contents if item.type == "file"), None)
    
    if first_file:
        print(f"   获取文件: {first_file.name}")
        content = crawler.get_file_content(test_repo, first_file.path)
        
        if content:
            print(f"文件内容获取成功: {len(content)} 字符")
            print(f"预览: {content[:100]}...")
            
            # 测试数据清洗
            print("\n5. 测试数据清洗...")
            cleaned_content = processor.clean_text(content)
            print(f"数据清洗完成")
            print(f"原始长度: {len(content)} 字符")
            print(f"清洗后长度: {len(cleaned_content)} 字符")
        else:
            print("文件内容获取失败")
    else:
        print("未找到文件")
    
    # 5. 获取代码文件统计
    print("\n6. 获取仓库统计信息...")
    stats = crawler.get_repository_stats(test_repo)
    
    if stats:
        print(f"仓库统计:")
        print(f"总文件数: {stats.get('total_files', 0)}")
        print(f"总目录数: {stats.get('total_directories', 0)}")
        print(f"代码文件数: {stats.get('code_files', 0)}")
        print(f"总代码行数: {stats.get('total_lines', 0)}")
        
        if stats.get('file_extensions'):
            print(f"文件扩展名分布:")
            for ext, count in stats['file_extensions'].items():
                print(f"{ext}: {count} 个")
    else:
        print("获取统计信息失败")
    
    # 6. 测试数据处理器
    print("\n7. 测试数据处理器...")
    
    # 创建测试文本
    test_text = "这是一个用于测试数据处理的文本。我们将测试文本分割功能。这个功能可以将长文本分割成适合处理的小块。"
    
    metadata = processor.create_metadata(
        source_type="doc",
        repo_name=test_repo,
        file_path="README.md",
        author="octocat"
    )
    
    chunks = processor.split_text(test_text, metadata)
    print(f"文本分割测试:")
    print(f": {len(test_text)} 字符")
    print(f"分割为: {len(chunks)} 个块")
    
    if chunks:
        print(f"第一个块: {chunks[0].content[:50]}...")
        print(f"元数据: {chunks[0].metadata.get('repository')}")
    
    print("\n" + "=" * 70)
    print(" demo2 演示完成！")
    print("=" * 70)
    
    print("\n今日完成功能:")
    print("1.目录内容获取")
    print("2.文件内容下载")
    print("3.代码文件过滤")
    print("4.仓库统计分析")
    print("5.数据清洗处理")
    print("6.文本分割功能")
    
    print("\n下一步:")
    print("1. 运行测试: python tests/test_day2.py")
    print("2. 提交代码: git add . && git commit -m ' demo2完成'")
    print("3. 准备demo3: Issue数据获取")

if __name__ == "__main__":
    main()