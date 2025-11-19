#!/usr/bin/env python3
"""
AI 代理层集成测试脚本
用于测试 MVP 功能的完整流程
"""

import sys
import requests
import json
from typing import Dict, Any


class AIProxyTester:
    """AI 代理层测试器"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.results = []

    def test_create_project(self, natural_language: str, workspace_slug: str = "default") -> Dict[str, Any]:
        """测试创建项目"""
        print(f"\n🔵 测试创建项目...")
        print(f"   输入: {natural_language}")

        url = f"{self.base_url}/api/v1/ai-proxy/project/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()

            if response.status_code == 201:
                print(f"   ✅ 成功: {result['data']['identifier']}")
                self.results.append(("创建项目", "PASS", result))
                return result
            else:
                print(f"   ❌ 失败: {result.get('error', '未知错误')}")
                self.results.append(("创建项目", "FAIL", result))
                return None

        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append(("创建项目", "ERROR", str(e)))
            return None

    def test_create_issue(self, natural_language: str, workspace_slug: str = "default") -> Dict[str, Any]:
        """测试创建任务"""
        print(f"\n🔵 测试创建任务...")
        print(f"   输入: {natural_language}")

        url = f"{self.base_url}/api/v1/ai-proxy/issue/create/"
        payload = {
            "natural_language": natural_language,
            "workspace_slug": workspace_slug
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()

            if response.status_code == 201:
                print(f"   ✅ 成功: {result['data']['identifier']}")
                self.results.append(("创建任务", "PASS", result))
                return result
            else:
                print(f"   ❌ 失败: {result.get('error', '未知错误')}")
                self.results.append(("创建任务", "FAIL", result))
                return None

        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append(("创建任务", "ERROR", str(e)))
            return None

    def test_query_projects(self, workspace_slug: str = "default") -> Dict[str, Any]:
        """测试查询项目列表"""
        print(f"\n🔵 测试查询项目列表...")

        url = f"{self.base_url}/api/v1/ai-proxy/projects/?workspace_slug={workspace_slug}"

        try:
            response = requests.get(url)
            result = response.json()

            if response.status_code == 200:
                print(f"   ✅ 成功: 找到 {result['count']} 个项目")
                self.results.append(("查询项目列表", "PASS", result))
                return result
            else:
                print(f"   ❌ 失败: {result.get('error', '未知错误')}")
                self.results.append(("查询项目列表", "FAIL", result))
                return None

        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append(("查询项目列表", "ERROR", str(e)))
            return None

    def run_mvp_tests(self):
        """运行 MVP 测试"""
        print("=" * 60)
        print("🚀 AI 代理层 MVP 功能测试")
        print("=" * 60)

        # 测试 1: 创建项目
        project = self.test_create_project(
            "创建一个名为 Web前端重构 的项目，描述为重构用户界面"
        )

        if not project:
            print("\n⚠️  创建项目失败，跳过后续测试")
            self.print_summary()
            return

        # 测试 2: 在项目下创建任务
        issue = self.test_create_issue(
            "在Web前端重构项目下创建一个任务，标题为优化登录页面加载速度，优先级为高"
        )

        # 测试 3: 查询项目列表
        projects = self.test_query_projects()

        self.print_summary()

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📊 测试摘要")
        print("=" * 60)

        passed = sum(1 for _, status, _ in self.results if status == "PASS")
        failed = sum(1 for _, status, _ in self.results if status in ["FAIL", "ERROR"])
        total = len(self.results)

        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"成功率: {passed/total*100 if total > 0 else 0:.1f}%")

        if failed > 0:
            print("\n失败的测试:")
            for test_name, status, error in self.results:
                if status != "PASS":
                    print(f"  - {test_name}: {status}")
                    if isinstance(error, dict):
                        print(f"    错误: {error.get('error')}")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        base_url = "http://localhost:8000"
    else:
        base_url = sys.argv[1]

    print(f"使用基础 URL: {base_url}")
    print(f"确保 Plane 服务正在运行在 {base_url}")

    tester = AIProxyTester(base_url)
    tester.run_mvp_tests()


if __name__ == "__main__":
    main()
