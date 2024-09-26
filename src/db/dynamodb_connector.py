import copy
import logging
import time

import boto3
from botocore.exceptions import ClientError

from db.db_connector import DBConnector


class DynamoDBConnector(DBConnector):
    check_interval = 1.0

    def __init__(self, config=None, env=None):
        super().__init__(config, env)
        self.create_params = self.get_table_definition(self.config["source_table"])
        self.is_dropped = False

    def connect(self):
        try:
            session = boto3.Session(profile_name=self.config.get("profile", "default"))
            self.dynamodb_client = session.client(
                "dynamodb", region_name=self.config["region"]
            )
            self.s3_client = session.client("s3", region_name=self.config["region"])
        except Exception:
            logging.error("Failed to connect to DynamoDB.")
            raise

    def commit(self):
        # boto3 DynamoDB resource does not require explicit close
        pass

    def close(self):
        # boto3 DynamoDB resource does not require explicit close
        pass

    def get_foreign_key_values(self, table_name, key_name):
        logging.error(
            "fountain-flow does not implement foreign key constraints for DynamoDB."
        )
        raise NotImplementedError(
            "Foreign key constraints are not implemented for DynamoDB."
        )

    def get_table_definition(self, table_name):
        try:
            # テーブル情報を取得する
            table_info = self.dynamodb_client.describe_table(TableName=table_name)

            table = table_info["Table"]

            # テーブル作成用パラメータを生成
            create_params = {
                "AttributeDefinitions": table["AttributeDefinitions"],
                "TableName": table["TableName"],
                "KeySchema": table["KeySchema"],
                "BillingMode": table.get("BillingModeSummary", {}).get(
                    "BillingMode", "PROVISIONED"
                ),
                "SSESpecification": table.get("SSEDescription"),
            }

            if create_params["BillingMode"] == "PROVISIONED":
                create_params["ProvisionedThroughput"] = {
                    "ReadCapacityUnits": table["ProvisionedThroughput"][
                        "ReadCapacityUnits"
                    ],
                    "WriteCapacityUnits": table["ProvisionedThroughput"][
                        "WriteCapacityUnits"
                    ],
                }

            if "GlobalSecondaryIndexes" in table:
                create_params["GlobalSecondaryIndexes"] = [
                    {
                        "IndexName": gsi["IndexName"],
                        "KeySchema": gsi["KeySchema"],
                        "Projection": gsi["Projection"],
                        "ProvisionedThroughput": gsi.get("ProvisionedThroughput"),
                    }
                    for gsi in table["GlobalSecondaryIndexes"]
                ]

            if "LocalSecondaryIndexes" in table:
                create_params["LocalSecondaryIndexes"] = [
                    {
                        "IndexName": lsi["IndexName"],
                        "KeySchema": lsi["KeySchema"],
                        "Projection": lsi["Projection"],
                    }
                    for lsi in table["LocalSecondaryIndexes"]
                ]

            # None のパラメータを削除
            create_params = {k: v for k, v in create_params.items() if v is not None}
            return create_params

        except ClientError:
            logging.error(f"Failed to get table definition '{table_name}'.")
            raise

    def drop_table(self, table_name):
        try:
            if self.check_table_exists(table_name):
                self.dynamodb_client.delete_table(TableName=table_name)
                # テーブルの削除完了を待機
                waiter = self.dynamodb_client.get_waiter("table_not_exists")
                waiter.wait(TableName=table_name)
                logging.info(f"Table '{table_name}' has been dropped.")
                if self.config["source_table"] == table_name:
                    self.is_dropped = True
            else:
                logging.info(f"Table '{table_name}' does not exist.")
        except ClientError:
            logging.error(f"Failed to drop table '{table_name}'.")
            raise

    def truncate_table(self, table_name):
        logging.info("fountain-flow does not implement truncate table for DynamoDB.")

    def insert_data(self, table_name, columns, data):
        logging.error("Insert operation is not implemented for DynamoDB.")
        raise NotImplementedError("Insert operation is not implemented for DynamoDB.")

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        logging.error("Copy from CSV is not implemented for DynamoDB.")
        raise NotImplementedError("Copy from CSV is not implemented for DynamoDB.")

    def copy_data_from_json(self, table_name, file_path):
        try:
            table_params = copy.deepcopy(self.create_params)
            table_params["TableName"] = table_name
            bucket_name = self.config["bucket_name"]
            s3_key = self.config["object_key"]

            # S3にファイルをアップロード
            self.s3_client.upload_file(file_path, bucket_name, s3_key)
            logging.info(f"Successfully uploaded {
                         file_path} to s3://{bucket_name}/{s3_key}")
            logging.info(f"Create table with params: {table_params}")

            self.dynamodb_client.import_table(
                S3BucketSource={"S3Bucket": bucket_name, "S3KeyPrefix": s3_key},
                InputFormat="DYNAMODB_JSON",
                InputCompressionType="NONE",
                TableCreationParameters=table_params,
            )

            # テーブルの作成完了を待機
            waiter = self.dynamodb_client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            logging.info(f"Table '{table_name}' successfully created.")

        except Exception:
            logging.error(
                f"Failed to copy data from JSON file to table '{table_name}'."
            )
            if self.is_dropped:
                self._recreate_source_table()
            raise

    def _recreate_source_table(self):
        try:
            create_response = self.dynamodb_client.create_table(**self.create_params)
            table_arn = create_response["TableDescription"]["TableArn"]
            logging.info(f"Source table '{
                         self.create_params['TableName']}' recreated with ARN: {table_arn}")
        except Exception:
            logging.error(f"Failed to recreate source table '{
                              self.create_params['TableName']}'.")
            raise

    def _check_status(self, import_arn):
        while True:
            response = self.dynamodb_client.describe_import(ImportArn=import_arn)
            status = response["ImportTableDescription"]["ImportStatus"]
            if status == "COMPLETED":
                return response.get("Records", response)
            elif status in ("FAILED", "CANCELLED"):
                logging.error(f"Import failed: {response}")
                raise Exception(f"Import failed: {response}")
            elif status in ("IN_PROGRESS", "CANCELLING"):
                logging.info(f"Waiting for import {import_arn} to finish...")
                time.sleep(self.check_interval)
            else:
                logging.error(f"Unexpected import status: {status}")
                raise Exception(f"Unexpected import status: {status}")

    def check_table_exists(self, table_name):
        try:
            self.dynamodb_client.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            else:
                raise
