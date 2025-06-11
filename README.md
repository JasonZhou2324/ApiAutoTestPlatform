# ApiAutoTestPlatform

ApiAutoTestPlatform是一个基于Python的自动化测试框架，支持多种协议（HTTP/HTTPS、ZMQ、Socket）的接口测试。该框架采用Page Object设计模式，实现了不同协议的解耦和统一管理。

## 项目特点

- 支持多种协议：HTTP/HTTPS、ZMQ、Socket
- 采用Page Object设计模式，提高代码复用性和可维护性
- 集成HttpRunner框架处理HTTP/HTTPS请求
- 配置化管理，支持多环境配置
- 完善的日志记录和测试报告
- 支持数据驱动测试
- 易于扩展和维护

## 项目结构

```
ApiAutoTestPlatform/
├── apis/                    # API接口定义
│   ├── http/               # HTTP/HTTPS接口
│   ├── zmq/                # ZMQ接口
│   └── socket/             # Socket接口
├── core/                    # 核心功能模块
│   ├── http_client.py      # HTTP客户端封装
│   ├── zmq_client.py       # ZMQ客户端封装
│   ├── socket_client.py    # Socket客户端封装
│   └── base_client.py      # 基础客户端类
├── models/                  # 数据模型
│   ├── http_model.py       # HTTP请求/响应模型
│   ├── zmq_model.py        # ZMQ消息模型
│   └── socket_model.py     # Socket消息模型
├── testcase/               # 测试用例
│   ├── http/              # HTTP测试用例
│   ├── zmq/               # ZMQ测试用例
│   └── socket/            # Socket测试用例
├── config/                 # 配置文件
│   ├── http_config.yaml   # HTTP配置
│   ├── zmq_config.yaml    # ZMQ配置
│   └── socket_config.yaml # Socket配置
└── utils/                  # 工具类
    ├── http_utils.py      # HTTP相关工具
    ├── zmq_utils.py       # ZMQ相关工具
    └── socket_utils.py    # Socket相关工具
```

## 环境要求

- Python 3.12+
- pip 20.0+
- 操作系统：Windows/Linux/MacOS

## 依赖安装

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 配置设置

在 `config` 目录下配置相应的环境参数：

```yaml
# config/http_config.yaml
default:
  base_url: http://api.example.com
  timeout: 30
  verify_ssl: true

# config/zmq_config.yaml
default:
  host: localhost
  port: 5555
  zmq_type: REQ

# config/socket_config.yaml
default:
  host: localhost
  port: 8888
```

### 2. 编写测试用例

#### HTTP测试用例示例

```python
# testcase/http/test_example.py
import pytest
from core.http_client import HTTPClient
from apis.http.example_page import HTTPExamplePage

class TestHTTPExample:
    @pytest.fixture
    def http_page(self):
        client = HTTPClient("http://api.example.com")
        page = HTTPExamplePage(client)
        page.setup()
        yield page
        page.teardown()
        
    def test_login(self, http_page):
        response = http_page.login("test_user", "test_pass")
        assert response["status_code"] == 200
```

#### ZMQ测试用例示例

```python
# testcase/zmq/test_example.py
import pytest
from core.zmq_client import ZMQClient
from apis.zmq.example_page import ZMQExamplePage

class TestZMQExample:
    @pytest.fixture
    def zmq_page(self):
        client = ZMQClient("localhost", 5555)
        page = ZMQExamplePage(client)
        page.setup()
        yield page
        page.teardown()
        
    def test_send_receive(self, zmq_page):
        response = zmq_page.send_message({"type": "test"})
        assert response["status"] == "success"
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定协议的测试
pytest testcase/http/
pytest testcase/zmq/
pytest testcase/socket/

# 生成测试报告
pytest --html=reports/report.html
```

## 框架扩展

### 添加新的协议支持

1. 在 `core` 目录下创建新的客户端类，继承 `BaseClient`
2. 在 `apis` 目录下创建对应的Page Object类
3. 在 `config` 目录下添加配置文件
4. 在 `testcase` 目录下编写测试用例

### 自定义Page Object

```python
from apis.base_page import BasePage

class CustomPage(BasePage):
    def __init__(self, client):
        super().__init__(client)
        
    def custom_method(self, *args, **kwargs):
        # 实现自定义方法
        pass
```

## 最佳实践

1. **配置管理**
   - 使用YAML文件管理配置
   - 区分不同环境的配置
   - 敏感信息使用环境变量

2. **测试用例组织**
   - 按协议类型组织测试用例
   - 使用有意义的测试用例命名
   - 合理使用fixture

3. **日志管理**
   - 使用框架提供的日志工具
   - 记录关键操作和错误信息
   - 定期清理日志文件

4. **代码规范**
   - 遵循PEP 8规范
   - 编写清晰的注释
   - 使用类型注解

## 常见问题

1. **Q: 如何处理不同环境的配置？**
   A: 在config目录下创建不同环境的配置文件，如dev.yaml, prod.yaml等

2. **Q: 如何添加新的协议支持？**
   A: 参考现有协议的实现，创建新的客户端类和Page Object类

3. **Q: 如何实现并发测试？**
   A: 使用pytest-xdist插件，通过命令行参数控制并发数

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 版本历史

- v1.0.0 (2025-06-10)
  - 初始版本发布
  - 支持HTTP/HTTPS、ZMQ、Socket协议
  - 实现基础框架功能

## 许可证

MIT License

## 联系方式

- 项目维护者：[Your Name]
- 邮箱：[Your Email]
- 项目地址：[GitHub Repository URL]


