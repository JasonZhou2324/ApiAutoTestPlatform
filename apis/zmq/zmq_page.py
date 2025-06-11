#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : zmq_page.py
@Time    : 2025/6/10 12:50
@Author  : zhouming
"""
from typing import Dict, Any, Optional, Union, List
from core.zmq_client import ZMQClient


class ZMQPage:
    """ZMQ页面类，封装具体的业务接口调用"""

    def __init__(self, client: ZMQClient):
        """
        初始化ZMQ页面对象

        Args:
            client: ZMQ客户端实例
        """
        self.client = client
        self.session_id = None
        self.connected = False

    def setup(self):
        """设置页面对象"""
        self.connect()
        self.handshake()

    def teardown(self):
        """清理页面对象"""
        if self.connected:
            self.disconnect()

    def connect(self) -> None:
        """建立连接"""
        self.client.connect()
        self.connected = True

    def disconnect(self) -> None:
        """断开连接"""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            self.session_id = None

    def handshake(self, protocol: str = 'TCP', timeout: int = 30) -> Dict[str, Any]:
        """
        握手协议

        Args:
            protocol: 协议类型
            timeout: 超时时间

        Returns:
            Dict: 握手响应
        """
        handshake_data = {
            'type': 'handshake',
            'protocol': protocol,
            'version': '1.0'
        }
        response = self.client.send_receive(handshake_data)
        
        if isinstance(response, dict) and response.get('status') == 'success':
            self.session_id = response.get('session_id')
        
        return response

    def send_message(
        self,
        message: Union[str, Dict[str, Any]],
        message_format: str = 'JSON',
        multipart: bool = False,
        wait_response: bool = True
    ) -> Optional[Union[Dict[str, Any], str, bytes, List[bytes]]]:
        """
        发送消息

        Args:
            message: 要发送的消息
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            multipart: 是否使用多部分消息
            wait_response: 是否等待响应

        Returns:
            Optional[Union[Dict, str, bytes, List[bytes]]]: 如果wait_response为True，返回响应数据；否则返回None
        """
        if not self.connected:
            raise ConnectionError("未连接到服务器")

        if wait_response:
            return self.client.send_receive(message, message_format, multipart)
        else:
            self.client.send(message, message_format, multipart)
            return None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            Dict: 登录响应
        """
        login_data = {
            'type': 'login',
            'username': username,
            'password': password
        }
        response = self.client.send_receive(login_data)
        
        if isinstance(response, dict) and response.get('status') == 'success':
            self.session_id = response.get('session_id')
        
        return response

    def logout(self) -> Dict[str, Any]:
        """
        登出

        Returns:
            Dict: 登出响应
        """
        logout_data = {
            'type': 'logout',
            'session_id': self.session_id
        }
        response = self.client.send_receive(logout_data)
        
        self.session_id = None
        return response

    def heartbeat(self) -> Dict[str, Any]:
        """
        心跳包

        Returns:
            Dict: 心跳响应
        """
        heartbeat_data = {
            'type': 'heartbeat',
            'session_id': self.session_id
        }
        return self.client.send_receive(heartbeat_data)

    def subscribe(self, topic: str) -> None:
        """
        订阅主题

        Args:
            topic: 主题名称
        """
        if self.client.socket_type == 'SUB':
            self.client.subscribe(topic)
        else:
            subscribe_data = {
                'type': 'subscribe',
                'topic': topic,
                'session_id': self.session_id
            }
            self.client.send_receive(subscribe_data)

    def unsubscribe(self, topic: str) -> None:
        """
        取消订阅

        Args:
            topic: 主题名称
        """
        if self.client.socket_type == 'SUB':
            self.client.unsubscribe(topic)
        else:
            unsubscribe_data = {
                'type': 'unsubscribe',
                'topic': topic,
                'session_id': self.session_id
            }
            self.client.send_receive(unsubscribe_data)

    def publish(self, topic: str, message: Union[str, Dict[str, Any]]) -> None:
        """
        发布消息

        Args:
            topic: 主题名称
            message: 消息内容
        """
        if self.client.socket_type == 'PUB':
            # PUB类型的socket直接发送多部分消息
            self.client.send([topic.encode(self.client.encoding), self.client._pack_data(message)], multipart=True)
        else:
            publish_data = {
                'type': 'publish',
                'topic': topic,
                'message': message,
                'session_id': self.session_id
            }
            self.client.send_receive(publish_data)

    def request_data(self, data_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        请求数据

        Args:
            data_type: 数据类型
            params: 请求参数

        Returns:
            Dict: 响应数据
        """
        request_data = {
            'type': 'request',
            'data_type': data_type,
            'params': params or {},
            'session_id': self.session_id
        }
        return self.client.send_receive(request_data)

    def push_data(self, data: Union[str, Dict[str, Any]], queue: str = 'default') -> None:
        """
        推送数据（用于PUSH类型的socket）

        Args:
            data: 要推送的数据
            queue: 队列名称
        """
        if self.client.socket_type == 'PUSH':
            # PUSH类型的socket直接发送数据
            self.client.send(data)
        else:
            push_data = {
                'type': 'push',
                'queue': queue,
                'data': data,
                'session_id': self.session_id
            }
            self.client.send_receive(push_data)

    def pull_data(self, queue: str = 'default') -> Union[Dict[str, Any], str, bytes]:
        """
        拉取数据（用于PULL类型的socket）

        Args:
            queue: 队列名称

        Returns:
            Union[Dict, str, bytes]: 拉取的数据
        """
        if self.client.socket_type == 'PULL':
            # PULL类型的socket直接接收数据
            return self.client.receive()
        else:
            pull_data = {
                'type': 'pull',
                'queue': queue,
                'session_id': self.session_id
            }
            return self.client.send_receive(pull_data)

    def upload_file(self, file_path: str, file_type: str = 'binary') -> Dict[str, Any]:
        """
        上传文件

        Args:
            file_path: 文件路径
            file_type: 文件类型

        Returns:
            Dict: 上传响应
        """
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, 'rb') as f:
            file_data = f.read()

        upload_data = {
            'type': 'upload',
            'file_name': os.path.basename(file_path),
            'file_type': file_type,
            'file_data': file_data,
            'session_id': self.session_id
        }
        return self.client.send_receive(upload_data, message_format='BINARY')

    def download_file(self, file_id: str, save_path: str) -> str:
        """
        下载文件

        Args:
            file_id: 文件ID
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        download_data = {
            'type': 'download',
            'file_id': file_id,
            'session_id': self.session_id
        }
        response = self.client.send_receive(download_data)
        
        if isinstance(response, dict) and response.get('status') == 'success':
            file_data = response.get('file_data')
            if file_data:
                with open(save_path, 'wb') as f:
                    f.write(file_data)
                return save_path
        
        raise ValueError("下载文件失败")

    def __enter__(self):
        """上下文管理器入口"""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.teardown() 