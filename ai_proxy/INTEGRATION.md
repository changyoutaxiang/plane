# 集成指南

## 1. 将 AI 代理层集成到 Plane 项目

### 步骤 1: 注册 AI Proxy 应用

编辑 `/apps/api/plane/settings.py`：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'ai_proxy',
]

# AI 代理层配置
PLANE_API_KEY = "your_plane_api_key_here"
```

### 步骤 2: 添加 URL 路由

编辑 `/apps/api/plane/app/urls/project.py` 或创建新的 URL 文件：

```python
# ai_proxy/urls.py
from django.urls import path, include

urlpatterns = [
    # ... 其他 URL
    path("ai-proxy/", include("ai_proxy.api.urls")),
]
```

### 步骤 3: 在主 URL 中包含 AI Proxy 路由

编辑 `/apps/api/plane/app/urls/__init__.py`：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他 URL
    path("", include("ai_proxy.urls")),
]
```

### 步骤 4: 重启服务

```bash
# 重启 Docker 容器
docker-compose restart api
```

## 2. 配置 API 密钥

### 2.1 获取 Plane API 密钥

1. 登录 Plane 管理后台
2. 进入设置 → API 密钥
3. 创建新的 API 密钥
4. 复制密钥

### 2.2 设置环境变量

在 `/apps/api/.env` 中添加：

```
PLANE_API_KEY=pl_api_xxxxxxxxxxxxxxxxx
PLANE_BASE_URL=http://localhost:8000/api/v1
```

## 3. 测试 API

### 3.1 测试项目创建

```bash
curl -X POST http://localhost:8000/api/v1/ai-proxy/project/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "创建一个名为 Web前端重构 的项目",
    "workspace_slug": "default"
  }'
```

预期响应：

```json
{
  "success": true,
  "action": "create_project",
  "data": {
    "project_id": "prj_123",
    "name": "Web前端重构",
    "identifier": "WEB",
    "url": "http://localhost:8000/workspaces/default/projects/web/"
  },
  "message": "项目 'Web前端重构' 创建成功"
}
```

### 3.2 测试任务创建

```bash
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "在Web前端重构项目下创建一个任务，标题为优化登录页面，优先级为高",
    "workspace_slug": "default"
  }'
```

预期响应：

```json
{
  "success": true,
  "action": "create_issue",
  "data": {
    "issue_id": "iss_456",
    "name": "优化登录页面",
    "identifier": "WEB-123",
    "project_id": "prj_123",
    "url": "http://localhost:8000/workspaces/default/projects/web/issues/web-123/"
  },
  "message": "任务 '优化登录页面' 创建成功"
}
```

### 3.3 测试查询项目列表

```bash
curl http://localhost:8000/api/v1/ai-proxy/projects/?workspace_slug=default
```

预期响应：

```json
{
  "success": true,
  "count": 1,
  "projects": [
    {
      "id": "prj_123",
      "name": "Web前端重构",
      "identifier": "WEB"
    }
  ]
}
```

## 4. 与 Claude Code 集成

### 4.1 自然语言到 API 调用的流程

1. **用户输入**：用户用自然语言描述需求
   ```
   用户: "创建一个名为 '移动端开发' 的项目"
   ```

2. **Claude Code 解析**：Claude Code 将自然语言转换为 API 调用
   ```python
   # Claude Code 生成的代码
   import requests

   response = requests.post(
       "http://localhost:8000/api/v1/ai-proxy/project/create/",
       json={
           "natural_language": "创建一个名为 '移动端开发' 的项目",
           "workspace_slug": "default"
       }
   )
   ```

3. **API 执行**：AI 代理层调用 Plane API

4. **返回结果**：返回结构化的结果

### 4.2 完整示例脚本

```python
#!/usr/bin/env python3
"""
Claude Code 与 AI 代理层集成的示例
"""

import requests
import json

class PlaneAIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_project(self, natural_language: str, workspace_slug: str = "default"):
        """通过自然语言创建项目"""
        url = f"{self.base_url}/api/v1/ai-proxy/project/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_issue(self, natural_language: str, workspace_slug: str = "default"):
        """通过自然语言创建任务"""
        url = f"{self.base_url}/api/v1/ai-proxy/issue/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

# 使用示例
if __name__ == "__main__":
    client = PlaneAIClient("http://localhost:8000")

    # 创建项目
    project = client.create_project("创建一个名为 Web前端重构 的项目")
    print(f"项目创建成功: {project['data']['identifier']}")

    # 创建任务
    issue = client.create_issue(
        "在Web前端重构项目下创建一个任务，标题为优化登录页面，优先级为高"
    )
    print(f"任务创建成功: {issue['data']['identifier']}")
```

## 5. 错误处理

### 5.1 常见错误及解决方案

| 错误类型 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 401 Unauthorized | API 密钥错误或过期 | 检查 `PLANE_API_KEY` 配置 |
| 404 Not Found | 工作空间或项目不存在 | 确认 `workspace_slug` 正确 |
| 400 Bad Request | 自然语言无法解析 | 检查输入格式是否符合要求 |
| 500 Internal Server Error | API 调用失败 | 查看后端日志定位具体错误 |

### 5.2 日志查看

```bash
# 查看 API 日志
docker-compose logs -f api | grep "ai_proxy"

# 查看所有日志
docker-compose logs -f api
```

## 6. 性能优化

### 6.1 缓存策略

建议对以下数据进行缓存：
- 项目列表（每小时更新）
- 用户列表（每小时更新）
- 标签列表（每小时更新）

### 6.2 并发处理

- 默认支持多线程并发处理
- 可以通过 Celery 等队列系统异步处理

## 7. 安全注意事项

1. **API 密钥安全**：
   - 不要在前端暴露 API 密钥
   - 定期轮换 API 密钥

2. **输入验证**：
   - 限制自然语言长度（建议 500 字符以内）
   - 过滤敏感词汇

3. **权限控制**：
   - 为 AI 代理层创建专用的 API 密钥
   - 限制该密钥的权限范围（只读项目列表 + 写任务）

## 8. 扩展功能

### 8.1 支持的操作类型

- [x] 创建项目
- [x] 创建任务
- [ ] 更新任务
- [ ] 查询任务
- [ ] 删除任务
- [ ] 创建里程碑
- [ ] 分配用户

### 8.2 高级功能

- 支持批量操作
- 支持条件筛选
- 支持自定义字段
- 支持模板化操作
- 支持审批流程
