import threading
import time
import webbrowser
import requests

import requests
from flask import Flask, jsonify, request

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

@app.route("/")
def home():
    return "Hello, Flask!"

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

#111
@app.route("/api/some_medicals", methods=["GET"])
def get_some_medicals():
    """查询多个诊疗方案信息"""
    item_codes = request.args.get('item_code', '').split(',')
    
    if not item_codes or item_codes == ['']:
        return jsonify({"error": "Missing required parameter: item_code"}), 400
    item_codes = [code.strip() for code in item_codes if code.strip()]
    if not item_codes:
        return jsonify({"error": "No valid item_code provided"}), 400

    return jsonify(service.get_some_medical_costs(item_codes))

@app.route("/api/some_drugs", methods=["GET"])
def get_some_drugs():
    """查询多个药品信息"""
    drug_codes = request.args.get('drug_code', '').split(',')
    
    if not drug_codes or drug_codes == ['']:
        return jsonify({"error": "Missing required parameter: drug_code"}), 400
    drug_codes = [code.strip() for code in drug_codes if code.strip()]
    if not drug_codes:
        return jsonify({"error": "No valid drug_code provided"}), 400

    return jsonify(service.get_some_drug_prices(drug_codes))


@app.route("/api/some_diseases", methods=["GET"])
def get_some_diseases():
    """查询多个疾病信息"""
    disease_names = request.args.get('disease_name', '').split(',')
    
    if not disease_names or disease_names == ['']:
        return jsonify({"error": "Missing required parameter: disease_name"}), 400
    disease_names = [code.strip() for code in disease_names if code.strip()]
    if not disease_names:
        return jsonify({"error": "No valid disease_name provided"}), 400

    return jsonify(service.get_some_disease_info(disease_names))

@app.route("/api/one_disease_medical_drug", methods=["GET"])
def get_disease_medical_drug_info_route():
    """查询疾病的基础信息、治疗方案、药品及费用"""
    disease_name = request.args.get('disease_name', '')
    if not disease_name:
        return jsonify({"error": "Missing required parameter: disease_name"}), 400

    result = service.get_disease_medical_drug_info(disease_name)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)

if __name__ == "__main__":
    # 注册服务
    service_register()

    # 启动心跳线程
    beat_thread = threading.Thread(target=service_beat)
    beat_thread.daemon = True
    beat_thread.start()

    #webbrowser.open("http://127.0.0.1:5000/api/one_disease_medical_drug?disease_name=肺炎")

    # 启动Flask服务
    app.run(host=IP, port=PORT)
