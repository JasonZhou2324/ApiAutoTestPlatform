#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : creat_testcase_temp.py
@Time    : 2025/6/10 13:49
@Author  : zhouming
"""
import pandas as pd
from openpyxl.utils import get_column_letter
from utility.path_utils.path_get import get_template_path


def create_testcase_template():
    """创建测试用例模板"""

    columns = {
        'HTTP测试用例': [
            '用例ID', '用例名称', '协议类型', '请求方法', 'URL', '请求头',
            '请求参数', '预期状态码', '预期响应', '前置条件', '后置条件',
            '是否执行', '优先级', '备注'
        ],
        'ZMQ测试用例': [
            '用例ID', '用例名称', '协议类型', '消息类型', '发送消息',
            '预期响应', '超时时间', '前置条件', '后置条件',
            '是否执行', '优先级', '备注'
        ],
        'Socket测试用例': [
            '用例ID', '用例名称', '协议类型', '消息格式', '发送消息',
            '预期响应', '超时时间', '前置条件', '后置条件',
            '是否执行', '优先级', '备注'
        ]
    }

    template_path = get_template_path()

    with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
        for sheet_name, cols in columns.items():
            df = pd.DataFrame(columns=cols)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]

            for idx, _ in enumerate(cols, start=1):
                worksheet.column_dimensions[get_column_letter(idx)].width = 15


if __name__ == '__main__':
    create_testcase_template()
    print("测试用例模板已生成!")
