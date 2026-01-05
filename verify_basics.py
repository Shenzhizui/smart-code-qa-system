# verify_basics.py - 基础验证
import sys
import os

print("=" * 60)
print("基础环境验证")
print("=" * 60)

# 1. Python环境
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"工作目录: {os.getcwd()}")

# 2. 检查虚拟环境
if "venv" in sys.executable:
    print("✅ 在虚拟环境中")
else:
    print("⚠ 可能不在虚拟环境中")

# 3. 测试关键模块导入
print("\n测试关键模块导入:")
modules_to_test = [
    "sentence_transformers",
    "chromadb",
    "llama_index",
    "fastapi",
    "github"
]

all_imports_ok = True
for module in modules_to_test:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")
        all_imports_ok = False

# 4. 测试配置文件
print("\n测试配置文件:")
try:
    import config.settings as settings
    print(f"  ✅ 导入成功")
    print(f"    项目: {settings.PROJECT_NAME}")
    print(f"    版本: {settings.VERSION}")
    print(f"    主机: {settings.HOST}:{settings.PORT}")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    all_imports_ok = False

# 5. 测试功能
print("\n测试基本功能:")
if all_imports_ok:
    try:
        # 测试sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode("test")
        print(f"  ✅ 嵌入模型: 工作正常 (维度: {len(embedding)})")
        
        # 测试chromadb
        import chromadb
        print(f"  ✅ 向量数据库: 已安装")
        
    except Exception as e:
        print(f"  ❌ 功能测试失败: {e}")
        all_imports_ok = False

# 总结
print("\n" + "=" * 60)
if all_imports_ok:
    print("🎉 所有基础验证通过！")
    print("\n下一步:")
    print("1. 编辑 .env 文件，填入GitHub Token")
    print("2. 开始第2周开发任务")
else:
    print("⚠ 部分验证未通过，需要修复")
print("=" * 60)