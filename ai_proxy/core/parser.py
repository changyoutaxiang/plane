"""
自然语言解析器
负责将自然语言通过 LLM 解析为结构化指令
"""

import json
import logging
from typing import Dict, Any, Optional
from ai_proxy.config import LLM_CONFIG, PROMPT_TEMPLATES

logger = logging.getLogger(__name__)


class NaturalLanguageParser:
    """自然语言解析器"""

    def __init__(self):
        self.llm_config = LLM_CONFIG
        self.prompt_templates = PROMPT_TEMPLATES

    def parse_to_structured(self, natural_language: str, action_type: str) -> Dict[str, Any]:
        """
        将自然语言解析为结构化指令

        Args:
            natural_language: 自然语言输入
            action_type: 操作类型（create_project, create_issue, update_issue）

        Returns:
            解析后的结构化指令
        """
        if action_type not in self.prompt_templates:
            raise ValueError(f"不支持的操作类型: {action_type}")

        # 构建 Prompt
        prompt = self.prompt_templates[action_type].format(
            natural_language=natural_language
        )

        # 调用 LLM（这里先用简单实现，后期可以替换为真实的 LLM API）
        try:
            # TODO: 替换为真实的 LLM API 调用
            # 例如: openai.ChatCompletion.create() 或 anthropic.messages.create()
            structured = self._mock_llm_call(prompt, action_type)

            # 验证和清理结果
            structured = self._validate_and_clean(structured, action_type)

            logger.info(f"解析成功: {action_type}")
            return structured

        except Exception as e:
            logger.error(f"解析失败: {e}")
            raise

    def _mock_llm_call(self, prompt: str, action_type: str) -> Dict[str, Any]:
        """
        模拟 LLM 调用（临时实现）
        实际项目中需要替换为真实的 LLM API
        """
        # 简单的规则匹配作为临时实现
        # 实际项目中需要调用 OpenAI/Anthropic 等 LLM

        if action_type == "create_project":
            # 简单的关键词提取
            import re

            # 提取项目名称（引号内的内容或"名为"后面的内容）
            name_match = re.search(r'名为\s*[的]?\s*["\']?([^"，,。\s]+)["\']?', prompt)
            name = name_match.group(1) if name_match else "未命名项目"

            # 提取描述
            desc_match = re.search(r'描述[为:]?\s*["\']?([^"，,。\s]+)["\']?', prompt)
            description = desc_match.group(1) if desc_match else ""

            # 生成标识符
            identifier = self._generate_identifier(name)

            return {
                "action": "create_project",
                "name": name,
                "description": description,
                "identifier": identifier,
            }

        elif action_type == "create_issue":
            # 提取任务标题
            title_match = re.search(r'标题[为:]?\s*["\']?([^"，,。\s]+)["\']?', prompt)
            title = title_match.group(1) if title_match else "未命名任务"

            # 提取项目名称
            project_match = re.search(r'项目[为:]?\s*["\']?([^"，,。\s]+)["\']?', prompt)
            project_name = project_match.group(1) if project_match else ""

            # 提取优先级
            priority = "medium"  # 默认优先级
            if "高" in prompt or "紧急" in prompt:
                priority = "high"
            elif "低" in prompt:
                priority = "low"

            return {
                "action": "create_issue",
                "title": title,
                "description": "",
                "project_name": project_name,
                "priority": priority,
                "assignee_name": "",
                "labels": [],
            }

        else:
            raise ValueError(f"未实现的动作类型: {action_type}")

    def _validate_and_clean(self, data: Dict[str, Any], action_type: str) -> Dict[str, Any]:
        """
        验证和清理解析结果
        """
        required_fields = {
            "create_project": ["action", "name"],
            "create_issue": ["action", "title", "project_name"],
            "update_issue": ["action", "issue_identifier"],
        }

        if action_type not in required_fields:
            raise ValueError(f"未知的动作类型: {action_type}")

        # 检查必需字段
        for field in required_fields[action_type]:
            if field not in data or not data[field]:
                raise ValueError(f"缺少必需字段: {field}")

        # 设置默认值
        if action_type == "create_project":
            if "identifier" not in data or not data["identifier"]:
                data["identifier"] = self._generate_identifier(data["name"])

        if action_type == "create_issue":
            if "priority" not in data:
                data["priority"] = "medium"
            if "labels" not in data:
                data["labels"] = []

        return data

    def _generate_identifier(self, name: str) -> str:
        """
        从项目名称生成标识符
        """
        # 提取首字母或前3个字母
        words = name.replace("-", " ").split()
        if words:
            identifier = "".join([word[0].upper() for word in words[:3]])
        else:
            identifier = name[:3].upper()

        return identifier[:6]  # 限制长度为6个字符
