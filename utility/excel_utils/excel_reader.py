#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : excel_reader.py
@Time    : 2025/6/10 13:48
@Author  : zhouming
"""
import json
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Dict, List, Any, Optional
from utility.excel_utils.create_testcase_template import create_testcase_template


class ExcelTestcaseReader:
    """Excel测试用例读取器"""

    def __init__(self, excel_path: str):
        """
        初始化Excel读取器

        Args:
            excel_path: Excel文件路径
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"测试用例文件不存在: {excel_path}")

        # 读取所有sheet页
        self.excel_data = pd.read_excel(
            self.excel_path,
            sheet_name=None,  # 读取所有sheet
            engine='openpyxl'
        )

    def get_testcases(self, protocol_type: str) -> List[Dict[str, Any]]:
        """
        获取指定协议类型的测试用例

        Args:
            protocol_type: 协议类型 ('HTTP', 'ZMQ', 'Socket')

        Returns:
            List[Dict]: 测试用例列表
        """
        sheet_name = f"{protocol_type}测试用例"
        if sheet_name not in self.excel_data:
            raise ValueError(f"未找到{protocol_type}协议的测试用例sheet页")

        df = self.excel_data[sheet_name]
        # 过滤出需要执行的测试用例
        df = df[df['是否执行'].str.lower() == 'yes']

        testcases = []
        for _, row in df.iterrows():
            testcase = row.to_dict()
            # 处理JSON字符串
            for key, value in testcase.items():
                if isinstance(value, str) and value.strip().startswith(('{', '[')):
                    try:
                        testcase[key] = json.loads(value)
                    except json.JSONDecodeError:
                        logger.warning(f"JSON解析失败: {value}")

            testcases.append(testcase)

        return testcases

    def get_all_testcases(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有协议的测试用例

        Returns:
            Dict[str, List[Dict]]: 按协议类型分类的测试用例字典
        """
        result = {}
        for sheet_name in self.excel_data.keys():
            protocol_type = sheet_name.replace('测试用例', '')
            result[protocol_type] = self.get_testcases(protocol_type)
        return result

    def get_testcase_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        根据用例ID获取测试用例

        Args:
            case_id: 测试用例ID

        Returns:
            Optional[Dict]: 测试用例数据，如果未找到返回None
        """
        for sheet_name, df in self.excel_data.items():
            case = df[df['用例ID'] == case_id]
            if not case.empty:
                return case.iloc[0].to_dict()
        return None


if __name__ == '__main__':
    # 创建测试用例模板

    create_testcase_template()

    # 读取测试用例
    reader = ExcelTestcaseReader('testcase/templates/testcase_template.xlsx')

    # 获取所有HTTP测试用例
    http_cases = reader.get_testcases('HTTP')
    print(f"HTTP测试用例数量: {len(http_cases)}")

    # 获取所有协议的测试用例
    all_cases = reader.get_all_testcases()
    for protocol, cases in all_cases.items():
        print(f"{protocol}测试用例数量: {len(cases)}")
