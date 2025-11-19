# Plane AI 代理层 - 详细文档

## 🎯 项目目标

这个 AI 代理层旨在让 Claude Code 作为"智能中枢"，通过自然语言操作替代传统 GUI 界面，实现项目管理的高效化和智能化。

## 🏗 系统架构

### 核心组件

```
┌─────────────────────┐
│   用户 / Claude Code │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AI 代理层 API      │  ← RESTful 接口
│  - /project/create │
│  - /issue/create   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   核心模块           │
│  ┌───────────────┐  │
│  │ Parser        │  │  ← 自然语言解析
│  │ Mapper        │  │  ← 字段映射
│  │ Executor      │  │  ← API 执行
│  └───────────────┘  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Plane API         │
│  - /api/v1/workspaces/
│  - /api/v1/projects/
│  - /api/v1/issues/
└─────────────────────┘
```

### 数据流

1. **输入阶段**
   - 用户提供自然语言描述
   - 例如："在Web前端项目下创建一个任务，优化登录页面"

2. **解析阶段**
   - `Parser` 将自然语言转换为结构化指令
   - 例如：`{"action": "create_issue", "title": "优化登录页面", "project_name": "Web前端"}`

3. **映射阶段**
   - `Mapper` 将名称映射为实际 ID
   - 例如：`project_name` → `project_id`

4. **执行阶段**
   - `Executor` 调用 Plane API
   - 创建任务并返回结果

5. **输出阶段**
   - 返回结构化的结果
   - 例如：`{"success": true, "data": {...}}`

## 📋 MVP 功能清单

### ✅ 已实现功能

1. **创建项目**
   - 输入：自然语言描述
   - 输出：项目 ID、标识符、URL

2. **创建任务**
   - 输入：自然语言描述（包含项目名）
   - 输出：任务 ID、编号、URL

3. **查询项目列表**
   - 输入：工作空间标识符
   - 输出：项目列表

### 🚧 计划实现功能

4. **更新任务**
   - 修改任务属性
   - 更新状态、优先级等

5. **查询任务**
   - 根据条件筛选任务
   - 批量查询

6. **删除任务/项目**
   - 安全删除操作

7. **批量操作**
   - 批量创建任务
   - 批量更新状态

## 🔧 技术实现

### 1. 自然语言解析器 (Parser)

**职责**：将自然语言转换为结构化指令

**当前实现**：
- 基于规则匹配的简单解析
- 支持项目创建和任务创建

**未来升级**：
- 集成真实的 LLM (GPT-4, Claude)
- 更精确的意图识别
- 支持更多操作类型

```python
# 示例解析
输入: "创建一个名为 Web前端重构 的项目"
输出:
{
  "action": "create_project",
  "name": "Web前端重构",
  "description": "",
  "identifier": "WEB"
}
```

### 2. 字段映射器 (Mapper)

**职责**：将名称映射为 ID

**支持映射**：
- 项目名称 → 项目 ID
- 用户名 → 用户 ID
- 优先级 → 标准值
- 标签名称 → 标签 ID

```python
# 示例映射
输入: project_name="Web前端重构"
输出: project_id="prj_123"
```

### 3. API 执行器 (Executor)

**职责**：实际调用 Plane API

**封装操作**：
- 创建项目
- 创建任务
- 查询列表
- 字段映射

```python
# 示例执行
payload = {
    "name": "Web前端重构",
    "description": "...",
    "identifier": "WEB"
}
response = requests.post(
    f"{base_url}/workspaces/{workspace}/projects/",
    json=payload,
    headers={"Authorization": f"Bearer {api_key}"}
)
```

## 📚 API 参考

### 创建项目

```http
POST /api/v1/ai-proxy/project/create/
Content-Type: application/json

{
    "natural_language": "创建一个名为 '项目名称' 的项目",
    "workspace_slug": "default"
}
```

**响应示例**：
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

### 创建任务

```http
POST /api/v1/ai-proxy/issue/create/
Content-Type: application/json

{
    "natural_language": "在项目名项目下创建一个任务，标题为xxx，优先级为高",
    "workspace_slug": "default"
}
```

**响应示例**：
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

### 查询项目列表

```http
GET /api/v1/ai-proxy/projects/?workspace_slug=default
```

**响应示例**：
```json
{
    "success": true,
    "count": 2,
    "projects": [
        {
            "id": "prj_123",
            "name": "Web前端重构",
            "identifier": "WEB"
        },
        {
            "id": "prj_456",
            "name": "移动端开发",
            "identifier": "MOB"
        }
    ]
}
```

## 💡 使用场景

### 场景 1: 开发新功能

```bash
# 1. 创建项目
curl -X POST http://localhost:8000/api/v1/ai-proxy/project/create/ \
  -d '{"natural_language": "创建一个名为 支付系统 的项目", "workspace_slug": "default"}'

# 2. 在项目中创建任务
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -d '{"natural_language": "在支付系统项目下创建任务：标题为接入微信支付，优先级为高"}'
```

### 场景 2: 处理 bug

```bash
# 创建 bug 任务
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -d '{"natural_language": "在Web前端项目下创建一个任务：标题为修复登录页面崩溃问题，优先级为紧急"}'
```

### 场景 3: 敏捷开发

```bash
# 创建冲刺任务
curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -d '{"natural_language": "在移动端开发项目下创建任务：标题为实现用户注册功能，优先级为中"}'

curl -X POST http://localhost:8000/api/v1/ai-proxy/issue/create/ \
  -d '{"natural_language": "在移动端开发项目下创建任务：标题为实现用户登录功能，优先级为高"}'
```

## 🔄 与 Claude Code 的集成

### 方式 1: 直接 API 调用

```python
import requests

# Claude Code 可以直接生成这样的代码
response = requests.post(
    "http://localhost:8000/api/v1/ai-proxy/project/create/",
    json={
        "natural_language": "创建一个名为 '新项目' 的项目",
        "workspace_slug": "default"
    }
)
project = response.json()
```

### 方式 2: 使用客户端库

```python
from plane_ai_client import PlaneAIClient

client = PlaneAIClient("http://localhost:8000")
project = client.create_project_by_nl("创建一个名为 '新项目' 的项目")
```

### 方式 3: 自动化脚本

```python
# 批量创建项目
projects = ["项目A", "项目B", "项目C"]
for project_name in projects:
    client.create_project_by_nl(f"创建一个名为 {project_name} 的项目")
```

## 🐛 调试指南

### 开启详细日志

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 查看解析日志
logger = logging.getLogger("ai_proxy.core.parser")
logger.setLevel(logging.DEBUG)

# 查看执行日志
logger = logging.getLogger("ai_proxy.core.executor")
logger.setLevel(logging.DEBUG)
```

### 测试解析器

```python
from ai_proxy.core.parser import NaturalLanguageParser

parser = NaturalLanguageParser()
result = parser.parse_to_structured(
    "创建一个名为 Web前端 的项目",
    "create_project"
)
print(json.dumps(result, indent=2))
```

### 测试映射器

```python
from ai_proxy.core.mapper import FieldMapper
from ai_proxy.core.executor import PlaneAPIExecutor

mapper = FieldMapper()
executor = PlaneAPIExecutor("http://localhost:8000", "your_api_key")

project_id = mapper.map_project_name_to_id("Web前端", "default", executor)
print(f"项目 ID: {project_id}")
```

## 🚀 性能优化

### 1. 缓存策略

建议实现以下缓存：

- 项目列表缓存（TTL: 1小时）
- 用户列表缓存（TTL: 1小时）
- 标签列表缓存（TTL: 1小时）

### 2. 异步处理

对于批量操作，建议使用 Celery：

```python
from celery import shared_task

@shared_task
def create_issues_batch(issues: list):
    for issue_data in issues:
        create_issue(issue_data)
```

### 3. 限制速率

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', block=True)
def create_issue(request):
    # 实现
    pass
```

## 🔒 安全最佳实践

1. **API 密钥管理**
   - 使用环境变量存储密钥
   - 定期轮换密钥
   - 限制密钥权限

2. **输入验证**
   - 限制输入长度
   - 过滤敏感词
   - 验证输入格式

3. **权限控制**
   - 区分只读和写权限
   - 按用户限制操作范围
   - 记录操作日志

4. **错误处理**
   - 不暴露内部错误信息
   - 记录错误日志
   - 优雅降级

## 📈 路线图

### 短期目标 (1-2周)

- [x] MVP 功能（创建项目、创建任务）
- [x] 基础 API 文档
- [ ] 与真实 LLM 集成（GPT-4/Claude）
- [ ] 更完善的错误处理

### 中期目标 (1-2个月)

- [ ] 支持更多操作（更新、查询、删除）
- [ ] 批量操作支持
- [ ] 缓存机制
- [ ] 完整的测试套件
- [ ] 性能优化

### 长期目标 (3-6个月)

- [ ] 与更多平台集成（飞书、Slack、Teams）
- [ ] 可视化配置界面
- [ ] 操作模板和宏
- [ ] 团队协作功能
- [ ] 移动端支持

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python -m pytest tests/

# 5. 提交代码
git add .
git commit -m "feat: add new feature"
git push origin main
```

### 代码规范

- 遵循 PEP 8
- 添加类型提示
- 编写单元测试
- 更新文档

## 📞 支持

如有问题，请：

1. 查阅文档
2. 搜索现有 Issue
3. 创建新的 Issue
4. 联系维护者

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 LICENSE 文件。

---

**🎉 享受 AI 驱动的项目管理体验！**
