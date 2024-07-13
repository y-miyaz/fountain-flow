import copy
import logging
import time

import boto3
from botocore.exceptions import ClientError
from db.db_connector import DBConnector


class DynamoDBConnector(DBConnector):
    check_interval = 1.0

    def __init__(self, config=None, env=None):
        try:
            if not self._initialized:
                super().__init__(config, env)
                self.create_params = self.get_table_definition(
                    self.config['source_table'])
                self.is_dropped = False
        except Exception:
            raise

    def connect(self):
        try:
            session = boto3.Session(
                profile_name=self.config.get('profile', 'default'))
            self.dynamodb_client = session.client(
                'dynamodb',
                region_name=self.config['region']
            )
            self.s3_client = session.client(
                's3', region_name=self.config['region'])
        except Exception:
            logging.exception("Failed to connect to DynamoDB.")
            raise

    def commit(self):
        # boto3 DynamoDB resource does not require explicit commit
        pass

    def close(self):
        # boto3 DynamoDB resource does not require explicit close
        pass

    def get_foreign_key_values(self, table_name, key_name):
        logging.error(
            "fountain-flow does not implement foreign key constraints for DynamoDB.")
        raise

    def get_table_definition(self, table_name):
        try:
            # テーブル情報を取得する
            table_info = self.dynamodb_client.describe_table(
                TableName=table_name)

            # 取得したテーブル情報を用いて、テーブル作成用パラメータを生成
            create_params = {
                'AttributeDefinitions': table_info['Table']['AttributeDefinitions'],
                'KeySchema': table_info['Table']['KeySchema'],
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': table_info['Table']['ProvisionedThroughput']['ReadCapacityUnits'],
                    'WriteCapacityUnits': table_info['Table']['ProvisionedThroughput']['WriteCapacityUnits']
                },
                'TableName': table_info['Table']['TableName'],
                'BillingMode': table_info['Table'].get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED'),
                'SSESpecification': table_info['Table'].get('SSEDescription', {}),
            }

            if 'GlobalSecondaryIndexes' in table_info['Table']:
                create_params['GlobalSecondaryIndexes'] = [
                    {
                        'IndexName': gsi['IndexName'],
                        'KeySchema': gsi['KeySchema'],
                        'Projection': gsi['Projection'],
                        'ProvisionedThroughput': gsi.get('ProvisionedThroughput', {}),
                        'OnDemandThroughput': gsi.get('OnDemandThroughput', {})
                    }
                    for gsi in table_info['Table']['GlobalSecondaryIndexes']
                ]

            if 'LocalSecondaryIndexes' in table_info['Table']:
                create_params['LocalSecondaryIndexes'] = [
                    {
                        'IndexName': lsi['IndexName'],
                        'KeySchema': lsi['KeySchema'],
                        'Projection': lsi['Projection']
                    }
                    for lsi in table_info['Table']['LocalSecondaryIndexes']
                ]

            if 'OnDemandThroughput' in table_info['Table']:
                create_params['OnDemandThroughput'] = table_info['Table']['OnDemandThroughput']

            # None のパラメータを削除
            create_params = {k: v for k,
                             v in create_params.items() if v is not None}
            return create_params
        except ClientError:
            logging.exception(
                f"Failed to get table definition '{table_name}'.")
            raise

    def drop_table(self, table_name):
        try:
            # テーブル情報を取得する
            is_exist = self.check_table_exists(table_name)
            if is_exist:
                table_params = self.get_table_definition(table_name)
                waiter = self.dynamodb_client.get_waiter(
                    'table_exists')
                waiter.wait(TableName=table_name)
                self.dynamodb_client.delete_table(TableName=table_name)
                # deleteが完了したのを確認する
                waiter = self.dynamodb_client.get_waiter(
                    'table_not_exists')
                waiter.wait(TableName=table_name)
                logging.info(f"Table '{table_name}' has been droped.")
                if self.config['source_table'] == table_name:
                    self.is_dropped = True
            else:
                logging.info(f"Table '{table_name}' does not exist.")

        except ClientError:
            logging.exception(
                f"Failed to drop table '{table_name}'.")
            create_response = self.dynamodb_client.create_table(
                **table_params)
            table_arn = create_response['TableDescription']['TableArn']
            logging.info(
                f"Table '{table_name}' recreated with ARN: '{table_arn}'")
            raise

    def truncate_table(self, table_name):
        logging.info(
            "fountain-flow does not implement truncate table for DynamoDB.")

    def insert_data(self, table_name, columns, data):
        try:
            table = self.dynamodb.Table(table_name)
            item = {col: val for col, val in zip(columns, data)}
            table.put_item(Item=item)
        except ClientError:
            logging.exception(
                f"Failed to insert data into table '{table_name}'.")
            raise

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        pass

    def copy_data_from_json(self, table_name, file_path):
        try:
            table_params = copy.deepcopy(self.create_params)
            table_params['TableName'] = table_name
            bucket_name = self.config['bucket_name']
            # S3にファイルをアップロード
            s3_key = self.config['object_key']
            self.s3_client.upload_file(file_path, bucket_name, s3_key)
            logging.info(
                f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_key}")
            logging.info(f'Create table with params: {table_params}')
            create_response = self.dynamodb_client.import_table(
                S3BucketSource={
                    'S3Bucket': bucket_name,
                    'S3KeyPrefix': s3_key
                },
                InputFormat='DYNAMODB_JSON',
                InputCompressionType='NONE',
                TableCreationParameters=table_params
            )
            # self._check_status(
            #    create_response['ImportTableDescription']['ImportArn'])
            waiter = self.dynamodb_client.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
            logging.info(
                f"Table '{table_name}' successfully created")

        except Exception:
            logging.exception(
                f"Failed to copy data from JSON file to table '{table_params['TableName']}'.")
            if self.is_dropped:
                create_response = self.dynamodb_client.create_table(
                    **self.create_params)
                table_arn = create_response['TableDescription']['TableArn']
                logging.info(
                    f"Source table {self.create_params['TableName']} recreated with ARN: {table_arn}")
            raise

    def _check_status(self, import_arn):
        while True:
            response = self.dynamodb_client.describe_import(
                ImportArn=import_arn
            )
            status = response['ImportTableDescription']['ImportStatus']
            if status == 'COMPLETED':
                if response.get('Records'):
                    return response['Records']
                else:
                    return response
            elif status in ('FAILED', 'CANCELLED'):
                logging.error(
                    f"import failed: {response}")
                raise Exception(
                    f"import failed: {response}")
            elif status in ('IN_PROGRESS', 'CANCELLING'):
                logging.info(
                    f"Waiting for import {import_arn} to finish...")
                time.sleep(self.check_interval)
            else:
                logging.error(f"Unexpected import status: {status}")
                raise Exception(f"Unexpected import status: {status}")

    def check_table_exists(self, table_name):
        try:
            # describe_tableを使用してテーブルの詳細を取得
            self.dynamodb_client.describe_table(
                TableName=table_name)
            # テーブルが存在する場合、Trueを返す
            return True
        except ClientError as e:
            # テーブルが存在しない場合のエラーメッセージをキャッチ
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                # その他のエラーの場合は例外を再スロー
                raise
