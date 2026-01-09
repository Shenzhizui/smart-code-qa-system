"""
网络环境设置脚本
"""
import os
import subprocess
import sys

def setup_network_environment():
    """设置网络环境"""
    print("🔧 设置网络环境")
    print("=" * 50)
    
    # 方法1：设置镜像源（推荐国内用户）
    print("\n1. 设置HuggingFace镜像源...")
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    print(f"   ✅ 设置 HF_ENDPOINT = {os.environ['HF_ENDPOINT']}")
    
    # 方法2：检查常见代理端口
    print("\n2. 检查代理设置...")
    proxy_ports = [7890, 7891, 1080, 1081, 1087, 2080]
    
    for port in proxy_ports:
        proxy_url = f"http://127.0.0.1:{port}"
        try:
            import requests
            # 测试代理是否可用
            test_response = requests.get('http://www.google.com', 
                                       proxies={'http': proxy_url, 'https': proxy_url},
                                       timeout=3)
            if test_response.status_code:
                print(f"   ✅ 发现可用代理: {proxy_url}")
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                break
        except:
            continue
    
    # 方法3：设置pip镜像源
    print("\n3. 设置pip镜像源...")
    pip_mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.aliyun.com/pypi/simple",
        "https://pypi.mirrors.ustc.edu.cn/simple"
    ]
    
    # 创建pip配置文件
    pip_config_content = """
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
"""
    
    # 对于Windows用户
    if sys.platform == 'win32':
        pip_config_path = os.path.expanduser("~/pip/pip.ini")
        pip_dir = os.path.dirname(pip_config_path)
        os.makedirs(pip_dir, exist_ok=True)
        
        with open(pip_config_path, 'w') as f:
            f.write(pip_config_content)
        print(f"   ✅ 创建pip配置文件: {pip_config_path}")
    
    # 方法4：设置git镜像（如果使用git下载模型）
    print("\n4. 设置git镜像源...")
    git_commands = [
        "git config --global url.https://hf-mirror.com/.insteadof https://huggingface.co/",
        "git config --global url.https://ghproxy.com/https://github.com/.insteadof https://github.com/"
    ]
    
    for cmd in git_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"   ✅ 执行: {cmd}")
        except:
            print(f"   ⚠️  跳过: {cmd}")
    
    print("\n" + "=" * 50)
    print("✅ 网络环境设置完成")
    
    # 显示当前设置
    print("\n📋 当前环境变量:")
    print(f"   HF_ENDPOINT: {os.environ.get('HF_ENDPOINT')}")
    print(f"   HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"   HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    
    return True

def test_connection():
    """测试连接"""
    print("\n🔍 测试网络连接...")
    
    test_urls = [
        ("HuggingFace镜像", "https://hf-mirror.com"),
        ("GitHub", "https://github.com"),
        ("PyPI镜像", "https://pypi.tuna.tsinghua.edu.cn")
    ]
    
    import requests
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"   ✅ {name}: {url} - 状态码 {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {url} - 失败 ({str(e)[:50]})")
    
    print("\n🎯 建议:")
    print("1. 如果所有测试都失败，请检查网络连接")
    print("2. 如果部分失败，我们会使用备用方案")
    print("3. 可以尝试使用VPN或代理")

if __name__ == "__main__":
    setup_network_environment()
    test_connection()