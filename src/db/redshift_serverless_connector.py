import logging
import time

import boto3
from db.db_connector import DBConnector


class RedshiftServerlessConnector(DBConnector):
    check_interval = 1.0

    def __init__(self, config=None, env=None):
        if not self._initialized:
            super().__init__(config, env)

    def connect(self):
        try:
            session = boto3.Session(
                profile_name=self.config.get('profile', 'default'))
            self.redshift_client = session.client(
                'redshift-data', region_name=self.config['region'])
            self.s3_client = session.client(
                's3', region_name=self.config['region'])
        except Exception:
            logging.exception("Failed to connect to Redshift database.")
            raise

    def commit(self):
        pass

    def close(self):
        # No explicit close method for boto3 redshift-data client
        pass

    def get_foreign_key_values(self, table_name, key_name):
        logging.error(
            "fountain-flow does not implement foreign key constraints for Redshift.")
        raise

    def truncate_table(self, table_name):
        try:
            sql = f'TRUNCATE TABLE {table_name};'
            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config['host'],
                Database=self.config['dbname'],
                Sql=sql
            )
            self._check_status(response['Id'])
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception:
            logging.exception(
                f"Failed to truncate table '{table_name}'.")
            raise

    def insert_data(self, table_name, columns, data):
        try:
            sql_data = []
            for item in data:
                if isinstance(item, int) or isinstance(item, float):
                    sql_data.append(str(item))
                else:
                    sql_data.append("'" + str(item) + "'")

            sql = f"INSERT INTO {table_name} VALUES ({', '.join(sql_data)})"

            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config['host'],
                Database=self.config['dbname'],
                Sql=sql,
            )
            self._check_status(response['Id'])
        except Exception:
            logging.exception(
                f"Failed to insert data into table '{table_name}'.")
            raise

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            # S3にファイルをアップロード
            bucket_name = self.config['bucket_name']
            object_key = self.config['object_key']
            iam_role = self.config['iam_role']
            s3_uri = f's3://{bucket_name}/{object_key}'
            self.s3_client.upload_file(file_path, bucket_name, object_key)

            logging.info(
                f"Successfully uploaded {file_path} to {s3_uri}")

            if include_headers:
                sql = f"COPY {table_name} FROM '{s3_uri}' IAM_ROLE '{iam_role}' CSV IGNOREHEADER as 1"
            else:
                sql = f"COPY {table_name} FROM '{s3_uri}' IAM_ROLE '{iam_role}' CSV"

            # S3からRedshiftにデータをコピー
            response = self.redshift_client.execute_statement(
                WorkgroupName=self.config['host'],
                Database=self.config['dbname'],
                Sql=sql
            )
            self._check_status(response['Id'])
            logging.info(
                f"Successfully loaded {s3_uri} to {table_name}")
        except Exception:
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'.")
            raise

    def _check_status(self, statement_id):
        while True:
            response = self.redshift_client.describe_statement(Id=statement_id)
            status = response['Status']
            if status == 'FINISHED':
                if response.get('Records'):
                    return response['Records']
                else:
                    return response
            elif status == 'FAILED':
                logging.error(
                    f"Statement execution failed: {response['Error']}")
                raise Exception(
                    f"Statement execution failed: {response['Error']}")
            elif status in ('SUBMITTED', 'PICKED', 'STARTED'):
                logging.info(
                    f"Waiting for statement {statement_id} to finish...")
                time.sleep(self.check_interval)
            else:
                logging.error(f"Unexpected statement status: {status}")
                raise Exception(f"Unexpected statement status: {status}")
