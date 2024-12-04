import os
import sqlite3
import threading

import pandas as pd


class MedicalService:
    def __init__(self):
        from config import DB_PATH

        self.db_path = DB_PATH
        self.local = threading.local()

    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def init_db(self):
        """初始化数据库表并导入数据"""
        cursor = self.get_connection().cursor()

        # 创建公示费用表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS publicize_cost (
                项目编码 VARCHAR,
                项目名称 VARCHAR,
                计价单位 VARCHAR,
                项目单价 DECIMAL
            )
            """
        )

        # 创建药品价格公示表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS publicize_drug_price (
                编号 VARCHAR,
                药品名称 VARCHAR,
                规格 VARCHAR,
                产地 VARCHAR,
                价格 DECIMAL
            )
            """
        )

        # 创建疾病信息表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS disease_info (
                疾病编码 VARCHAR,
                疾病名称 VARCHAR,
                疾病描述 TEXT,
                疾病分级 VARCHAR,
                常用诊疗 TEXT,
                常用诊疗编号 TEXT,
                常用药品 TEXT,
                常用药品编号 TEXT
            )
            """
        )

        # 导入数据
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

        # 导入公示费用数据
        cost_df = pd.read_csv(
            os.path.join(data_dir, "医院A", "PublicizeCostData.csv"), encoding="utf-8"
        )
        cost_df.to_sql(
            "publicize_cost", self.get_connection(), if_exists="replace", index=False
        )

        # 导入药品价格数据
        drug_df = pd.read_csv(
            os.path.join(data_dir, "医院A", "PublicizeDrugPriceData.csv"),
            encoding="utf-8",
        )
        drug_df.to_sql(
            "publicize_drug_price",
            self.get_connection(),
            if_exists="replace",
            index=False,
        )

        # 导入疾病信息数据
        disease_df = pd.read_csv(
            os.path.join(data_dir, "卫健委", "DiseaseInfo.csv"), encoding="utf-8"
        )
        disease_df.to_sql(
            "disease_info", self.get_connection(), if_exists="replace", index=False
        )

        self.get_connection().commit()

    def get_medical_costs(self):
        """获取医疗项目公示价格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                项目编码 as item_code,
                项目名称 as item_name,
                计价单位 as unit,
                项目单价（元） as price
            FROM publicize_cost
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_drug_prices(self):
        """获取药品公示价格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                编号 as drug_code,
                药品名称 as drug_name,
                规格 as specification,
                产地 as manufacturer,
                价格 as price
            FROM publicize_drug_price
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_disease_info(self):
        """获取疾病信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                疾病编码 as disease_code,
                疾病名称 as disease_name,
                疾病描述 as description,
                疾病分级 as level,
                常用诊疗 as treatment,
                常用药品 as recommended_drugs,
                常用诊疗编号 as treatment_codes,
                常用药品编号 as recommended_drugs_codes
            FROM disease_info
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    
#sql1
class MedicalCostService:
    def __init__(self):
        from config import DB_PATH

        self.db_path = DB_PATH
        self.local = threading.local()

    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def get_some_medical_costs(self, item_code):
        """查询某种诊疗方案对应的公示价格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                项目编码 as item_code,
                项目名称 as item_name,
                计价单位 as unit,
                项目单价（元） as price
            FROM publicize_cost
            WHERE 项目编码 IN ({})
        """.format(','.join('?' for _ in item_code))
        cursor.execute(query, tuple(item_code))
        return [dict(row) for row in cursor.fetchall()]

#sql2
class DrugPriceService:
    def __init__(self):
        from config import DB_PATH

        self.db_path = DB_PATH
        self.local = threading.local()

    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def get_some_drug_prices(self, drug_code):
        """查询某种药品公示价格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                编号 as drug_code,
                药品名称 as drug_name,
                规格 as specification,
                产地 as manufacturer,
                价格 as price
            FROM publicize_drug_price
            WHERE 编号 IN ({})

            """.format(','.join(['?'] * len(drug_code))),
            tuple(drug_code)
        )
        return [dict(row) for row in cursor.fetchall()]

#sql3
class DiseaseInfoService:
    def __init__(self):
        from config import DB_PATH

        self.db_path = DB_PATH
        self.local = threading.local()

    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def get_some_disease_info(self, disease_name):
        """查询某种疾病基础信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                疾病名称 as disease_name,
                疾病编码 as disease_code,
                疾病描述 as description,
                疾病分级 as level,
                常用诊疗 as treatment,
                常用药品 as recommended_drugs,
                常用诊疗编号 as treatment_code,
                常用药品编号 as recommended_drugs_code
            FROM disease_info
            WHERE 疾病名称 IN ({})

            """.format(','.join(['?'] * len(disease_name))),
            tuple(disease_name)
        )
        return [dict(row) for row in cursor.fetchall()]

#BPMN
class DiseaseMedicalDrugService:
    def __init__(self):
        self.medical_cost_service = MedicalCostService()
        self.drug_price_service = DrugPriceService()
        self.disease_info_service = DiseaseInfoService()

    def get_disease_medical_drug_info(self, disease_name):
        """组合查询：查询疾病信息、药品价格和医疗费用信息"""
        #输入
        disease_info = self.disease_info_service.get_some_disease_info([disease_name])
        if not disease_info:
            return {"error": "Disease not found"}
        disease = disease_info[0]
        #分割
        treatment_codes = disease['treatment_code'].split(';')
        drug_codes = disease['recommended_drugs_code'].split(';')
        medical_costs = self.medical_cost_service.get_some_medical_costs(treatment_codes)
        drug_prices = self.drug_price_service.get_some_drug_prices(drug_codes)
        #输出
        result = {
            "description": disease['description'],
            "disease_name": disease['disease_name'],
            "level": disease['level'],
            "recommended_drugs": disease['recommended_drugs'],
            "treatment": disease['treatment'],
            
        }

        for idx, drug in enumerate(drug_prices):
            result[f"drug_name{idx + 1}"] = drug['drug_name']
            result[f"drug_price{idx + 1}"] = drug['price']
            result[f"drug_specification{idx + 1}"] = drug['specification']
            result[f"drug_manufacturer{idx + 1}"] = drug['manufacturer']

        for idx, medical in enumerate(medical_costs):
            result[f"treatment_name{idx + 1}"] = medical['item_name']
            result[f"treatment_price{idx + 1}"] = medical['price']
            result[f"treatment_unit{idx + 1}"] = medical['unit']

        return [result]


    def __del__(self):
        if hasattr(self.local, "conn"):
            self.local.conn.close()

