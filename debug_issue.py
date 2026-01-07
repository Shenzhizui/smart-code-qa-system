# debug_issue.py
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.github_crawler import GitHubIssue

# 测试直接创建GitHubIssue对象
print("测试GitHubIssue类创建...")
try:
    # 创建一个简单的Issue对象
    test_issue = GitHubIssue(
        number=1,
        title="测试Issue",
        body="测试内容",
        state="open",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        user="testuser",
        assignees=[],
        labels=[],
        comments=0,
        url="https://github.com/test/repo/issues/1"
    )
    print(f"✅ GitHubIssue创建成功: {test_issue}")
    print(f"   标题: {test_issue.title}")
    print(f"   编号: {test_issue.number}")
except Exception as e:
    print(f"❌ 创建失败: {e}")
    print(f"   错误类型: {type(e).__name__}")

# 测试to_dict方法
print("\n测试to_dict方法...")
try:
    issue_dict = test_issue.to_dict()
    print(f"✅ to_dict成功: {issue_dict}")
except Exception as e:
    print(f"❌ to_dict失败: {e}")