#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_logs.py
@Time    : 2025/6/10 19:12
@Author  : zhouming
"""
from utility.log_utils.logger import get_logger, info, debug, warning, error, exception

# 获取一个自定义日志实例（可省略使用默认的 default_logger）
logger = get_logger(name="TestModule", level="DEBUG", log_path="logs/test_module.log")

# 使用全局导出的日志方法
info("这是一个信息日志")
debug("这是一个调试日志")
warning("这是一个警告日志")
error("这是一个错误日志")
