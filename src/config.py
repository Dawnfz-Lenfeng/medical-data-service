import os

from nacos import NacosClient

# Nacos配置
SERVICE_NAME = "medical-data-service"
NACOS_SERVER = "127.0.0.1:8848"
IP = "127.0.0.1"
PORT = 5000

# 数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medical.db")


def get_nacos_client():
    try:
        client = NacosClient(
            server_addresses=NACOS_SERVER,
            namespace=SERVICE_NAME,
            username="nacos",  # 默认用户名
            password="nacos",  # 默认密码
        )
        # 测试连接
        client.get_server()
        return client
    except Exception as e:
        print(f"Failed to connect to Nacos: {e}")
        return None
