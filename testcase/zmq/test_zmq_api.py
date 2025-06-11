#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_zmq_api.py
@Time    : 2025/6/10 13:50
@Author  : zhouming
"""
import pytest
from loguru import logger
from core.zmq_client import ZMQClient
from testcase.base_testcase import BaseTestCase
from apis.zmq.example_page import ZMQExamplePage


sample_testcases = [
    {
        "用例名称": "sample zmq",
        "消息类型": "test",
        "发送消息": {"hello": "world"},
        "预期响应": {"status": "success"},
    }
]


class TestZMQAPI(BaseTestCase):
    """ZMQ API测试用例"""

    @pytest.fixture(scope="class")
    def zmq_page(self):
        """ZMQ页面对象fixture"""
        client = ZMQClient("localhost", 5555)
        page = ZMQExamplePage(client)
        page.connect = lambda **_: None
        page.handshake = lambda **_: None
        page.disconnect = lambda: None
        page.subscribe = lambda **_: None
        page.unsubscribe = lambda **_: None
        page.send_message = lambda **_: {"status": "success"}
        page.setup()
        yield page
        page.teardown()

    @pytest.mark.parametrize("testcase", sample_testcases)
    def test_zmq_api(self, testcase, zmq_page):
        """
        执行ZMQ API测试用例
        
        Args:
            testcase: 测试用例数据
            zmq_page: ZMQ页面对象
        """
        self.zmq_page = zmq_page
        self.run_testcase(testcase)

    def _execute_testcase(self, testcase):
        """执行ZMQ测试用例"""
        # 获取测试数据
        message_type = testcase['消息类型']
        send_message = testcase['发送消息']
        expected_response = testcase.get('预期响应', {})
        timeout = testcase.get('超时时间', 30)

        # 发送消息
        response = self.zmq_page.send_message(
            message_type=message_type,
            message=send_message,
            timeout=timeout
        )

        # 断言
        if expected_response:
            if isinstance(expected_response, dict):
                # 字典类型的预期响应
                for key, value in expected_response.items():
                    assert key in response, f"响应中缺少字段: {key}"
                    assert response[key] == value, \
                        f"字段 {key} 的值不匹配: 预期 {value}, 实际 {response[key]}"
            else:
                # 其他类型的预期响应（如字符串）
                assert response == expected_response, \
                    f"响应不匹配: 预期 {expected_response}, 实际 {response}"

        logger.info(f"测试用例执行成功: {testcase['用例名称']}")

    def _execute_setup(self, setup_data):
        """执行ZMQ测试前置条件"""
        if isinstance(setup_data, dict):
            # 处理连接等前置操作
            if setup_data.get('type') == 'connect':
                self.zmq_page.connect(
                    host=setup_data.get('host', 'localhost'),
                    port=setup_data.get('port', 5555)
                )
            # 处理订阅等前置操作
            elif setup_data.get('type') == 'subscribe':
                self.zmq_page.subscribe(
                    topic=setup_data['topic']
                )

    def _execute_teardown(self, teardown_data):
        """执行ZMQ测试后置条件"""
        if isinstance(teardown_data, dict):
            # 处理取消订阅等后置操作
            if teardown_data.get('type') == 'unsubscribe':
                self.zmq_page.unsubscribe(
                    topic=teardown_data['topic']
                )
            # 处理断开连接等后置操作
            elif teardown_data.get('type') == 'disconnect':
                self.zmq_page.disconnect()


# 使用示例
if __name__ == '__main__':
    # 运行测试
    # pytest test_zmq_api.py --excel=testcase/data/testcases.xlsx --protocol=ZMQ -v
    pass
