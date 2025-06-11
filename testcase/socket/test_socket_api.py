#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_socket_api.py
@Time    : 2025/6/10 17:07
@Author  : zhouming
"""
import json
import pytest
from testcase.base_testcase import BaseTestCase
from core.socket_client import SocketClient
from apis.socket.socket_page import SocketPage
from loguru import logger


sample_testcases = [
    {
        "用例名称": "sample socket",
        "消息格式": "JSON",
        "发送消息": {"ping": "pong"},
        "预期响应": {"res": "ok"},
    }
]


class TestSocketAPI(BaseTestCase):
    """Socket API测试用例"""

    @pytest.fixture(scope="class")
    def socket_page(self):
        """Socket页面对象fixture"""
        client = SocketClient("localhost", 8888)
        page = SocketPage(client)
        page.connect = lambda **_: None
        page.handshake = lambda **_: None
        page.disconnect = lambda: None
        page.send_message = lambda **_: {"res": "ok"}
        page.setup()
        yield page
        page.teardown()

    @pytest.mark.parametrize("testcase", sample_testcases)
    def test_socket_api(self, testcase, socket_page):
        """
        执行Socket API测试用例

        Args:
            testcase: 测试用例数据
            socket_page: Socket页面对象
        """
        self.socket_page = socket_page
        self.run_testcase(testcase)

    def _execute_testcase(self, testcase):
        """执行Socket测试用例"""
        # 获取测试数据
        message_format = testcase['消息格式']  # 如：JSON, XML, 二进制等
        send_message = testcase['发送消息']
        expected_response = testcase.get('预期响应', {})
        timeout = testcase.get('超时时间', 30)

        # 根据消息格式处理发送消息
        if message_format.upper() == 'JSON':
            if isinstance(send_message, str):
                try:
                    send_message = json.loads(send_message)
                except json.JSONDecodeError:
                    logger.warning(f"JSON解析失败，将使用原始字符串: {send_message}")

        # 发送消息
        response = self.socket_page.send_message(
            message=send_message,
            message_format=message_format,
            timeout=timeout
        )

        # 根据消息格式处理响应
        if message_format.upper() == 'JSON':
            try:
                if isinstance(response, str):
                    response = json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"响应JSON解析失败: {response}")

        # 断言
        if expected_response:
            if isinstance(expected_response, dict):
                # 字典类型的预期响应
                for key, value in expected_response.items():
                    assert key in response, f"响应中缺少字段: {key}"
                    assert response[key] == value, \
                        f"字段 {key} 的值不匹配: 预期 {value}, 实际 {response[key]}"
            else:
                # 其他类型的预期响应
                assert response == expected_response, \
                    f"响应不匹配: 预期 {expected_response}, 实际 {response}"

        logger.info(f"测试用例执行成功: {testcase['用例名称']}")

    def _execute_setup(self, setup_data):
        """执行Socket测试前置条件"""
        if isinstance(setup_data, dict):
            # 处理连接等前置操作
            if setup_data.get('type') == 'connect':
                self.socket_page.connect(
                    host=setup_data.get('host', 'localhost'),
                    port=setup_data.get('port', 8888)
                )
            # 处理握手等前置操作
            elif setup_data.get('type') == 'handshake':
                self.socket_page.handshake(
                    protocol=setup_data.get('protocol', 'TCP'),
                    timeout=setup_data.get('timeout', 30)
                )

    def _execute_teardown(self, teardown_data):
        """执行Socket测试后置条件"""
        if isinstance(teardown_data, dict):
            # 处理断开连接等后置操作
            if teardown_data.get('type') == 'disconnect':
                self.socket_page.disconnect()
            # 处理清理会话等后置操作
            elif teardown_data.get('type') == 'cleanup':
                self.socket_page.cleanup_session()


# 使用示例
if __name__ == '__main__':
    # 运行测试
    # pytest test_socket_api.py --excel=testcase/data/testcases.xlsx --protocol=Socket -v
    pass
