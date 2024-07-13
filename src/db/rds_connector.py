import logging
import boto3
from botocore.config import Config

from db.db_connector import DBConnector

class RDSConnector(DBConnector):
    def __init__(self, config=None, env=None):
        try:
            if not self._initialized:
                super().__init__(config, env)
                session = boto3.Session(profile_name=self.config.get('profile', 'default'))
                self.region = self.config['region']
                self.credentials = session.get_credentials().get_frozen_credentials()
                # タイムアウト設定
                config = Config(connect_timeout=900, read_timeout=120)
                self.rds_client = session.client('rds-data', config=config, region_name=self.region)
                self.s3_client = session.client('s3', region_name=self.region)
        except Exception:
            logging.exception(f"Failed to initialize RDSConnector.")
            raise

    def execute_statement(self, sql, parameters=None):
        try:
            params = {
                'resourceArn': self.config['host'],
                'secretArn': self.config['secret_arn'],
                'database': self.config['dbname'],
                'sql': sql,
                'includeResultMetadata': True,
                'continueAfterTimeout': True
            }
            if parameters:
                params['parameters'] = parameters

            response = self.rds_client.execute_statement(**params)
            return response
        except Exception:
            logging.exception("Failed to execute statement.")
            raise

    def connect(self):
        pass

    def commit(self):
        pass  # Boto3 RDS Data API handles commits automatically.

    def close(self):
        pass  # Boto3 RDS Data API does not require closing connections.

    def get_foreign_key_values(self, table_name, key_name):
        """指定したテーブルからキーのリストを取得"""
        try:
            sql = f'SELECT DISTINCT {key_name} FROM {table_name}'
            response = self.execute_statement(sql)
            keys = response['records']
            return [key[0]['stringValue'] for key in keys]
        except Exception:
            logging.exception(
                f"Failed to get foreign keys values '{table_name}.{key_name}'.")
            raise

    def truncate_table(self, table_name):
        try:
            sql = f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE'
            self.execute_statement(sql)
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception:
            logging.exception(
                f"Failed to truncate table '{table_name}'.")
            raise

    def insert_data(self, table_name, columns, data):
        # TOBE
        """
        try:

            #sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':' + col for col in columns])})"
            #parameters = [{'name': col, 'value': {'stringValue': str(val)}} for col, val in zip(columns, data)]
            data = ["'" + str(item) + "'" for item in data]
            sql = (
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(tuple(data))})"
            )
            self.execute_statement(sql)
        except Exception:
            logging.exception(
                f"Failed to insert data into table '{table_name}'.")
            raise
        """
        logging.info(
            "fountain-flow does not implement insert data for RDS.")
        raise NotImplementedError

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            bucket_name = self.config['bucket_name']
            object_key = self.config['object_key']
            s3_uri = f"s3://{bucket_name}/{object_key}"
            # upload csv file to S3
            self.s3_client.upload_file(file_path, bucket_name, object_key)
            logging.info(
                f"Successfully uploaded {file_path} to {s3_uri}")
            # Prepare SQL command
            sql = f"""
            SELECT aws_s3.table_import_from_s3(
               '{table_name}', 
               '', 
               '(format csv)',
               '{bucket_name}',
               '{object_key}',
               '{self.region}'
            );
            """

            if include_headers:
                sql = sql.replace("(format csv)", "(format csv, header)")

            # Execute SQL command
            self.execute_statement(sql)
            logging.info(
                f"Successfully loaded {s3_uri} to {table_name}")
        except Exception:
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'.")
            raise

    def close(self):
        if self.connection:
            self.connection.close()