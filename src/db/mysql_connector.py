import logging
import os
import shutil

import mysql.connector

from db.db_connector import DBConnector


class MySQLConnector(DBConnector):
    def __init__(self, config=None, env=None):
        super().__init__(config, env)

    def connect(self):
        if not self.connection or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    database=self.config["dbname"],
                    user=self.config["user"],
                    password=self.config["password"],
                )
            except Exception as e:
                logging.exception("Failed to connect to MySQL database.")
                raise e

    def commit(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                logging.exception("Failed to commit transaction.")
                raise e

    def close(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
            except Exception as e:
                logging.exception("Failed to close the connection.")
                raise e

    def get_foreign_key_values(self, table_name, key_name):
        """指定したテーブルからキーのリストを取得"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT DISTINCT {key_name} FROM {table_name}")
                keys = cursor.fetchall()
                return [key[0] for key in keys]
        except Exception as e:
            logging.exception(
                f"Failed to get foreign keys values '{table_name}.{key_name}'."
            )
            raise e

    def truncate_table(self, table_name):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {table_name};")
            self.connection.commit()
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception as e:
            self.connection.rollback()
            logging.exception(f"Failed to truncate table '{table_name}'.")
            raise e

    def insert_data(self, table_name, columns, data):
        try:
            self.connect()
            placeholders = ", ".join(["%s"] * len(columns))
            columns_formatted = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({columns_formatted}) VALUES ({placeholders})"
            with self.connection.cursor() as cursor:
                cursor.execute(query, tuple(data))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logging.exception(f"Failed to insert data into table '{table_name}'.")
            raise e

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                # secure_file_privの値を確認
                cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv';")
                result = cursor.fetchone()
                secure_file_priv = result[1]

                if not secure_file_priv:
                    raise ValueError(
                        "The MySQL server is not configured with secure_file_priv or the value is empty."
                    )

                if secure_file_priv != "NULL":
                    dest_file_path = os.path.join(
                        secure_file_priv, os.path.basename(file_path)
                    )
                    # secure_file_privディレクトリにファイルをコピー
                    shutil.copy(file_path, dest_file_path)
                    logging.info(f"Successfully copied {file_path} to {dest_file_path}")
                else:
                    dest_file_path = file_path
                    logging.info("secure_file_priv is NULL.")

                # secure_file_privディレクトリからデータをロード
                header_option = "IGNORE 1 LINES" if include_headers else ""
                query = (
                    f"LOAD DATA INFILE '{dest_file_path}' INTO TABLE {table_name} "
                    f"FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' {header_option};"
                )
                cursor.execute(query)
            self.connection.commit()
            logging.info(
                f"Data from '{dest_file_path}' has been loaded into the table '{table_name}'."
            )
        except Exception as e:
            self.connection.rollback()
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'."
            )
            raise e
