---

## **🎯 一、MVP 的目标和边界**

### **1.1 目标（一句话）**

做一个“AI 项目经理”，能在 **飞书里听得懂人话、在 Plane 里自动建/维护任务、每天自动写项目日报**。

### **1.2 MVP 只做三件事**

1. **飞书一句话 → Plane 自动创建高质量任务**

2. **AI 自动帮现有任务补充描述 / 拆子任务**

3. **每天固定时间，AI 自动生成 Plane 项目的中文日报发到飞书群**

这三件事情做到体验顺滑，你的“AI PM”就已经很有存在感了。

---

## **🏗 二、整体架构设计（工程视角）**

**组件：**

* Plane（自托管 or Cloud 都可）

* 飞书（一个群 \+ 自建应用 / 自定义机器人）

* n8n（自动化中枢）

* OpenAI / ChatGPT（LLM 服务）

**数据流：**

1. 飞书消息 ➜ n8n ➜ LLM ➜ Plane API ➜ 飞书回执

2. Plane 定时数据 ➜ n8n ➜ LLM ➜ 飞书日报

3. Plane Issue ➜ n8n ➜ LLM ➜ Plane Issue/子任务更新

可以脑补一个逻辑图：

飞书（输入 & 输出界面）  
 ⬇️  
 n8n（路由 \+ 调度）  
 ⬅️➡️ Plane（任务与文档数据库）  
 ⬇️  
 OpenAI（大脑，负责理解 & 生成内容）

---

## **🧩 三、功能 1：飞书一句话 → Plane 自动建任务**

### **3.1 用户体验（从人的角度）**

在某个项目群里：

你：`@AI PM 创建一个登录页面太慢的 bug，优先级高，派给 Leon，放到「Web端」项目`

机器人几秒后回复：  
 ✅ 已创建任务：\[WEB-123 登录页面加载过慢\]

* 项目：Web端

* 优先级：High

* 负责人：Leon

* 链接：[https://your-plane-domain/.../issues/WEB-123](https://your-plane-domain/.../issues/WEB-123)

### **3.2 技术流程（n8n 工作流）**

1. **触发：飞书回调 / Webhook**

   * 在飞书开放平台配置一个“应用机器人”或在群里用“自定义机器人 \+ 交互卡片回调”。

   * 飞书将包含消息内容/用户信息的 JSON POST 给 n8n 的 Webhook 节点。

2. **节点 1：解析飞书消息**

   * 提取文本，比如：  
      `创建一个登录页面太慢的 bug，优先级高，派给 Leon，放到 Web端 项目`

   * 也可以要求用户使用简单格式，如：  
      `新任务 标题: XXX 项目: XXX 优先级: P1 负责人: XXX`

3. **节点 2：调用 LLM 解析成结构化 JSON**

   * 用 OpenAI Chat Completions 节点，Prompt 类似：

你是一个项目管理助手，负责把自然语言指令解析成 Plane 的 Issue 数据。

输入是一句中文指令，例如：  
“创建一个登录页面太慢的 bug，优先级高，派给 Leon，放到 Web端 项目”

请严格输出 JSON，字段：  
{  
  "title": "任务标题（简短，但有信息量）",  
  "description": "详细描述（可以从指令中扩展出背景、期望行为、复现步骤）",  
  "project": "项目名称（例如：Web端）",  
  "priority": "low | medium | high | urgent",  
  "assignee\_name": "负责人名字（如原文中的 Leon）",  
  "tags": \["从内容中推断的一些标签，数组，可以为空"\]  
}

只输出 JSON，不要多余文字。

4.   
5. **节点 3：映射到 Plane 的内部 ID**

   * 用一个 `IF / Switch` 或小代码节点，把：

     * `project` 名 → Plane 的 `project_id`

     * `assignee_name` → Plane 用户的 ID

   * 这些映射可以配置在 n8n 的环境变量 / 数据表里（比如 `Leon -> user_123`）。

6. **节点 4：调用 Plane API 创建 Issue**

   * n8n 的 HTTP Request 节点：

POST https://your-plane-domain/api/v1/workspaces/:workspace-slug/projects/:project\_id/issues/

Headers:  
  X-API-Key: plane\_api\_xxx  
  Content-Type: application/json

Body:  
{  
  "name": "{{ $json.title }}",  
  "description": "{{ $json.description }}",  
  "priority": "{{ $json.priority }}",  
  "assignees": \["{{ $json.assignee\_id }}"\],  
  "labels": \[...\],  
  ...  
}

7.   
8. **节点 5：飞书回执**

   * 接收 Plane 返回的 Issue key / id。

   * 再用 HTTP 节点把一条确认消息发回飞书群：  
      `✅ 已创建任务 [WEB-123 登录页面加载过慢]`

至此，你已经完成了：**自然语言 → 任务结构化 → Plane 创建 → 飞书反馈** 的闭环。

---

## **🧩 四、功能 2：AI 自动帮现有任务“补全 & 拆分”**

这个功能是为了让 AI 帮你整理 backlog、提高任务质量。

### **4.1 用户体验**

* 产品经理/开发写了一个非常简略的 Issue：

   标题：登录页面优化  
   描述：页面有点慢，之后再看

* 每天晚上 n8n 跑一遍：

  * 找到所有“描述太短 / 没有子任务”的 Issue；

  * 喂给 LLM，请它写详细说明 \+ 推荐拆分为 3–5 个子任务；

  * 自动更新 Issue 描述 & 创建子 Issue。

* 第二天你打开 Plane，发现：

  * 描述已经变成“规范 PRD 风格”；

  * 底下多了几个清晰的子任务（前端优化、后端缓存、监控指标等）。

### **4.2 技术流程**

1. **触发：n8n Cron（例如每天 20:00）**

2. **节点 1：拉取 Plane 中“目标项目的 Issues”**

   * GET `/issues/?project_id=xxx&per_page=100`

   * 只选那些：

     * `description` 为空 or 太短；

     * 没有子任务；

3. **节点 2：For Each Issue 调用 LLM**

   * Prompt 示例：

你是高级产品经理和高级工程师。  
现在我给你一个任务标题 \+ 简短描述，请你完成两件事：

1\. 写出一段更完整的任务描述（背景、现状问题、预期结果、验收标准）。  
2\. 拆分出 3\~6 个合理的子任务，适合给工程师执行。

请输出 JSON：  
{  
  "improved\_description": "更完整的描述",  
  "subtasks": \[  
    { "title": "...", "suggested\_owner\_role": "前端/后端/测试/产品" },  
    ...  
  \]  
}

任务信息：  
标题: {{issue.name}}  
原始描述: {{issue.description}}

4.   
5. **节点 3：更新 Plane Issue 描述**

   * PATCH `/issues/:id/`

   * 把 `improved_description` 写回 `description`。

6. **节点 4：在 Plane 中创建子任务**

   * 循环 `subtasks` 数组，调用 POST `/issues/` 并设置 `parent_id` 为原任务 ID。

7. **节点 5：在父 Issue 里加一条 AI 注释**

   * 可调用评论 API 或在 description 尾部加一段：

      *由 AI 帮你补全描述并生成子任务，编辑前请检查是否符合实际需求。*

---

## **🧩 五、功能 3：AI 项目日报（Plane ➜ 飞书）**

### **5.1 用户体验**

每天 18:30，飞书项目群自动出现一条消息：

📊 《今日项目简报 \- Web端》

* 新增任务：8 个（其中高优先级 3 个）

* 完成任务：5 个

* 延迟任务：2 个（原因建议择期讨论）

* 当前迭代进度：预计完成度 72%

* 可能的风险：登录性能优化进度滞后、注册流程需求频繁变更

* 建议关注：

  * \[WEB-123 登录页面加载过慢\]

  * \[WEB-98 新用户注册转化率低\]

### **5.2 技术流程**

1. **触发：n8n Cron（每天 18:00，Asia/Singapore 时区）**

2. **节点 1：从 Plane 抓数据**

   * 拉今天（或最近 24h）的 Issue 活动：

     * 新建 / 变更状态 / 关闭 / 被重新打开

   * 拉当前 cycle 的进度：

     * 总任务数

     * 已完成数

     * 剩余工作量

3. **节点 2：整理成“事实 JSON”**

   * 在 n8n 中先不让 LLM自由发挥，而是拼一个结构化 summary，例如：

{  
  "date": "2025-11-14",  
  "new\_issues": \[...\],  
  "closed\_issues": \[...\],  
  "delayed\_issues": \[...\],  
  "cycle": {  
    "name": "Sprint 12",  
    "progress": 0.72,  
    "start\_date": "...",  
    "end\_date": "..."  
  }  
}

4.   
5. **节点 3：调用 LLM 生成自然语言日报**

   * Prompt 示例：

你是一个资深项目经理，负责根据项目数据写一份简短的中文日报。

下面是原始数据（JSON）：  
{{json数据}}

写作要求：  
\- 用中文输出，不超过 300 字。  
\- 结构包括：总体概览 / 关键进展 / 风险 &建议。  
\- 对任务可以点名 2\~5 个最值得关注的任务（用任务 ID \+ 标题）。  
\- 语气专业但不死板。

只输出日报内容。

6.   
7. **节点 4：发到飞书群**

   * 使用机器人 Webhook 推送文本 / 富文本消息即可。

---

## **🔐 六、安全 & 配置建议**

* 把以下敏感配置放到 n8n 的环境变量中：

  * OpenAI API Key

  * Plane API Key

  * 飞书 Bot Webhook / App Secret

* 对 LLM 的输入做必要过滤：

  * 避免传输不该“出公司”的信息（比如客户隐私字段）

* 给 Plane 中 AI 生成内容打一个“AI 标记”：

  * 比如统一在自动写入的 description 末尾加一小行注释，方便人工识别。

---

## **🧭 七、实施顺序（我建议的落地路线）**

1. **第 1 步：打通 Plane API \+ n8n**

   * 完成一次“手动调用 Plane API 创建 Issue”的 n8n Flow。

2. **第 2 步：实现功能 1（飞书一句话建任务）**

   * 这是最直观的“哇，这东西活了”的时刻。

3. **第 3 步：实现功能 3（日报）**

   * 团队会开始依赖它，每天都看到 AI 的价值。

4. **第 4 步：实现功能 2（AI 补全任务 & 拆子任务）**

   * 这个相当于“加智能涂层”，对任务质量提升很明显。  
