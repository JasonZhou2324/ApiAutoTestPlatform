#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : zmq_client.py
@Time    : 2025/6/10 12:50
@Author  : zhouming
"""
import json
import zmq
from typing import Dict, Any, Optional, Union, List, Tuple
from loguru import logger


class ZMQClient:
    """ZMQ客户端类，支持多种ZMQ模式"""

    # ZMQ Socket类型映射
    SOCKET_TYPES = {
        'REQ': zmq.REQ,      # 请求-响应模式
        'REP': zmq.REP,      # 响应-请求模式
        'PUB': zmq.PUB,      # 发布-订阅模式（发布者）
        'SUB': zmq.SUB,      # 发布-订阅模式（订阅者）
        'PUSH': zmq.PUSH,    # 推-拉模式（推送者）
        'PULL': zmq.PULL,    # 推-拉模式（拉取者）
        'DEALER': zmq.DEALER,# 异步请求-响应模式
        'ROUTER': zmq.ROUTER,# 异步请求-响应模式
        'PAIR': zmq.PAIR     # 点对点模式
    }

    def __init__(
        self,
        host: str,
        port: int,
        socket_type: str = 'REQ',
        context: Optional[zmq.Context] = None,
        timeout: int = 30,
        encoding: str = 'utf-8'
    ):
        """
        初始化ZMQ客户端

        Args:
            host: 服务器主机名或IP地址
            port: 服务器端口
            socket_type: Socket类型 ('REQ', 'REP', 'PUB', 'SUB', 'PUSH', 'PULL', 'DEALER', 'ROUTER', 'PAIR')
            context: ZMQ上下文，如果为None则创建新的上下文
            timeout: 超时时间（秒）
            encoding: 数据编码方式
        """
        self.host = host
        self.port = port
        self.socket_type = socket_type.upper()
        self.encoding = encoding
        self.connected = False

        # 创建或使用现有的上下文
        self.context = context or zmq.Context()
        
        # 创建socket
        if self.socket_type not in self.SOCKET_TYPES:
            raise ValueError(f"不支持的Socket类型: {socket_type}")
        
        self.socket = self.context.socket(self.SOCKET_TYPES[self.socket_type])
        
        # 设置超时
        self.socket.setsockopt(zmq.RCVTIMEO, timeout * 1000)  # 毫秒
        self.socket.setsockopt(zmq.SNDTIMEO, timeout * 1000)  # 毫秒

    def connect(self) -> None:
        """
        连接到服务器

        Raises:
            ConnectionError: 连接失败时抛出
        """
        if self.connected:
            return

        try:
            self.socket.connect(f"tcp://{self.host}:{self.port}")
            self.connected = True
            logger.info(f"已连接到服务器 {self.host}:{self.port}")
        except Exception as e:
            self.connected = False
            logger.error(f"连接服务器失败: {str(e)}")
            raise ConnectionError(f"无法连接到服务器 {self.host}:{self.port}") from e

    def disconnect(self) -> None:
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"关闭连接时发生错误: {str(e)}")
            finally:
                self.socket = None
                self.connected = False
                logger.info("已断开连接")

    def _pack_data(self, data: Union[str, bytes, Dict[str, Any]], message_format: str = 'JSON') -> bytes:
        """
        打包数据

        Args:
            data: 要发送的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')

        Returns:
            bytes: 打包后的数据
        """
        try:
            if message_format.upper() == 'JSON':
                if isinstance(data, dict):
                    data = json.dumps(data, ensure_ascii=False)
                elif isinstance(data, str):
                    # 尝试解析JSON字符串
                    json.loads(data)
                else:
                    raise ValueError("JSON格式数据必须是字典或JSON字符串")
                return data.encode(self.encoding)

            elif message_format.upper() == 'TEXT':
                if isinstance(data, str):
                    return data.encode(self.encoding)
                elif isinstance(data, bytes):
                    return data
                else:
                    return str(data).encode(self.encoding)

            elif message_format.upper() == 'BINARY':
                if isinstance(data, bytes):
                    return data
                else:
                    raise ValueError("BINARY格式数据必须是bytes类型")

            else:
                raise ValueError(f"不支持的消息格式: {message_format}")

        except Exception as e:
            logger.error(f"数据打包失败: {str(e)}")
            raise

    def _unpack_data(self, data: bytes, message_format: str = 'JSON') -> Union[Dict[str, Any], str, bytes]:
        """
        解包数据

        Args:
            data: 接收到的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')

        Returns:
            Union[Dict, str, bytes]: 解包后的数据
        """
        try:
            if message_format.upper() == 'JSON':
                try:
                    return json.loads(data.decode(self.encoding))
                except json.JSONDecodeError:
                    logger.warning("JSON解析失败，返回原始文本")
                    return data.decode(self.encoding)

            elif message_format.upper() == 'TEXT':
                return data.decode(self.encoding)

            elif message_format.upper() == 'BINARY':
                return data

            else:
                raise ValueError(f"不支持的消息格式: {message_format}")

        except Exception as e:
            logger.error(f"数据解包失败: {str(e)}")
            raise

    def send(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        message_format: str = 'JSON',
        multipart: bool = False
    ) -> None:
        """
        发送数据

        Args:
            data: 要发送的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            multipart: 是否发送多部分消息

        Raises:
            ConnectionError: 未连接时抛出
            zmq.error.ZMQError: ZMQ错误时抛出
        """
        if not self.connected:
            raise ConnectionError("未连接到服务器")

        try:
            # 打包数据
            packed_data = self._pack_data(data, message_format)

            # 发送数据
            if multipart and isinstance(data, (list, tuple)):
                self.socket.send_multipart(packed_data)
            else:
                self.socket.send(packed_data)

            logger.debug(f"已发送数据: {data}")

        except zmq.error.ZMQError as e:
            logger.error(f"发送数据失败: {str(e)}")
            raise

    def receive(
        self,
        message_format: str = 'JSON',
        multipart: bool = False
    ) -> Union[Dict[str, Any], str, bytes, List[bytes]]:
        """
        接收数据

        Args:
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            multipart: 是否接收多部分消息

        Returns:
            Union[Dict, str, bytes, List[bytes]]: 接收到的数据

        Raises:
            ConnectionError: 未连接时抛出
            zmq.error.ZMQError: ZMQ错误时抛出
        """
        if not self.connected:
            raise ConnectionError("未连接到服务器")

        try:
            # 接收数据
            if multipart:
                data = self.socket.recv_multipart()
                # 只解包第一部分数据
                if data and len(data) > 0:
                    data[0] = self._unpack_data(data[0], message_format)
                return data
            else:
                data = self.socket.recv()
                return self._unpack_data(data, message_format)

        except zmq.error.ZMQError as e:
            logger.error(f"接收数据失败: {str(e)}")
            raise

    def send_receive(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        message_format: str = 'JSON',
        multipart: bool = False
    ) -> Union[Dict[str, Any], str, bytes, List[bytes]]:
        """
        发送数据并等待响应

        Args:
            data: 要发送的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            multipart: 是否使用多部分消息

        Returns:
            Union[Dict, str, bytes, List[bytes]]: 响应数据

        Raises:
            ConnectionError: 未连接时抛出
            zmq.error.ZMQError: ZMQ错误时抛出
        """
        self.send(data, message_format, multipart)
        return self.receive(message_format, multipart)

    def subscribe(self, topic: str) -> None:
        """
        订阅主题（仅用于SUB类型的socket）

        Args:
            topic: 主题名称

        Raises:
            ValueError: 非SUB类型的socket调用时抛出
        """
        if self.socket_type != 'SUB':
            raise ValueError("只有SUB类型的socket才能订阅主题")

        try:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            logger.info(f"已订阅主题: {topic}")
        except zmq.error.ZMQError as e:
            logger.error(f"订阅主题失败: {str(e)}")
            raise

    def unsubscribe(self, topic: str) -> None:
        """
        取消订阅（仅用于SUB类型的socket）

        Args:
            topic: 主题名称

        Raises:
            ValueError: 非SUB类型的socket调用时抛出
        """
        if self.socket_type != 'SUB':
            raise ValueError("只有SUB类型的socket才能取消订阅")

        try:
            self.socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)
            logger.info(f"已取消订阅主题: {topic}")
        except zmq.error.ZMQError as e:
            logger.error(f"取消订阅失败: {str(e)}")
            raise

    def bind(self, port: Optional[int] = None) -> None:
        """
        绑定端口（用于REP, PUB, PULL, ROUTER类型的socket）

        Args:
            port: 端口号，如果为None则使用初始化时指定的端口

        Raises:
            ValueError: 不支持的socket类型调用时抛出
        """
        if self.socket_type not in ['REP', 'PUB', 'PULL', 'ROUTER']:
            raise ValueError(f"{self.socket_type}类型的socket不支持绑定操作")

        try:
            bind_port = port or self.port
            self.socket.bind(f"tcp://*:{bind_port}")
            logger.info(f"已绑定端口: {bind_port}")
        except zmq.error.ZMQError as e:
            logger.error(f"绑定端口失败: {str(e)}")
            raise

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
