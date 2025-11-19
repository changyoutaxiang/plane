#!/usr/bin/env python3
"""
AI 代理层使用示例
展示如何在实际项目中使用 AI 代理层
"""

import requests
import json
from typing import Optional, Dict, Any


class PlaneAIClient:
    """
    Plane AI 客户端

    这是一个高级客户端，提供简洁的 API 用于与 AI 代理层交互。
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            base_url: Plane 服务的基础 URL
            api_key: API 密钥（可选）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

        # 如果有 API 密钥，设置默认 header
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })

    # ========== 项目相关 ==========

    def create_project_by_nl(self, natural_language: str, workspace_slug: str = "default") -> Dict[str, Any]:
        """
        通过自然语言创建项目

        Args:
            natural_language: 自然语言描述，如 "创建一个名为 'Web前端' 的项目"
            workspace_slug: 工作空间标识符

        Returns:
            创建的项目信息

        Raises:
            requests.HTTPError: 当 API 调用失败时
        """
        url = f"{self.base_url}/api/v1/ai-proxy/project/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def list_projects(self, workspace_slug: str = "default") -> Dict[str, Any]:
        """
        获取项目列表

        Args:
            workspace_slug: 工作空间标识符

        Returns:
            项目列表

        Raises:
            requests.HTTPError: 当 API 调用失败时
        """
        url = f"{self.base_url}/api/v1/ai-proxy/projects/"
        params = {"workspace_slug": workspace_slug}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # ========== 任务相关 ==========

    def create_issue_by_nl(self, natural_language: str, workspace_slug: str = "default") -> Dict[str, Any]:
        """
        通过自然语言创建任务

        Args:
            natural_language: 自然语言描述，如 "在Web前端项目下创建一个任务：标题为优化登录页面"
            workspace_slug: 工作空间标识符

        Returns:
            创建的任务信息

        Raises:
            requests.HTTPError: 当 API 调用失败时
        """
        url = f"{self.base_url}/api/v1/ai-proxy/issue/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    # ========== 工具方法 ==========

    def print_project(self, project: Dict[str, Any]):
        """打印项目信息"""
        data = project.get("data", {})
        print(f"✅ 项目创建成功!")
        print(f"   ID: {data.get('project_id')}")
        print(f"   名称: {data.get('name')}")
        print(f"   标识符: {data.get('identifier')}")
        print(f"   URL: {data.get('url')}")

    def print_issue(self, issue: Dict[str, Any]):
        """打印任务信息"""
        data = issue.get("data", {})
        print(f"✅ 任务创建成功!")
        print(f"   ID: {data.get('issue_id')}")
        print(f"   名称: {data.get('name')}")
        print(f"   编号: {data.get('identifier')}")
        print(f"   URL: {data.get('url')}")

    def print_projects(self, projects_data: Dict[str, Any]):
        """打印项目列表"""
        projects = projects_data.get("projects", [])
        print(f"📁 项目列表 (共 {len(projects)} 个):")
        for project in projects:
            print(f"   - {project['name']} ({project['identifier']})")


def main():
    """使用示例"""
    # 初始化客户端
    client = PlaneAIClient("http://localhost:8000")

    print("=" * 60)
    print("🚀 AI 代理层使用示例")
    print("=" * 60)

    try:
        # 示例 1: 创建项目
        print("\n1️⃣ 创建项目")
        project = client.create_project_by_nl(
            "创建一个名为 '移动端开发' 的项目，描述为开发移动端应用"
        )
        client.print_project(project)

        # 示例 2: 创建另一个项目
        print("\n2️⃣ 创建另一个项目")
        project2 = client.create_project_by_nl(
            "创建一个名为 'API服务' 的项目，描述为重构后端API接口"
        )
        client.print_project(project2)

        # 示例 3: 查询项目列表
        print("\n3️⃣ 查询项目列表")
        projects = client.list_projects()
        client.print_projects(projects)

        # 示例 4: 创建任务
        print("\n4️⃣ 创建任务")
        issue = client.create_issue_by_nl(
            "在移动端开发项目下创建一个任务：标题为实现用户登录功能，优先级为高"
        )
        client.print_issue(issue)

        # 示例 5: 创建另一个任务
        print("\n5️⃣ 创建另一个任务")
        issue2 = client.create_issue_by_nl(
            "在移动端开发项目下创建一个任务：标题为优化首页加载速度，优先级为中"
        )
        client.print_issue(issue2)

        print("\n" + "=" * 60)
        print("✨ 所有示例执行完成!")
        print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        print("请确保:")
        print("  1. Plane 服务正在运行")
        print("  2. AI 代理层已正确集成")
        print("  3. API 配置正确")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")


if __name__ == "__main__":
    main()
