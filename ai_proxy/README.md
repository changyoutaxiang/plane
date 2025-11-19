# Plane AI 代理层 (MVP)

## 架构概述

这个 AI 代理层作为"智能中枢"，将自然语言指令转换为 Plane API 调用，实现 GUI 的替代操作。

### 数据流

```
用户输入自然语言
    ↓
Claude Code (自然语言 → 结构化指令)
    ↓
AI 代理层 (解析指令 → 映射到 Plane API)
    ↓
Plane API (执行 CRUD 操作)
    ↓
返回结构化结果
```

### MVP 功能

1. **创建项目**
   - 输入: "创建一个名为 'Web前端重构' 的项目，描述为 '重构用户界面以提升用户体验'，在 '默认工作空间' 中"
   - 输出: 项目 ID、标识符、URL

2. **在项目下创建任务**
   - 输入: "在 'Web前端重构' 项目下创建一个任务：标题为 '优化登录页面加载速度'，描述为 '当前登录页面加载时间超过3秒，需要优化'，优先级为 '高'，指派给 '张三'"
   - 输出: 任务 ID、任务编号、URL

## 目录结构

```
ai_proxy/
├── core/
│   ├── parser.py          # 自然语言解析器
│   ├── mapper.py          # 字段映射器
│   └── executor.py        # API 执行器
├── api/
│   ├── endpoints.py       # API 端点定义
│   └── views.py           # Django 视图
├── models/
│   └── ai_command.py      # AI 指令模型
└── config.py              # 配置
```

## 使用示例

### 创建项目

```bash
curl -X POST http://localhost:8000/ai-proxy/project/create \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "创建一个名为 Web前端重构的项目，描述为重构用户界面",
    "workspace_slug": "default"
  }'
```

### 创建任务

```bash
curl -X POST http://localhost:8000/ai-proxy/issue/create \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "在Web前端重构项目下创建一个任务，标题为优化登录页面，优先级为高",
    "workspace_slug": "default"
  }'
```
