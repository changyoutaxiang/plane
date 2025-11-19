"""
AI 代理层配置
"""

# LLM 配置
LLM_CONFIG = {
    "provider": "openai",  # 或 "claude", "anthropic"
    "model": "gpt-4",      # 或 "claude-3-sonnet"
    "temperature": 0.1,    # 低温度确保输出稳定
    "max_tokens": 1000,
}

# 字段映射配置
FIELD_MAPPINGS = {
    "projects": {
        # 项目名 -> 项目 ID 映射（运行时动态获取）
        # "Web前端": 12,
        # "iOS": 19,
    },
    "users": {
        # 用户名 -> 用户 ID 映射（运行时动态获取）
        # "张三": "usr_123",
        # "李四": "usr_456",
    },
    "priorities": {
        "低": "low",
        "中": "medium",
        "高": "high",
        "紧急": "urgent",
    },
    "states": {
        # 状态名 -> 状态 ID 映射
        "待办": "todo",
        "进行中": "in_progress",
        "完成": "done",
    }
}

# API 配置
API_CONFIG = {
    "plane_base_url": "http://localhost:8000/api/v1",
    "timeout": 30,
    "retry_attempts": 3,
}

# Prompt 模板
PROMPT_TEMPLATES = {
    "create_project": """
你是一个专业的项目管理助手，负责将自然语言转换为结构化的项目创建指令。

请严格输出 JSON 格式，不要包含任何其他文字：

{
  "action": "create_project",
  "name": "项目名称（从自然语言中提取）",
  "description": "项目描述（可适当扩展和完善）",
  "identifier": "项目标识符（3-5个字母，可从项目名提取）",
  "emoji": "项目图标（可选）"
}

输入的自然语言：
{natural_language}

示例：
输入："创建一个名为 Web前端重构 的项目，描述为重构用户界面"
输出：{{"action": "create_project", "name": "Web前端重构", "description": "重构用户界面", "identifier": "WEB"}}
""",

    "create_issue": """
你是一个专业的任务管理助手，负责将自然语言转换为结构化的任务创建指令。

请严格输出 JSON 格式，不要包含任何其他文字：

{
  "action": "create_issue",
  "title": "任务标题",
  "description": "任务描述（可适当扩展）",
  "project_name": "项目名称",
  "priority": "low|medium|high|urgent",
  "assignee_name": "指派给谁（可选）",
  "labels": ["标签1", "标签2"],
  "due_date": "截止日期（可选，YYYY-MM-DD格式）"
}

输入的自然语言：
{natural_language}

示例：
输入："在Web前端项目下创建一个任务，标题为优化登录页面，优先级为高"
输出：{{"action": "create_issue", "title": "优化登录页面", "project_name": "Web前端", "priority": "high"}}
""",

    "update_issue": """
你是一个专业的任务管理助手，负责将自然语言转换为结构化的任务更新指令。

请严格输出 JSON 格式，不要包含任何其他文字：

{
  "action": "update_issue",
  "issue_identifier": "任务编号（如 WEB-123）",
  "updates": {
    "title": "新标题（可选）",
    "description": "新描述（可选）",
    "priority": "新优先级（可选）",
    "state": "新状态（可选）"
  }
}

输入的自然语言：
{natural_language}
"""
}
