import logging
import os
import shutil

import mysql.connector
from db.db_connector import DBConnector


class MySQLConnector(DBConnector):
    def __init__(self, config=None, env=None):
        if not self._initialized:
            super().__init__(config, env)

    def connect(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['dbname'],
                    user=self.config['user'],
                    password=self.config['password']
                )
        except Exception:
            logging.exception("Failed to connect to MySQL database.")
            raise

    def commit(self):
        try:
            self.connection.commit()
        except Exception:
            self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()

    def get_foreign_key_values(self, table_name, key_name):
        """指定したテーブルからキーのリストを取得"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(f'SELECT DISTINCT {key_name} FROM {table_name}')
            keys = cursor.fetchall()
            return [key[0] for key in keys]
        except Exception:
            logging.exception(
                f"Failed to get foreign keys values '{table_name}.{key_name}'.")
            raise
        finally:
            cursor.close()

    def truncate_table(self, table_name):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(f'TRUNCATE TABLE {table_name};')
            self.connection.commit()
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception:
            self.connection.rollback()
            logging.exception(
                f"Failed to truncate table '{table_name}'.")
            raise
        finally:
            cursor.close()

    def insert_data(self, table_name, columns, data):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                tuple(data)
            )
        except Exception:
            self.connection.rollback()
            logging.exception(
                f"Failed to insert data into table '{table_name}'.")
            raise
        finally:
            cursor.close()

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            self.connect()
            cursor = self.connection.cursor()
            # secure_file_privの値を確認
            cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv';")
            result = cursor.fetchone()
            secure_file_priv = result[1]

            if not secure_file_priv:
                raise ValueError(
                    "The MySQL server is not configured with secure_file_priv or the value is empty.")
            if secure_file_priv != 'NULL':
                dest_file_path = os.path.join(
                    secure_file_priv, os.path.basename(file_path))
                # secure_file_privディレクトリにファイルをコピー
                shutil.copy(file_path, dest_file_path)
                logging.info(
                    f"Successfully copied {file_path} to {dest_file_path}")
            else:
                dest_file_path = file_path
                logging.info(
                    "secure_file_priv is NULL.")

            # secure_file_privディレクトリからデータをロード
            header_option = "IGNORE 1 LINES" if include_headers else ""
            query = (
                f"LOAD DATA INFILE '{dest_file_path}' INTO TABLE {table_name} "
                f"FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' {header_option};"
            )
            cursor.execute(query)
            self.connection.commit()
            logging.info(
                f"Data from '{dest_file_path}' has been loaded into the table '{table_name}'.")
        except Exception:
            self.connection.rollback()
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'.")
            raise
        finally:
            cursor.close()
