"""
字段映射器
负责将结构化指令中的字段映射到 Plane 的实际 ID
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FieldMapper:
    """字段映射器"""

    def __init__(self):
        pass

    def map_project_name_to_id(self, project_name: str, workspace_slug: str, plane_api) -> Optional[str]:
        """
        将项目名称映射为项目 ID

        Args:
            project_name: 项目名称
            workspace_slug: 工作空间标识符
            plane_api: Plane API 客户端

        Returns:
            项目 ID 或 None
        """
        try:
            # 先尝试通过 API 查找项目
            projects = plane_api.list_projects(workspace_slug)

            # 精确匹配
            for project in projects:
                if project["name"] == project_name:
                    return project["id"]

            # 模糊匹配
            for project in projects:
                if project_name.lower() in project["name"].lower():
                    return project["id"]

            logger.warning(f"未找到项目: {project_name}")
            return None

        except Exception as e:
            logger.error(f"获取项目列表失败: {e}")
            return None

    def map_user_name_to_id(self, user_name: str, workspace_slug: str, plane_api) -> Optional[str]:
        """
        将用户名映射为用户 ID

        Args:
            user_name: 用户名
            workspace_slug: 工作空间标识符
            plane_api: Plane API 客户端

        Returns:
            用户 ID 或 None
        """
        try:
            # 通过 API 获取成员列表
            members = plane_api.list_members(workspace_slug)

            # 精确匹配
            for member in members:
                if member.get("display_name", "").strip() == user_name:
                    return member["id"]

            # 模糊匹配
            for member in members:
                if user_name.lower() in member.get("display_name", "").lower():
                    return member["id"]

            logger.warning(f"未找到用户: {user_name}")
            return None

        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return None

    def map_priority_to_value(self, priority: str) -> str:
        """
        将优先级映射为标准值

        Args:
            priority: 优先级（中文或英文）

        Returns:
            标准化的优先级
        """
        priority_map = {
            "低": "low",
            "中": "medium",
            "高": "high",
            "紧急": "urgent",
            "low": "low",
            "medium": "medium",
            "high": "high",
            "urgent": "urgent",
        }

        return priority_map.get(priority, "medium")

    def map_label_names_to_ids(self, label_names: list, workspace_slug: str, project_id: str, plane_api) -> list:
        """
        将标签名称列表映射为 ID 列表

        Args:
            label_names: 标签名称列表
            workspace_slug: 工作空间标识符
            project_id: 项目 ID
            plane_api: Plane API 客户端

        Returns:
            标签 ID 列表
        """
        try:
            # 获取项目标签
            labels = plane_api.list_labels(workspace_slug, project_id)

            label_ids = []
            for label_name in label_names:
                # 精确匹配
                for label in labels:
                    if label["name"] == label_name:
                        label_ids.append(label["id"])
                        break
                else:
                    # 未找到，记录但不中断
                    logger.warning(f"未找到标签: {label_name}")

            return label_ids

        except Exception as e:
            logger.error(f"获取标签列表失败: {e}")
            return []
