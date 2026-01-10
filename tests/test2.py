#!/usr/bin/env python3
"""
demo2 测试
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
        from src.crawler.github_crawler import GitHubCrawler, GitHubFile, CodeFile
        print("  GitHubCrawler和相关类")
        return True
    except Exception as e:
        print(f"  导入失败: {e}")
        return False

def test_data_processor():
    """测试数据处理器"""
    print("\n测试数据处理器...")
    
    try:
        from src.crawler.data_processor import DataProcessor, TextChunk
        processor = DataProcessor()
        
        # 测试文本清理
        test_text = "  test  text  "
        cleaned = processor.clean_text(test_text)
        if cleaned == "test text":
            print("  文本清理功能")
        else:
            print(f"  文本清理异常: {repr(cleaned)}")
            return False
        
        # 测试元数据创建
        metadata = processor.create_metadata("test", "owner/repo", "test.txt")
        if all(key in metadata for key in ["source_type", "repository", "file_path"]):
            print("  元数据创建功能")
        else:
            print(f"  元数据创建异常: {metadata}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  数据处理器测试失败: {e}")
        return False

def test_github_extensions():
    """测试GitHub扩展功能"""
    print("\n测试GitHub扩展功能...")
    
    try:
        from src.crawler.github_crawler import GitHubCrawler
        
        crawler = GitHubCrawler()
        
        if not crawler.is_connected():
            print("  GitHub未连接，跳过扩展测试")
            return True  # 不算失败，只是跳过
        
        # 测试语言映射
        language = crawler._get_language_from_extension(".py")
        if language == "Python":
            print("  语言映射功能")
        else:
            print(f"  语言映射异常: {language}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  GitHub扩展测试失败: {e}")
        return False

def run_data_processor_demo():
    """运行数据处理器演示"""
    print("\n运行数据处理器演示...")
    
    try:
        # 导入并运行数据处理器测试
        from src.crawler.data_processor import test_processor
        test_processor()
        return True
    except Exception as e:
        print(f"  数据处理器演示失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Day 2 测试套件")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("数据处理器测试", test_data_processor),
        ("GitHub扩展测试", test_github_extensions),
        ("数据处理器演示", run_data_processor_demo),
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
        print("\n所有测试通过！")
        print("\n运行演示: python scripts/demo2.py")
    elif passed >= 3:
        print(f"\n  {total - passed} 个测试失败，但核心功能正常")
        print("\n仍然可以运行演示: python scripts/demo2.py")
    else:
        print(f"\n  {total - passed} 个测试失败，需要修复")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()