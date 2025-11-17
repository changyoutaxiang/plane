  
 目标：**做出“飞书一句话 → Plane 自动创建任务”的 MVP 级产品**。

分五大块，严格设计：

1. **完整系统架构（含数据流图 \+ 技术栈）**

2. **飞书端要做的配置（机器人、权限、回调）**

3. **n8n 工作流的完整设计（逐节点说明）**

4. **LLM 的 Prompt 结构规范（开发可直接拷贝）**

5. **Plane API 的调用规范（含字段映射、错误处理）**

---

# **🧱 1\. 系统架构图（高层、可直接给产品经理 & 研发）**

┌──────────────────────┐  
│      飞书群（用户）      │  
│  @AI PM: "创建任务..."   │  
└────────▲──────────┘  
         │ Webhook 回调（JSON）  
         ▼  
┌──────────────────────┐  
│       n8n Webhook     │  ←—— (入口触发)  
└────────▲──────────┘  
         │  
         ▼  
┌──────────────────────┐  
│   LLM（OpenAI Chat）  │ ←—— 自然语言解析  
│  NLP → JSON 结构体     │  
└────────▲──────────┘  
         │  
         ▼  
┌────────────────────────────┐  
│   n8n 逻辑层（数据清洗/映射） │  
│   \- 用户名 → Plane user\_id │  
│   \- 项目名 → project\_id    │  
└────────▲───────────────────┘  
         │  
         ▼  
┌────────────────────────────┐  
│       Plane API（REST）      │  
│ POST /issues/               │  
└────────▲───────────────────┘  
         │  
         ▼  
┌────────────────────────────┐  
│ 飞书群：机器人发送回执消息     │  
│ “已创建任务 \[WEB-123\] ..."  │  
└────────────────────────────┘

---

# **🎯 2\. 飞书端配置（必须严格按顺序）**

## **2.1 创建一个 飞书应用（推荐，而不是“自定义机器人”）**

这样你能：

* 接收消息事件（message.receive）

* 回复消息（通过 send API）

* 使用交互式卡片（未来扩展）

* 管理权限更灵活

### **需要的权限（Scopes）**

| 权限 | 用途 |
| ----- | ----- |
| `message.receive` | 机器人才能收到用户消息 |
| `im:message` | 用于向群发消息 |
| `im:message:send_as_bot` | 必须，不然不能发回执 |
| `group.chat:readonly` | 未来如果需要读取群基础信息 |

### **2.2 事件订阅**

订阅：

* **消息接收事件**（message.receive\_v1）

* 设置事件回调 URL \= `https://your-n8n-domain/webhook/feishu-ai-plane`

飞书会用 POST 携带如下 payload：

{  
  "schema": "...",  
  "header": {...},  
  "event": {  
    "message": {  
      "message\_id": "...",  
      "chat\_id": "...",  
      "sender": {...},  
      "content": "{\\"text\\": \\"@AI PM 创建一个 ...\\"}",  
      "mentions": \[...\]  
    }  
  }  
}

---

# **🔧 3\. n8n 工作流（这是整个 MVP 的核心）**

下面是一个实际开发可以直接据此搭建的“节点级设计”。

---

## **3.1 工作流结构总览**

\[Webhook Trigger\]  
      ↓  
\[节点 1：清洗飞书消息\]  
      ↓  
\[节点 2：OpenAI Chat Completion —— NLP 解析\]  
      ↓  
\[节点 3：Plane 字段映射（project/assignee）\]  
      ↓  
\[节点 4：HTTP → Plane 创建 Issue\]  
      ↓  
\[节点 5：生成飞书回执消息\]  
      ↓  
\[节点 6：HTTP → 飞书 BOT 发消息\]

---

## **🔨 3.2 每个节点的详细设计**

---

### **节点 0：Webhook Trigger**

配置：

* Method: `POST`

* Path: `/feishu-ai-plane`

* Response: `200 OK`（可以立即返回“received”，不用等待整个流程）

---

### **节点 1：清洗飞书消息**

处理原始 JSON：

* 取 `event.message.content`

* 飞书内容通常是 JSON，如：`{"text": "@AI PM 创建任务 登录页面太慢"}`

* 解析并取其中 `text`

处理 @bot 内容：

* 去掉前缀 "@AI PM"（飞书通常会在 mentions 中提供 bot 的 open\_id）

* 得到纯自然语言指令：

"创建任务 登录页面太慢，优先级高，指派给 Leon"

输出示例：

{  
  "plain\_text": "创建任务 登录页面太慢，优先级高，指派给 Leon",  
  "chat\_id": "oc\_xxxx",  
  "sender": "ou\_xxx"  
}

---

### **节点 2：OpenAI Chat Completion (NLP 解析)**

**Prompt 模板（强结构化）**：

你是一名专业项目经理助手，负责把中文自然语言指令解析为 Plane Issue 的结构化数据。

请严格输出 JSON 格式，字段如下：

{  
  "title": "简洁但有信息量的标题",  
  "description": "详细描述，可扩写为 PRD 级格式",  
  "priority": "low | medium | high | urgent（从自然语言推断）",  
  "project\_name": "用户提到的项目名，如 Web端、iOS、后台",  
  "assignee\_name": "用户提到的人名，如 Leon；如果未指定则返回空字符串",  
  "tags": \["可选标签数组，可从文本推断"\]  
}

输入为：

{{plain\_text}}

注意：  
\- 必须是可解析的 JSON。  
\- 不要输出任何额外文字。

输出示例：

{  
  "title": "登录页面加载过慢",  
  "description": "用户反馈登录页面在弱网环境下加载超过 5 秒，需要性能优化。",  
  "priority": "high",  
  "project\_name": "Web端",  
  "assignee\_name": "Leon",  
  "tags": \["性能", "登录"\]  
}

---

### **节点 3：字段映射（项目 → ID、人员 → ID）**

Plane API 需要：

* `project_id`

* `assignees: [user_id]`

* `labels: [label_id]`

在 n8n 里你可以配置一个“Key-Value 表”（或 ENV JSON）：

{  
  "projects": {  
    "Web端": 12,  
    "iOS": 19,  
    "后台": 27  
  },  
  "assignees": {  
    "Leon": "usr\_123456",  
    "李雷": "usr\_654321"  
  }  
}

这个节点执行：

project\_id \= kv.projects\[project\_name\]  
assignee\_id \= kv.assignees\[assignee\_name\] || null

---

### **节点 4：调用 Plane API 创建 Issue**

HTTP Node 配置：

| 字段 | 值 |
| ----- | ----- |
| Method | POST |
| URL | `https://your-plane-domain/api/v1/workspaces/:workspace_slug/projects/{{project_id}}/issues/` |
| Headers | `X-API-Key: plane_api_xxx` |

**Body 示例：**

{  
  "name": "登录页面加载过慢",  
  "description": "用户反馈登录页面在弱网环境下超过 5 秒...",  
  "priority": "high",  
  "assignees": \["usr\_123456"\],  
  "labels": \[\],  
  "estimate\_point": null  
}

API 返回：

{  
  "id": "iss\_112233",  
  "name": "登录页面加载过慢",  
  "identifier": "WEB-123"  
}

---

### **节点 5：生成飞书回执消息（构造 JSON）**

飞书机器人消息 JSON：

{  
  "msg\_type": "interactive",  
  "card": {  
    "config": { "wide\_screen\_mode": true },  
    "header": {  
      "template": "blue",  
      "title": { "tag": "plain\_text", "content": "Plane 任务已创建" }  
    },  
    "elements": \[  
      {  
        "tag": "div",  
        "text": {  
          "tag": "lark\_md",  
          "content": "\*\*{{identifier}} {{title}}\*\*\\n项目：{{project\_name}}\\n优先级：{{priority}}"  
        }  
      },  
      {  
        "tag": "action",  
        "actions": \[  
          {  
            "tag": "button",  
            "text": { "tag": "plain\_text", "content": "打开任务" },  
            "type": "primary",  
            "url": "https://your-plane-domain/workspaces/.../issues/{{identifier}}"  
          }  
        \]  
      }  
    \]  
  }  
}

---

### **节点 6：调用飞书 Send message API 发送回执**

URL：

https://open.feishu.cn/open-apis/im/v1/messages?receive\_id\_type=chat\_id

Headers：

Authorization: Bearer {{tenant\_access\_token}}  
Content-Type: application/json

Body：

{  
  "receive\_id": "{{chat\_id}}",  
  "msg\_type": "interactive",  
  "content": "{{stringified card json}}"  
}

---

# **📘 4\. LLM Prompt：开发人员可直接使用的版本**

我整理成正式文档版格式，便于在代码中使用：

---

## **Prompt（系统角色）**

你是一个专业的任务解析器（Task Parser），专门把中文自然语言指令解析成结构化的 Plane Issue 数据。  
 输出必须严格为 JSON，可被机器解析，不允许输出多余任何内容。

---

## **Prompt（用户输入）**

请将以下自然语言转换成 Plane Issue JSON：

要求输出 JSON：  
{  
  "title": "string",  
  "description": "string",  
  "priority": "low|medium|high|urgent",  
  "project\_name": "string",  
  "assignee\_name": "string",  
  "tags": \[\]  
}

输入内容：  
{{plain\_text}}

---

# **🚀 5\. Plane API 部分（最小可用说明）**

Plane API 创建任务：

POST /api/v1/workspaces/{workspace\_slug}/projects/{project\_id}/issues/

必要字段：

| 字段 | 类型 | 说明 |
| ----- | ----- | ----- |
| name | string | 任务标题 |
| description | string | 任务描述 |
| priority | enum | low/medium/high/urgent |
| assignees | array of string | 用户 ID |
| labels | array of number | 标签 ID |

最常见错误：

| 错误 | 原因 |
| ----- | ----- |
| 401 Unauthorized | API Key 错误 |
| 404 project not found | project\_id 映射错误 |
| 422 validation error | priority 值不合法 |

---

