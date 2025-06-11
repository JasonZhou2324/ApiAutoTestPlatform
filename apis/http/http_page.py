#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : http_page.py
@Time    : 2025/6/10 12:48
@Author  : zhouming
"""
from typing import Dict, Any, Optional, Union
from core.http_client import HTTPClient


class HTTPPage:
    """HTTP页面类，封装具体的业务接口调用"""

    def __init__(self, client: HTTPClient):
        """
        初始化HTTP页面对象

        Args:
            client: HTTP客户端实例
        """
        self.client = client
        self.token = None
        self.headers = {}

    def setup(self):
        """设置页面对象"""
        # 可以在这里进行一些初始化设置
        pass

    def teardown(self):
        """清理页面对象"""
        self.client.close()

    def set_token(self, token: str):
        """
        设置认证token

        Args:
            token: 认证token
        """
        self.token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def set_headers(self, headers: Dict[str, str]):
        """
        设置请求头

        Args:
            headers: 请求头字典
        """
        self.headers.update(headers)

    def send_request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: 请求方法
            url: 请求URL
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            **kwargs: 其他请求参数

        Returns:
            Dict: 响应数据
        """
        # 合并请求头
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        return self.client.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json_data=json_data,
            headers=request_headers,
            **kwargs
        )

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        登录接口

        Args:
            username: 用户名
            password: 密码

        Returns:
            Dict: 登录响应数据
        """
        data = {
            'username': username,
            'password': password
        }
        response = self.send_request(
            method='POST',
            url='/api/login',
            json_data=data
        )

        # 如果登录成功，保存token
        if response.get('token'):
            self.set_token(response['token'])

        return response

    def logout(self) -> Dict[str, Any]:
        """
        登出接口

        Returns:
            Dict: 登出响应数据
        """
        response = self.send_request(
            method='POST',
            url='/api/logout'
        )

        # 清除token
        self.token = None
        self.headers.pop('Authorization', None)

        return response

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户信息
        """
        return self.send_request(
            method='GET',
            url=f'/api/users/{user_id}'
        )

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建用户

        Args:
            user_data: 用户数据

        Returns:
            Dict: 创建结果
        """
        return self.send_request(
            method='POST',
            url='/api/users',
            json_data=user_data
        )

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            user_data: 更新的用户数据

        Returns:
            Dict: 更新结果
        """
        return self.send_request(
            method='PUT',
            url=f'/api/users/{user_id}',
            json_data=user_data
        )

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            Dict: 删除结果
        """
        return self.send_request(
            method='DELETE',
            url=f'/api/users/{user_id}'
        )

    def search_users(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        搜索用户

        Args:
            query_params: 查询参数

        Returns:
            Dict: 搜索结果
        """
        return self.send_request(
            method='GET',
            url='/api/users/search',
            params=query_params
        )

    def upload_file(self, file_path: str, file_field: str = 'file', extra_data: Optional[Dict[str, Any]] = None) -> \
            Dict[str, Any]:
        """
        上传文件

        Args:
            file_path: 文件路径
            file_field: 文件字段名
            extra_data: 额外的表单数据

        Returns:
            Dict: 上传结果
        """
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        files = {
            file_field: open(file_path, 'rb')
        }

        try:
            return self.send_request(
                method='POST',
                url='/api/upload',
                data=extra_data,
                files=files
            )
        finally:
            files[file_field].close()

    def download_file(self, file_id: str, save_path: str) -> str:
        """
        下载文件

        Args:
            file_id: 文件ID
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        response = self.client.session.get(
            self.client._build_url(f'/api/download/{file_id}'),
            headers=self.headers,
            stream=True
        )
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path
