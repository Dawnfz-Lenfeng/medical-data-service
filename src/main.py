import threading
import time

import requests
from flask import Flask, jsonify

from config import IP, NACOS_SERVER, PORT, SERVICE_NAME
from service import MedicalService

app = Flask(__name__)
service = MedicalService()

# 初始化数据库
service.init_db()


def service_register():
    """注册服务到Nacos"""
    url = (
        f"http://{NACOS_SERVER}/nacos/v2/ns/instance?"
        f"serviceName={SERVICE_NAME}&ip={IP}&port={PORT}"
    )
    try:
        res = requests.post(url)
        if res.status_code == 200:
            print("Service registered successfully")
        else:
            print(f"Failed to register service: {res.text}")
    except Exception as e:
        print(f"Error registering service: {e}")


def service_beat():
    """发送心跳到Nacos"""
    while True:
        url = (
            f"http://{NACOS_SERVER}/nacos/v1/ns/instance/beat?"
            f"serviceName={SERVICE_NAME}&ip={IP}&port={PORT}"
        )
        try:
            res = requests.put(url)
            if res.status_code != 200:
                print(f"Failed to send heartbeat: {res.text}")
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
        time.sleep(5)


@app.route("/api/medical-costs", methods=["GET"])
def get_medical_costs():
    """获取医疗项目公示价格"""
    return jsonify(service.get_medical_costs())


@app.route("/api/drug-prices", methods=["GET"])
def get_drug_prices():
    """获取药品公示价格"""
    return jsonify(service.get_drug_prices())


@app.route("/api/diseases", methods=["GET"])
def get_diseases():
    """获取疾病信息"""
    return jsonify(service.get_disease_info())


if __name__ == "__main__":
    # 注册服务
    service_register()

    # 启动心跳线程
    beat_thread = threading.Thread(target=service_beat)
    beat_thread.daemon = True
    beat_thread.start()

    # 启动Flask服务
    app.run(host=IP, port=PORT)
