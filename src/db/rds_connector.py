import logging

import boto3
from botocore.config import Config

from db.db_connector import DBConnector


class RDSConnector(DBConnector):
    def __init__(self, config=None, env=None):
        try:
            super().__init__(config, env)
            session = boto3.Session(profile_name=self.config.get("profile", "default"))
            self.region = self.config["region"]
            self.credentials = session.get_credentials().get_frozen_credentials()
            # タイムアウト設定
            boto_config = Config(connect_timeout=900, read_timeout=120)
            self.rds_client = session.client(
                "rds-data", config=boto_config, region_name=self.region
            )
            self.s3_client = session.client("s3", region_name=self.region)
        except Exception:
            logging.exception("Failed to initialize RDSConnector.")
            raise

    def execute_statement(self, sql, parameters=None):
        try:
            params = {
                "resourceArn": self.config["host"],
                "secretArn": self.config["secret_arn"],
                "database": self.config["dbname"],
                "sql": sql,
                "includeResultMetadata": True,
                "continueAfterTimeout": True,
            }
            if parameters:
                params["parameters"] = parameters

            response = self.rds_client.execute_statement(**params)
            return response
        except Exception:
            logging.exception("Failed to execute statement.")
            raise

    def connect(self):
        pass  # Boto3 RDS Data API does not require an explicit connection.

    def commit(self):
        pass  # Boto3 RDS Data API handles commits automatically.

    def close(self):
        pass  # Boto3 RDS Data API does not require closing connections.

    def get_foreign_key_values(self, table_name, key_name):
        """指定したテーブルからキーのリストを取得"""
        try:
            sql = f"SELECT DISTINCT {key_name} FROM {table_name}"
            response = self.execute_statement(sql)
            keys = response["records"]
            return [record[0]["stringValue"] for record in keys]
        except Exception:
            logging.exception(f"Failed to get foreign keys values '{
                              table_name}.{key_name}'.")
            raise

    def truncate_table(self, table_name):
        try:
            sql = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"
            self.execute_statement(sql)
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception:
            logging.exception(f"Failed to truncate table '{table_name}'.")
            raise

    def insert_data(self, table_name, columns, data):
        logging.error("Insert operation is not implemented for RDS.")
        raise NotImplementedError("Insert operation is not implemented for RDS.")

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            bucket_name = self.config["bucket_name"]
            object_key = self.config["object_key"]
            s3_uri = f"s3://{bucket_name}/{object_key}"

            # CSVファイルをS3にアップロード
            self.s3_client.upload_file(file_path, bucket_name, object_key)
            logging.info(f"Successfully uploaded {file_path} to {s3_uri}")

            # SQLコマンドの準備
            copy_options = "(format csv"
            if include_headers:
                copy_options += ", header"
            copy_options += ")"

            sql = f"""
            SELECT aws_s3.table_import_from_s3(
               '{table_name}',
               '',
               '{copy_options}',
               '{bucket_name}',
               '{object_key}',
               '{self.region}'
            );
            """

            # SQLコマンドの実行
            self.execute_statement(sql)
            logging.info(f"Successfully loaded {s3_uri} to {table_name}")
        except Exception:
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'."
            )
            raise
