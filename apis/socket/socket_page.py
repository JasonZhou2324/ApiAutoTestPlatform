#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : socket_page.py
@Time    : 2025/6/10 12:50
@Author  : zhouming
"""
from typing import Dict, Any, Optional, Union
from core.socket_client import SocketClient


class SocketPage:
    """Socket页面类，封装具体的业务接口调用"""

    def __init__(self, client: SocketClient):
        """
        初始化Socket页面对象

        Args:
            client: Socket客户端实例
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
        response = self.client.send(
            data=handshake_data,
            message_format='JSON',
            timeout=timeout
        )
        
        if isinstance(response, dict) and response.get('status') == 'success':
            self.session_id = response.get('session_id')
        
        return response

    def send_message(
        self,
        message: Union[str, Dict[str, Any]],
        message_format: str = 'JSON',
        use_length_prefix: bool = False,
        timeout: Optional[int] = None
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        发送消息

        Args:
            message: 要发送的消息
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            use_length_prefix: 是否使用长度前缀（仅TCP协议）
            timeout: 超时时间

        Returns:
            Union[Dict, str, bytes]: 响应数据
        """
        if not self.connected:
            raise ConnectionError("未连接到服务器")

        if use_length_prefix and self.client.protocol == 'TCP':
            return self.client.send_with_length(
                data=message,
                message_format=message_format,
                timeout=timeout
            )
        else:
            return self.client.send(
                data=message,
                message_format=message_format,
                timeout=timeout
            )

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
        response = self.send_message(login_data)
        
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
        response = self.send_message(logout_data)
        
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
        return self.send_message(heartbeat_data)

    def subscribe(self, topic: str) -> Dict[str, Any]:
        """
        订阅主题

        Args:
            topic: 主题名称

        Returns:
            Dict: 订阅响应
        """
        subscribe_data = {
            'type': 'subscribe',
            'topic': topic,
            'session_id': self.session_id
        }
        return self.send_message(subscribe_data)

    def unsubscribe(self, topic: str) -> Dict[str, Any]:
        """
        取消订阅

        Args:
            topic: 主题名称

        Returns:
            Dict: 取消订阅响应
        """
        unsubscribe_data = {
            'type': 'unsubscribe',
            'topic': topic,
            'session_id': self.session_id
        }
        return self.send_message(unsubscribe_data)

    def publish(self, topic: str, message: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        发布消息

        Args:
            topic: 主题名称
            message: 消息内容

        Returns:
            Dict: 发布响应
        """
        publish_data = {
            'type': 'publish',
            'topic': topic,
            'message': message,
            'session_id': self.session_id
        }
        return self.send_message(publish_data)

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
        return self.send_message(request_data)

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
        return self.send_message(upload_data, message_format='BINARY')

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
        response = self.send_message(download_data)
        
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