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
                常用药品 as recommended_drugs
            FROM disease_info
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def __del__(self):
        if hasattr(self.local, "conn"):
            self.local.conn.close()
