#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_logs.py
@Time    : 2025/6/10 19:12
@Author  : zhouming
"""
from utility.log_utils.logger import (
    get_logger,
    info,
    debug,
    warning,
    error,
    exception,
)


def test_logs():
    logger = get_logger(name="TestModule", level="DEBUG", log_path=None)
    info("info")
    debug("debug")
    warning("warning")
    error("error")
    exception("exception")
