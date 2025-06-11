#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_http_api.py
@Time    : 2025/6/10 17:05
@Author  : zhouming
"""
import pytest
from testcase.base_testcase import BaseTestCase
from core.http_client import HTTPClient
from apis.http.http_page import HTTPPage
from loguru import logger


class TestHTTPAPI(BaseTestCase):
    """HTTP API测试用例"""

    @pytest.fixture(scope="class")
    def http_page(self):
        """HTTP页面对象fixture"""
        client = HTTPClient("http://api.example.com")
        page = HTTPPage(client)
        page.setup()
        yield page
        page.teardown()

    @pytest.mark.parametrize("testcase", [], indirect=True)
    def test_http_api(self, testcase, http_page):
        """
        执行HTTP API测试用例

        Args:
            testcase: 测试用例数据
            http_page: HTTP页面对象
        """
        self.run_testcase(testcase)

    def _execute_testcase(self, testcase):
        """执行HTTP测试用例"""
        # 获取测试数据
        method = testcase['请求方法']
        url = testcase['URL']
        headers = testcase.get('请求头', {})
        params = testcase.get('请求参数', {})
        expected_status = testcase.get('预期状态码')
        expected_response = testcase.get('预期响应', {})

        # 执行请求
        response = self.http_page.send_request(
            method=method,
            url=url,
            headers=headers,
            params=params
        )

        # 断言
        if expected_status:
            assert response.status_code == expected_status, \
                f"状态码不匹配: 预期 {expected_status}, 实际 {response.status_code}"

        if expected_response:
            actual_response = response.json()
            for key, value in expected_response.items():
                assert key in actual_response, f"响应中缺少字段: {key}"
                assert actual_response[key] == value, \
                    f"字段 {key} 的值不匹配: 预期 {value}, 实际 {actual_response[key]}"

        logger.info(f"测试用例执行成功: {testcase['用例名称']}")

    def _execute_setup(self, setup_data):
        """执行HTTP测试前置条件"""
        if isinstance(setup_data, dict):
            # 处理登录等前置操作
            if setup_data.get('type') == 'login':
                self.http_page.login(
                    username=setup_data['username'],
                    password=setup_data['password']
                )

    def _execute_teardown(self, teardown_data):
        """执行HTTP测试后置条件"""
        if isinstance(teardown_data, dict):
            # 处理登出等后置操作
            if teardown_data.get('type') == 'logout':
                self.http_page.logout()


# 使用示例
if __name__ == '__main__':
    # 运行测试
    # pytest test_http_api.py --excel=testcase/data/http_testcases.xlsx --protocol=HTTP -v
    pass
