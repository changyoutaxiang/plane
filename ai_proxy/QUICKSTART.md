# 🚀 快速开始指南

## 5 分钟体验 AI 代理层

按照以下步骤快速体验 AI 代理层的功能。

### 前提条件

- ✅ Plane 项目正在本地运行 (http://localhost:8000)
- ✅ 拥有 Plane API 密钥
- ✅ Python 3.8+ 环境

### 步骤 1: 准备配置

在 `/apps/api/.env` 文件中添加：

```bash
PLANE_API_KEY=your_plane_api_key_here
PLANE_BASE_URL=http://localhost:8000/api/v1
```

### 步骤 2: 创建测试脚本

```python
#!/usr/bin/env python3
# test_quickstart.py

import requests
import json

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/ai-proxy"

def test_create_project():
    """测试创建项目"""
    print("\n1️⃣ 测试创建项目")
    url = f"{BASE_URL}{API_PREFIX}/project/create/"
    payload = {
        "natural_language": "创建一个名为 'AI 测试项目' 的项目",
        "workspace_slug": "default"
    }

    response = requests.post(url, json=payload)
    result = response.json()

    if response.status_code == 201:
        print(f"   ✅ 成功: {result['data']['identifier']}")
        return result['data']
    else:
        print(f"   ❌ 失败: {result.get('error')}")
        return None

def test_create_issue(project_data):
    """测试创建任务"""
    print("\n2️⃣ 测试创建任务")
    url = f"{BASE_URL}{API_PREFIX}/issue/create/"
    payload = {
        "natural_language": f"在{project_data['name']}项目下创建一个任务：标题为测试自然语言创建功能",
        "workspace_slug": "default"
    }

    response = requests.post(url, json=payload)
    result = response.json()

    if response.status_code == 201:
        print(f"   ✅ 成功: {result['data']['identifier']}")
        return result['data']
    else:
        print(f"   ❌ 失败: {result.get('error')}")
        return None

def main():
    print("=" * 60)
    print("🚀 AI 代理层快速体验")
    print("=" * 60)

    # 测试创建项目
    project = test_create_project()
    if not project:
        print("\n⚠️  项目创建失败，退出测试")
        return

    # 测试创建任务
    issue = test_create_issue(project)
    if not issue:
        print("\n⚠️  任务创建失败")
        return

    print("\n" + "=" * 60)
    print("✨ 所有测试通过!")
    print("=" * 60)
    print(f"\n创建的资源:")
    print(f"  项目: {project['name']} ({project['identifier']})")
    print(f"  任务: {issue['name']} ({issue['identifier']})")

if __name__ == "__main__":
    main()
```

### 步骤 3: 运行测试

```bash
# 确保 Plane 服务正在运行
docker-compose up -d

# 运行测试脚本
python test_quickstart.py
```

### 步骤 4: 查看结果

如果成功，你应该看到类似输出：

```
============================================================
🚀 AI 代理层快速体验
============================================================

1️⃣ 测试创建项目
   ✅ 成功: AI

2️⃣ 测试创建任务
   ✅ 成功: AI-1

============================================================
✨ 所有测试通过!
============================================================

创建的资源:
  项目: AI 测试项目 (AI)
  任务: 测试自然语言创建功能 (AI-1)
```

### 步骤 5: 验证创建的资源

访问 Plane 控制台验证：
- 打开 http://localhost:8000
- 进入 "AI 测试项目"
- 查看 "测试自然语言创建功能" 任务

## 🎯 实际使用示例

### 示例 1: 创建新功能项目

```bash
curl -X POST http://localhost:8000/api/v1/ai-proxy/project/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "创建一个名为 支付系统 的项目，描述为开发支付功能模块",
    "workspace_slug": "default"
  }'
```

### 示例 2: 报告 Bug

```bash
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "在支付系统项目下创建一个任务：标题为修复登录页面崩溃问题，优先级为紧急",
    "workspace_slug": "default"
  }'
```

### 示例 3: 创建开发任务

```bash
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "在支付系统项目下创建一个任务：标题为实现微信支付接口，优先级为高",
    "workspace_slug": "default"
  }'
```

## 💡 高级使用

### 使用 Python 客户端

```python
from plane_ai_client import PlaneAIClient

client = PlaneAIClient("http://localhost:8000")

# 创建项目
project = client.create_project_by_nl(
    "创建一个名为 '移动端开发' 的项目"
)

# 创建多个任务
tasks = [
    "在移动端开发项目下创建任务：标题为实现用户注册功能",
    "在移动端开发项目下创建任务：标题为实现用户登录功能",
    "在移动端开发项目下创建任务：标题为实现用户资料页面"
]

for task_nl in tasks:
    client.create_issue_by_nl(task_nl)
    print(f"✅ 已创建: {task_nl}")
```

### 批量创建

```python
import json

# 从文件读取任务列表
with open("tasks.json", "r") as f:
    tasks = json.load(f)

for task in tasks:
    client.create_issue_by_nl(
        f"在{task['project']}项目下创建任务：标题为{task['title']}，优先级为{task['priority']}"
    )
```

## 🛠️ 故障排除

### 问题 1: 401 Unauthorized

**原因**: API 密钥错误或未配置

**解决**:
1. 检查 `/apps/api/.env` 中的 `PLANE_API_KEY`
2. 确认 API 密钥有效
3. 重启服务: `docker-compose restart api`

### 问题 2: 404 Not Found

**原因**: 工作空间或项目不存在

**解决**:
1. 确认 `workspace_slug` 正确（默认为 "default"）
2. 确认项目名称正确
3. 先创建项目再创建任务

### 问题 3: 500 Internal Server Error

**原因**: AI 代理层内部错误

**解决**:
1. 查看 API 日志: `docker-compose logs -f api | grep ai_proxy`
2. 检查配置是否正确
3. 尝试使用简单的自然语言

### 问题 4: 解析失败

**原因**: 自然语言格式不符合预期

**解决**:
1. 使用明确的表述，例如：
   - "创建一个名为 X 的项目"
   - "在 X 项目下创建一个任务：标题为 Y"
2. 避免使用模糊的词汇

## 📚 更多资源

- 📖 [完整文档](README_DETAILED.md) - 查看详细技术文档
- 🔧 [集成指南](INTEGRATION.md) - 了解如何集成到现有项目
- 🧪 [测试脚本](test_integration.py) - 运行完整的测试套件
- 💡 [使用示例](example_usage.py) - 学习更多使用场景

## 🎉 下一步

1. **集成到你的工作流** - 将 AI 代理层集成到你的日常开发中
2. **扩展功能** - 添加更多操作类型（更新、删除、查询等）
3. **使用真实 LLM** - 集成 GPT-4 或 Claude 提升解析准确性
4. **创建自动化脚本** - 使用 AI 代理层批量处理任务

---

**🚀 开始体验 AI 驱动的项目管理吧！**
