"""
AI 代理层 URL 路由
"""

from django.urls import path
from .views import (
    CreateProjectAPIView,
    CreateIssueAPIView,
    QueryProjectsAPIView,
)

urlpatterns = [
    # 创建项目
    path(
        "project/create/",
        CreateProjectAPIView.as_view(),
        name="ai-proxy-create-project"
    ),

    # 创建任务
    path(
        "issue/create/",
        CreateIssueAPIView.as_view(),
        name="ai-proxy-create-issue"
    ),

    # 查询项目列表
    path(
        "projects/",
        QueryProjectsAPIView.as_view(),
        name="ai-proxy-projects"
    ),
]
