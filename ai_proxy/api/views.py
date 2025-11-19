"""
AI 代理层 API 视图
提供自然语言到 Plane API 的转换接口
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from ai_proxy.core.parser import NaturalLanguageParser
from ai_proxy.core.mapper import FieldMapper
from ai_proxy.core.executor import PlaneAPIExecutor
from ai_proxy.config import API_CONFIG

logger = logging.getLogger(__name__)


class CreateProjectAPIView(APIView):
    """创建项目 API"""

    def __init__(self):
        super().__init__()
        self.parser = NaturalLanguageParser()
        self.mapper = FieldMapper()
        self.executor = PlaneAPIExecutor(
            base_url=API_CONFIG["plane_base_url"],
            api_key=settings.PLANE_API_KEY  # 需要在 settings 中配置
        )

    def post(self, request):
        """
        通过自然语言创建项目

        请求体示例：
        {
            "natural_language": "创建一个名为 Web前端重构 的项目，描述为重构用户界面",
            "workspace_slug": "default"
        }
        """
        try:
            # 获取输入
            natural_language = request.data.get("natural_language", "").strip()
            workspace_slug = request.data.get("workspace_slug", "default")

            if not natural_language:
                return Response(
                    {"error": "natural_language 不能为空"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 解析自然语言
            structured = self.parser.parse_to_structured(
                natural_language,
                action_type="create_project"
            )

            # 执行创建项目
            result = self.executor.create_project(workspace_slug, structured)

            # 构造返回结果
            response_data = {
                "success": True,
                "action": "create_project",
                "data": {
                    "project_id": result.get("id"),
                    "name": result.get("name"),
                    "identifier": result.get("identifier"),
                    "url": result.get("url"),
                },
                "message": f"项目 '{result.get('name')}' 创建成功"
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"参数错误: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            return Response(
                {"error": f"创建项目失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateIssueAPIView(APIView):
    """创建任务 API"""

    def __init__(self):
        super().__init__()
        self.parser = NaturalLanguageParser()
        self.mapper = FieldMapper()
        self.executor = PlaneAPIExecutor(
            base_url=API_CONFIG["plane_base_url"],
            api_key=settings.PLANE_API_KEY
        )

    def post(self, request):
        """
        通过自然语言创建任务

        请求体示例：
        {
            "natural_language": "在Web前端项目下创建一个任务，标题为优化登录页面，优先级为高",
            "workspace_slug": "default"
        }
        """
        try:
            # 获取输入
            natural_language = request.data.get("natural_language", "").strip()
            workspace_slug = request.data.get("workspace_slug", "default")

            if not natural_language:
                return Response(
                    {"error": "natural_language 不能为空"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 解析自然语言
            structured = self.parser.parse_to_structured(
                natural_language,
                action_type="create_issue"
            )

            # 映射项目名称到 ID
            project_id = self.mapper.map_project_name_to_id(
                structured["project_name"],
                workspace_slug,
                self.executor
            )

            if not project_id:
                return Response(
                    {"error": f"未找到项目: {structured['project_name']}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 映射用户名到 ID
            assignee_id = None
            if structured.get("assignee_name"):
                assignee_id = self.mapper.map_user_name_to_id(
                    structured["assignee_name"],
                    workspace_slug,
                    self.executor
                )

            # 映射优先级
            priority = self.mapper.map_priority_to_value(
                structured.get("priority", "medium")
            )

            # 映射标签名称到 ID
            label_ids = []
            if structured.get("labels"):
                label_ids = self.mapper.map_label_names_to_ids(
                    structured["labels"],
                    workspace_slug,
                    project_id,
                    self.executor
                )

            # 准备任务数据
            issue_data = {
                "title": structured["title"],
                "description": structured.get("description", ""),
                "priority": priority,
                "assignee_id": assignee_id,
                "label_ids": label_ids,
                "due_date": structured.get("due_date"),
            }

            # 执行创建任务
            result = self.executor.create_issue(
                workspace_slug,
                project_id,
                issue_data
            )

            # 构造返回结果
            response_data = {
                "success": True,
                "action": "create_issue",
                "data": {
                    "issue_id": result.get("id"),
                    "name": result.get("name"),
                    "identifier": result.get("identifier"),
                    "project_id": project_id,
                    "url": result.get("url"),
                },
                "message": f"任务 '{result.get('name')}' 创建成功"
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"参数错误: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            return Response(
                {"error": f"创建任务失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryProjectsAPIView(APIView):
    """查询项目列表 API"""

    def __init__(self):
        super().__init__()
        self.executor = PlaneAPIExecutor(
            base_url=API_CONFIG["plane_base_url"],
            api_key=settings.PLANE_API_KEY
        )

    def get(self, request):
        """
        获取项目列表

        查询参数：
        - workspace_slug: 工作空间标识符（默认: default）
        """
        try:
            workspace_slug = request.query_params.get("workspace_slug", "default")

            projects = self.executor.list_projects(workspace_slug)

            # 简化返回数据
            simplified = [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "identifier": p.get("identifier"),
                }
                for p in projects
            ]

            return Response({
                "success": True,
                "count": len(simplified),
                "projects": simplified
            })

        except Exception as e:
            logger.error(f"获取项目列表失败: {e}")
            return Response(
                {"error": f"获取项目列表失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
