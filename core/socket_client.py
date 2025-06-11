#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : socket_client.py
@Time    : 2025/6/10 12:50
@Author  : zhouming
"""
import socket
import json
import struct
from typing import Dict, Any, Optional, Union, Tuple
from loguru import logger


class SocketClient:
    """Socket客户端类，支持TCP/UDP通信"""

    def __init__(
        self,
        host: str,
        port: int,
        protocol: str = 'TCP',
        timeout: int = 30,
        buffer_size: int = 8192,
        encoding: str = 'utf-8'
    ):
        """
        初始化Socket客户端

        Args:
            host: 服务器主机名或IP地址
            port: 服务器端口
            protocol: 协议类型 ('TCP' 或 'UDP')
            timeout: 超时时间（秒）
            buffer_size: 接收缓冲区大小
            encoding: 数据编码方式
        """
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.socket = None
        self.connected = False

    def connect(self) -> None:
        """
        建立连接

        Raises:
            ConnectionError: 连接失败时抛出
        """
        if self.connected:
            return

        try:
            # 创建socket对象
            if self.protocol == 'TCP':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:  # UDP
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 设置超时
            self.socket.settimeout(self.timeout)

            # 连接服务器
            if self.protocol == 'TCP':
                self.socket.connect((self.host, self.port))
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
        wait_response: bool = True,
        timeout: Optional[int] = None
    ) -> Optional[Union[Dict[str, Any], str, bytes]]:
        """
        发送数据

        Args:
            data: 要发送的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            wait_response: 是否等待响应
            timeout: 超时时间（秒），None表示使用默认超时时间

        Returns:
            Optional[Union[Dict, str, bytes]]: 如果wait_response为True，返回响应数据；否则返回None

        Raises:
            ConnectionError: 未连接时抛出
            TimeoutError: 超时时抛出
        """
        if not self.connected and self.protocol == 'TCP':
            raise ConnectionError("未连接到服务器")

        try:
            # 打包数据
            packed_data = self._pack_data(data, message_format)

            # 发送数据
            if self.protocol == 'TCP':
                self.socket.sendall(packed_data)
            else:  # UDP
                self.socket.sendto(packed_data, (self.host, self.port))

            logger.debug(f"已发送数据: {data}")

            # 等待响应
            if wait_response:
                return self.receive(message_format, timeout)
            return None

        except socket.timeout:
            logger.error("发送数据超时")
            raise TimeoutError("发送数据超时")
        except Exception as e:
            logger.error(f"发送数据失败: {str(e)}")
            raise

    def receive(
        self,
        message_format: str = 'JSON',
        timeout: Optional[int] = None
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        接收数据

        Args:
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            timeout: 超时时间（秒），None表示使用默认超时时间

        Returns:
            Union[Dict, str, bytes]: 接收到的数据

        Raises:
            ConnectionError: 未连接时抛出
            TimeoutError: 超时时抛出
        """
        if not self.connected and self.protocol == 'TCP':
            raise ConnectionError("未连接到服务器")

        try:
            # 设置超时
            if timeout is not None:
                self.socket.settimeout(timeout)

            # 接收数据
            if self.protocol == 'TCP':
                data = self.socket.recv(self.buffer_size)
            else:  # UDP
                data, _ = self.socket.recvfrom(self.buffer_size)

            if not data:
                raise ConnectionError("连接已关闭")

            # 解包数据
            result = self._unpack_data(data, message_format)
            logger.debug(f"已接收数据: {result}")
            return result

        except socket.timeout:
            logger.error("接收数据超时")
            raise TimeoutError("接收数据超时")
        except Exception as e:
            logger.error(f"接收数据失败: {str(e)}")
            raise

    def send_with_length(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        message_format: str = 'JSON',
        wait_response: bool = True,
        timeout: Optional[int] = None
    ) -> Optional[Union[Dict[str, Any], str, bytes]]:
        """
        发送带长度前缀的数据（用于TCP协议）

        Args:
            data: 要发送的数据
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            wait_response: 是否等待响应
            timeout: 超时时间（秒）

        Returns:
            Optional[Union[Dict, str, bytes]]: 如果wait_response为True，返回响应数据；否则返回None
        """
        if self.protocol != 'TCP':
            raise ValueError("带长度前缀的数据发送仅支持TCP协议")

        try:
            # 打包数据
            packed_data = self._pack_data(data, message_format)
            
            # 添加长度前缀（4字节网络字节序）
            length_prefix = struct.pack('!I', len(packed_data))
            full_data = length_prefix + packed_data

            # 发送数据
            self.socket.sendall(full_data)
            logger.debug(f"已发送数据(带长度前缀): {data}")

            # 等待响应
            if wait_response:
                return self.receive_with_length(message_format, timeout)
            return None

        except Exception as e:
            logger.error(f"发送数据失败: {str(e)}")
            raise

    def receive_with_length(
        self,
        message_format: str = 'JSON',
        timeout: Optional[int] = None
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        接收带长度前缀的数据（用于TCP协议）

        Args:
            message_format: 消息格式 ('JSON', 'TEXT', 'BINARY')
            timeout: 超时时间（秒）

        Returns:
            Union[Dict, str, bytes]: 接收到的数据
        """
        if self.protocol != 'TCP':
            raise ValueError("带长度前缀的数据接收仅支持TCP协议")

        try:
            # 设置超时
            if timeout is not None:
                self.socket.settimeout(timeout)

            # 接收长度前缀
            length_data = self.socket.recv(4)
            if len(length_data) != 4:
                raise ConnectionError("接收长度前缀失败")

            # 解析长度
            message_length = struct.unpack('!I', length_data)[0]

            # 接收完整消息
            received_data = b''
            remaining = message_length
            while remaining > 0:
                chunk = self.socket.recv(min(remaining, self.buffer_size))
                if not chunk:
                    raise ConnectionError("连接已关闭")
                received_data += chunk
                remaining -= len(chunk)

            # 解包数据
            result = self._unpack_data(received_data, message_format)
            logger.debug(f"已接收数据(带长度前缀): {result}")
            return result

        except socket.timeout:
            logger.error("接收数据超时")
            raise TimeoutError("接收数据超时")
        except Exception as e:
            logger.error(f"接收数据失败: {str(e)}")
            raise

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
