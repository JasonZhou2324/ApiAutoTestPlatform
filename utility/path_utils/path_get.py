#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : path_get.py
@Time    : 2025/6/10 14:45
@Author  : zhouming
"""
from pathlib import Path

PROJECT_NAME = "ApiAutoTestPlatform"


def find_project_root() -> Path:
    """获取项目根目录"""
    project_root = Path(__file__).resolve().parents[2]
    if project_root.name != PROJECT_NAME:
        raise RuntimeError(f"Expected project root '{PROJECT_NAME}', but found '{project_root.name}'")
    return project_root


def get_template_path() -> Path:
    """获取测试用例模板路径"""
    project_root = find_project_root()
    template_path = project_root / 'testcase' / 'templates' / 'testcase_template.xlsx'
    template_path.parent.mkdir(parents=True, exist_ok=True)
    return template_path
