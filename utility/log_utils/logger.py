#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : logger.py
@Time    : 2025/6/10 17:05
@Author  : zhouming
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, Any
from loguru import logger


class Logger:
    """日志工具类，支持彩色输出和灵活的日志配置"""

    # 日志级别对应的颜色
    LEVEL_COLORS = {
        "TRACE": "<cyan>",
        "DEBUG": "<blue>",
        "INFO": "<green>",
        "SUCCESS": "<green>",
        "WARNING": "<yellow>",
        "ERROR": "<red>",
        "CRITICAL": "<red><bold>",
    }

    def __init__(
        self,
        log_path: Optional[str] = None,
        level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "1 week",
        format_str: Optional[str] = None,
        colorize: bool = True,
    ):
        """
        初始化日志工具类

        Args:
            log_path: 日志文件路径，默认为 None（不输出到文件）
            level: 日志级别，默认为 INFO
            rotation: 日志轮转大小，默认为 10 MB
            retention: 日志保留时间，默认为 1 week
            format_str: 日志格式字符串，默认为 None（使用默认格式）
            colorize: 是否启用彩色输出，默认为 True
        """
        self.log_path = log_path
        self.level = level
        self.rotation = rotation
        self.retention = retention
        self.colorize = colorize

        # 设置默认日志格式
        if format_str is None:
            format_str = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )

        # 移除默认的处理器
        logger.remove()

        # 添加控制台输出处理器
        logger.add(
            sys.stderr,
            format=format_str,
            level=level,
            colorize=colorize,
            backtrace=True,
            diagnose=True,
        )

        # 如果指定了日志路径，添加文件输出处理器
        if log_path:
            self._setup_file_handler(log_path, format_str)

    def _setup_file_handler(self, log_path: str, format_str: str) -> None:
        """
        设置文件日志处理器

        Args:
            log_path: 日志文件路径
            format_str: 日志格式字符串
        """
        # 确保日志目录存在
        log_dir = os.path.dirname(log_path)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 添加文件处理器
        logger.add(
            log_path,
            format=format_str,
            level=self.level,
            rotation=self.rotation,
            retention=self.retention,
            encoding="utf-8",
            enqueue=True,  # 异步写入
            backtrace=True,
            diagnose=True,
        )

    @classmethod
    def get_logger(
        cls,
        name: Optional[str] = None,
        log_path: Optional[str] = None,
        **kwargs: Any,
    ) -> "Logger":
        """
        获取日志实例

        Args:
            name: 日志名称，默认为 None
            log_path: 日志文件路径，默认为 None
            **kwargs: 其他配置参数

        Returns:
            Logger: 日志实例
        """
        if name is None:
            name = "ApiAutoTestPlatform"

        # 如果未指定日志路径，使用默认路径
        if log_path is None:
            log_path = os.path.join("logs", f"{name.lower()}.log")

        return cls(log_path=log_path, **kwargs)

    def set_level(self, level: str) -> None:
        """
        设置日志级别

        Args:
            level: 日志级别
        """
        logger.remove()
        self.level = level
        self._setup_file_handler(self.log_path, self.format_str)

    @staticmethod
    def trace(message: str, **kwargs: Any) -> None:
        """输出 TRACE 级别日志"""
        logger.trace(message, **kwargs)

    @staticmethod
    def debug(message: str, **kwargs: Any) -> None:
        """输出 DEBUG 级别日志"""
        logger.debug(message, **kwargs)

    @staticmethod
    def info(message: str, **kwargs: Any) -> None:
        """输出 INFO 级别日志"""
        logger.info(message, **kwargs)

    @staticmethod
    def success(message: str, **kwargs: Any) -> None:
        """输出 SUCCESS 级别日志"""
        logger.success(message, **kwargs)

    @staticmethod
    def warning(message: str, **kwargs: Any) -> None:
        """输出 WARNING 级别日志"""
        logger.warning(message, **kwargs)

    @staticmethod
    def error(message: str, **kwargs: Any) -> None:
        """输出 ERROR 级别日志"""
        logger.error(message, **kwargs)

    @staticmethod
    def critical(message: str, **kwargs: Any) -> None:
        """输出 CRITICAL 级别日志"""
        logger.critical(message, **kwargs)

    @staticmethod
    def exception(message: str, **kwargs: Any) -> None:
        """输出异常日志"""
        logger.exception(message, **kwargs)


# 创建默认日志实例
default_logger = Logger.get_logger()

# 导出常用方法
trace = default_logger.trace
debug = default_logger.debug
info = default_logger.info
success = default_logger.success
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception
get_logger = Logger.get_logger 