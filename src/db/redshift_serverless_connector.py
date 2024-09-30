import logging
import time

import boto3

from db.db_connector import DBConnector


class RedshiftServerlessConnector(DBConnector):
    check_interval = 1.0

    def __init__(self, config=None, env=None):
        super().__init__(config, env)
        session = boto3.Session(profile_name=self.config.get("profile", "default"))
        self.redshift_client = session.client(
            "redshift-data", region_name=self.config["region"]
        )
        self.s3_client = session.client("s3", region_name=self.config["region"])

    def connect(self):
        pass  # boto3 redshift-data クライアントは明示的な接続を必要としません

    def commit(self):
        pass  # boto3 redshift-data クライアントは自動的にコミットを処理します

    def close(self):
        pass  # boto3 redshift-data クライアントは明示的なクローズを必要としません

    def get_foreign_key_values(self, table_name, key_name):
        logging.error("fountain-flow は Redshift の外部キー制約を実装していません。")
        raise NotImplementedError("Redshift の外部キー制約は未実装です。")

    def truncate_table(self, table_name):
        try:
            sql = f"TRUNCATE TABLE {table_name};"
            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config["host"],
                Database=self.config["dbname"],
                Sql=sql,
            )
            self._check_status(response["Id"])
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception as e:
            logging.error(f"Failed to truncate table '{table_name}'.")
            raise e

    def insert_data(self, table_name, columns, data):
        try:
            placeholders = ", ".join(["%s"] * len(data))
            columns_formatted = ", ".join(columns)
            sql = f"INSERT INTO {table_name} ({columns_formatted}) VALUES ({
                placeholders});"

            parameters = []
            for item in data:
                if isinstance(item, int):
                    parameters.append({"name": "", "value": {"longValue": item}})
                elif isinstance(item, float):
                    parameters.append({"name": "", "value": {"doubleValue": item}})
                else:
                    parameters.append({"name": "", "value": {"stringValue": str(item)}})

            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config["host"],
                Database=self.config["dbname"],
                Sql=sql,
                Parameters=parameters,
            )
            self._check_status(response["Id"])
        except Exception as e:
            logging.error(f"Failed to insert data into table '{table_name}'.")
            raise e

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            # S3にファイルをアップロード
            bucket_name = self.config["bucket_name"]
            object_key = self.config["object_key"]
            iam_role = self.config["iam_role"]
            s3_uri = f"s3://{bucket_name}/{object_key}"
            self.s3_client.upload_file(file_path, bucket_name, object_key)
            logging.info(f"Successfully uploaded {file_path} to {s3_uri}")

            copy_options = "CSV"
            if include_headers:
                copy_options += " IGNOREHEADER AS 1"

            sql = f"COPY {table_name} FROM '{
                s3_uri}' IAM_ROLE '{iam_role}' {copy_options};"

            # S3からRedshiftにデータをコピー
            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config["host"],
                Database=self.config["dbname"],
                Sql=sql,
            )
            self._check_status(response["Id"])
            logging.info(f"Successfully loaded {s3_uri} to {table_name}")
        except Exception as e:
            logging.error(f"Failed to copy data from CSV file to table '{table_name}'.")
            raise e

    def _check_status(self, statement_id):
        while True:
            response = self.redshift_client.describe_statement(Id=statement_id)
            status = response["Status"]
            if status == "FINISHED":
                return response.get("Records", response)
            elif status == "FAILED":
                error_message = response.get("Error", "Unknown error")
                logging.error(f"Statement execution failed: {error_message}")
                raise
            elif status in ("SUBMITTED", "PICKED", "STARTED"):
                logging.info(f"Waiting for statement {
                             statement_id} to finish...")
                time.sleep(self.check_interval)
            else:
                logging.error(f"Unexpected statement status: {status}")
                raise
