#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : http_client.py
@Time    : 2025/6/10 12:48
@Author  : zhouming
"""
import json
import requests
from loguru import logger
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException


class HTTPClient:
    """HTTP客户端类，封装requests库的HTTP请求方法"""

    def __init__(self, base_url: str, timeout: int = 30, verify_ssl: bool = True):
        """
        初始化HTTP客户端

        Args:
            base_url: 基础URL
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl

    def _build_url(self, path: str) -> str:
        """
        构建完整的URL

        Args:
            path: 请求路径

        Returns:
            str: 完整的URL
        """
        path = path.lstrip('/')
        return f"{self.base_url}/{path}"

    @staticmethod
    def _handle_response(response: requests.Response) -> Dict[str, Any]:
        """
        处理响应

        Args:
            response: requests响应对象

        Returns:
            Dict: 响应数据
        """
        try:
            response.raise_for_status()
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            return {'text': response.text, 'status_code': response.status_code}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            return {'text': response.text, 'status_code': response.status_code}
        except Exception as e:
            logger.error(f"请求处理错误: {str(e)}")
            raise

    def request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: 请求方法（GET, POST, PUT, DELETE等）
            url: 请求URL
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他requests参数

        Returns:
            Dict: 响应数据
        """
        try:
            url = self._build_url(url)
            timeout = timeout or self.timeout
            headers = headers or {}

            # 设置默认的Content-Type
            if json_data and 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'

            logger.info(f"发送{method}请求到: {url}")
            logger.debug(f"请求参数: params={params}, data={data}, json={json_data}, headers={headers}")

            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs
            )

            result = self._handle_response(response)
            logger.info(f"请求成功: {url}")
            logger.debug(f"响应数据: {result}")
            return result

        except RequestException as e:
            logger.error(f"请求失败: {url}, 错误: {str(e)}")
            raise

    def get(
            self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """发送GET请求"""
        return self.request('GET', url, params=params, headers=headers, **kwargs)

    def post(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """发送POST请求"""
        return self.request('POST', url, data=data, json_data=json_data, headers=headers, **kwargs)

    def put(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """发送PUT请求"""
        return self.request('PUT', url, data=data, json_data=json_data, headers=headers, **kwargs)

    def delete(
            self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """发送DELETE请求"""
        return self.request('DELETE', url, params=params, headers=headers, **kwargs)

    def patch(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """发送PATCH请求"""
        return self.request('PATCH', url, data=data, json_data=json_data, headers=headers, **kwargs)

    def close(self):
        """关闭会话"""
        self.session.close()
