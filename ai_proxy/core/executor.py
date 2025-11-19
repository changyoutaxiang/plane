"""
API 执行器
负责执行实际的 Plane API 调用
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PlaneAPIExecutor:
    """Plane API 执行器"""

    def __init__(self, base_url: str, api_key: str):
        """
        初始化 API 执行器

        Args:
            base_url: Plane API 基础 URL
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = None

    def create_project(self, workspace_slug: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建项目

        Args:
            workspace_slug: 工作空间标识符
            project_data: 项目数据

        Returns:
            创建的项目信息
        """
        import requests

        url = f"{self.base_url}/workspaces/{workspace_slug}/projects/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "name": project_data["name"],
            "description": project_data.get("description", ""),
            "identifier": project_data.get("identifier", ""),
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"创建项目成功: {result.get('id')}")
            return result

        except requests.RequestException as e:
            logger.error(f"创建项目失败: {e}")
            raise

    def create_issue(self, workspace_slug: str, project_id: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建任务

        Args:
            workspace_slug: 工作空间标识符
            project_id: 项目 ID
            issue_data: 任务数据

        Returns:
            创建的任务信息
        """
        import requests

        url = f"{self.base_url}/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "name": issue_data["title"],
            "description": issue_data.get("description", ""),
            "priority": issue_data.get("priority", "medium"),
        }

        # 添加指派者
        if "assignee_id" in issue_data and issue_data["assignee_id"]:
            payload["assignees"] = [issue_data["assignee_id"]]

        # 添加标签
        if "label_ids" in issue_data and issue_data["label_ids"]:
            payload["labels"] = issue_data["label_ids"]

        # 添加截止日期
        if "due_date" in issue_data and issue_data["due_date"]:
            payload["target_date"] = issue_data["due_date"]

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"创建任务成功: {result.get('id')}")
            return result

        except requests.RequestException as e:
            logger.error(f"创建任务失败: {e}")
            raise

    def list_projects(self, workspace_slug: str) -> list:
        """
        获取项目列表

        Args:
            workspace_slug: 工作空间标识符

        Returns:
            项目列表
        """
        import requests

        url = f"{self.base_url}/workspaces/{workspace_slug}/projects/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"获取项目列表成功: {len(result)} 个项目")
            return result

        except requests.RequestException as e:
            logger.error(f"获取项目列表失败: {e}")
            return []

    def list_members(self, workspace_slug: str) -> list:
        """
        获取成员列表

        Args:
            workspace_slug: 工作空间标识符

        Returns:
            成员列表
        """
        import requests

        url = f"{self.base_url}/workspaces/{workspace_slug}/members/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"获取成员列表成功: {len(result)} 个成员")
            return result

        except requests.RequestException as e:
            logger.error(f"获取成员列表失败: {e}")
            return []

    def list_labels(self, workspace_slug: str, project_id: str) -> list:
        """
        获取项目标签列表

        Args:
            workspace_slug: 工作空间标识符
            project_id: 项目 ID

        Returns:
            标签列表
        """
        import requests

        url = f"{self.base_url}/workspaces/{workspace_slug}/projects/{project_id}/labels/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"获取标签列表成功: {len(result)} 个标签")
            return result

        except requests.RequestException as e:
            logger.error(f"获取标签列表失败: {e}")
            return []
