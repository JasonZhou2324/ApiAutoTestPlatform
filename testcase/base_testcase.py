#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : base_testcase.py
@Time    : 2025/6/10 13:45
@Author  : zhouming
"""
import pytest
from loguru import logger
from typing import Dict, Any
from utility.excel_utils.excel_reader import ExcelTestcaseReader


class BaseTestCase:
    """测试用例基类"""

    @pytest.fixture(scope="class")
    def excel_reader(self, request):
        """Excel读取器fixture"""
        excel_path = request.config.getoption("--excel")
        if not excel_path:
            raise ValueError("请通过--excel参数指定测试用例文件路径")
        return ExcelTestcaseReader(excel_path)

    @pytest.fixture(scope="class")
    def testcases(self, excel_reader, request):
        """测试用例数据fixture"""
        protocol_type = request.config.getoption("--protocol", "HTTP")
        return excel_reader.get_testcases(protocol_type)

    @staticmethod
    def setup_method(method):
        """测试方法执行前的设置"""
        logger.info(f"开始执行测试方法: {method.__name__}")

    @staticmethod
    def teardown_method(method):
        """测试方法执行后的清理"""
        logger.info(f"测试方法执行完成: {method.__name__}")

    def run_testcase(self, testcase: Dict[str, Any]):
        """
        执行测试用例

        Args:
            testcase: 测试用例数据
        """
        logger.info(f"执行测试用例: {testcase['用例名称']}")

        # 执行前置条件
        if testcase.get('前置条件'):
            self._execute_setup(testcase['前置条件'])

        try:
            # 执行测试步骤
            self._execute_testcase(testcase)

            # 执行后置条件
            if testcase.get('后置条件'):
                self._execute_teardown(testcase['后置条件'])

        except Exception as e:
            logger.error(f"测试用例执行失败: {str(e)}")
            raise

    def _execute_setup(self, setup_data: Dict[str, Any]):
        """执行前置条件"""
        logger.info("执行前置条件")
        # 由子类实现具体的前置条件执行逻辑
        pass

    def _execute_testcase(self, testcase: Dict[str, Any]):
        """执行测试用例"""
        # 由子类实现具体的测试用例执行逻辑
        pass

    def _execute_teardown(self, teardown_data: Dict[str, Any]):
        """执行后置条件"""
        logger.info("执行后置条件")
        # 由子类实现具体的后置条件执行逻辑
        pass


def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--excel",
        action="store",
        default=None,
        help="测试用例Excel文件路径"
    )
    parser.addoption(
        "--protocol",
        action="store",
        default="HTTP",
        choices=["HTTP", "ZMQ", "Socket"],
        help="测试协议类型"
    )
