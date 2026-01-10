#!/usr/bin/env python3
"""
集成测试脚本 - 简化版
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

def test_data_integration():
    """测试数据集成"""
    print("=" * 60)
    print("  数据集成测试")
    print("=" * 60)
    
    try:
        # 首先检查是否有数据文件
        data_dir = project_root / "data"
        print(f"数据目录: {data_dir}")
        
        if data_dir.exists():
            files = list(data_dir.glob("*.json"))
            print(f"找到 {len(files)} 个数据文件:")
            for f in files:
                print(f"  - {f.name}")
        else:
            print("  数据目录不存在")
        
        # 导入并测试
        print("\n导入数据集成器...")
        from src.vector_store.data_integrator import DataIntegrator
        
        print("创建数据集成器...")
        integrator = DataIntegrator("test_integration")
        
        print("开始集成数据...")
        result = integrator.integrate_all_data("test-repo")
        
        print(f"\n  集成成功！")
        print(f"   总文档数: {result['total_documents']}")
        
        return True
        
    except ImportError as e:
        print(f"  导入失败: {e}")
        print("请确保在项目根目录运行")
        return False
    except Exception as e:
        print(f"  集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print(" 数据集成测试")
    
    # 运行测试
    success = test_data_integration()
    
    if success:
        print("\n 数据集成测试通过！")
        print("\n 现在可以:")
        print("1. 查看集成结果: python -c \"from src.vector_store.chroma_store import ChromaVectorStore; s=ChromaVectorStore('test_integration'); print(s.get_collection_info())\"")
        print("2. 运行搜索测试: python scripts/qa_test.py")
        print("3. 开始Day 5开发")
    else:
        print("\n  数据集成测试失败")
        print("请检查:")
        print("1. 是否在项目根目录运行？")
        print("2. 是否安装了所有依赖？")
        print("3. 是否有数据文件？")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()