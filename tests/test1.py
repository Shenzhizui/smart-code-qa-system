#!/usr/bin/env python3
"""
demo1 测试
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    print("测试导入...")
    
    try:
        import config.settings
        print("  config.settings")
    except Exception as e:
        print(f"  config.settings: {e}")
        return False
    
    try:
        from src.crawler.github_crawler import GitHubCrawler
        print("  GitHubCrawler")
        return True
    except Exception as e:
        print(f"  GitHubCrawler: {e}")
        return False

def test_config():
    print("\n测试配置文件...")
    
    from config import settings
    
    print(f"项目: {settings.PROJECT_NAME}")
    print(f"版本: {settings.VERSION}")
    print(f"主机: {settings.HOST}:{settings.PORT}")
    print(f"调试模式: {settings.DEBUG}")
    
    # 修复：直接检查settings中的GITHUB_TOKEN
    if hasattr(settings, 'GITHUB_TOKEN'):
        token = settings.GITHUB_TOKEN
        if token and token != "your_github_token_here":
            print(f"  settings.GITHUB_TOKEN: 已配置 ({token[:10]}...)")
            return True
        else:
            print("  settings.GITHUB_TOKEN: 未配置或为示例值")
            print("   但可能从环境变量正确读取了")
            # 检查环境变量
            load_dotenv()
            env_token = os.getenv("GITHUB_TOKEN")
            if env_token and env_token != "your_github_token_here":
                print(f"     环境变量中有Token: {env_token[:10]}...")
                return True
    return False

def test_github_connection():
    print("\n测试GitHub连接...")
    
    try:
        from src.crawler.github_crawler import GitHubCrawler
        crawler = GitHubCrawler()
        
        if not crawler.is_connected():
            print("  GitHub爬取器未连接")
            return False
        
        if crawler.test_connection():
            print("  GitHub连接测试成功")
            return True
        else:
            print("  GitHub连接测试失败")
            return False
            
    except Exception as e:
        print(f"  GitHub连接测试异常: {e}")
        return False

def main():
    print("=" * 60)
    print("Day 1测试 - 修复版本")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("导入测试", test_imports),
        ("配置测试", test_config),
        ("GitHub连接测试", test_github_connection),
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
        print("\n 所有测试通过！")
        print("\n运行演示: python src/crawler/github_crawler.py")
    elif passed >= 2:
        print(f"\n  {total - passed} 个测试失败，但核心功能可能正常")
        print("\n仍然可以运行演示: python src/crawler/github_crawler.py")
    else:
        print(f"\n  {total - passed} 个测试失败，需要修复")
    
    print("=" * 60)

if __name__ == "__main__":
    main()