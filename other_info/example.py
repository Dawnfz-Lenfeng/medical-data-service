import logging
import sys

# 用于异步处理心跳检测
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import Flask, request

app = Flask(__name__)
executor = ThreadPoolExecutor(5)

# 服务的组名
GROUP_NAME = "DEFAULT_GROUP"
# 服务的名称
SERVICE_NAME = "python-model-service"
# 服务的IP地址
IP = "127.0.0.1"
# 服务的端口
global_port = 50056


class TestModelServicer:

    def test_function(self, data):
        if data == "time":
            current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            current = "你好呀"
        print(current + ":" + "GenVisModelStruct")
        return current + ":" + "GenVisModelStruct"


# 服务注册
def service_register(port):
    url = (
        "http://127.0.0.1:8848/nacos/v2/ns/instance?serviceName="
        + SERVICE_NAME
        + "&ip="
        + IP
        + "&port="
        + str(port)
    )
    res = requests.post(url)
    print(res.json())
    print("完成注册")


# 心跳检测
def service_beat():
    while True:
        url = (
            "http://127.0.0.1:8848/nacos/v1/ns/instance/beat?serviceName="
            + SERVICE_NAME
            + "&ip="
            + IP
            + "&port="
            + str(global_port)
        )
        res = requests.put(url)
        # print("心跳检测中... 响应状态码： {res.status_code}")
        time.sleep(5)


@app.route("/test", methods=["GET"])
def square():
    print("收到请求")
    data = request.args.get("type")
    print(data)
    my_class_instance = TestModelServicer()
    result = my_class_instance.test_function(data)
    return result


if __name__ == "__main__":
    service_register(global_port)

    # 创建线程对象
    send_beat_thread = threading.Thread(target=service_beat)
    # 启动线程
    send_beat_thread.start()

    app.run(host=IP, port=int(global_port), threaded=True)
