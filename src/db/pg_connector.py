import logging

import psycopg2

from db.db_connector import DBConnector


class PGConnector(DBConnector):
    def __init__(self, config=None, env=None):
        super().__init__(config, env)

    def connect(self):
        try:
            if not self.connection or self.connection.closed != 0:
                self.connection = psycopg2.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    dbname=self.config["dbname"],
                    user=self.config["user"],
                    password=self.config["password"],
                )
        except Exception as e:
            logging.error("Failed to connect to database.")
            raise e

    def commit(self):
        if self.connection and self.connection.closed == 0:
            try:
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                logging.error("Failed to commit transaction.")
                raise e

    def close(self):
        if self.connection and self.connection.closed == 0:
            try:
                self.connection.close()
            except Exception as e:
                logging.error("Failed to close the connection.")
                raise e

    def get_foreign_key_values(self, table_name, key_name):
        """指定したテーブルからキーのリストを取得"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT DISTINCT {key_name} FROM {table_name}")
                keys = cursor.fetchall()
                return [key[0] for key in keys]
        except Exception as e:
            logging.error(
                f"Failed to get foreign keys values '{table_name}.{key_name}'."
            )
            raise e

    def truncate_table(self, table_name):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            self.connection.commit()
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception as e:
            if self.connection and self.connection.closed == 0:
                self.connection.rollback()
            logging.error(f"Failed to truncate table '{table_name}'.")
            raise e

    def insert_data(self, table_name, columns, data):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                placeholders = ", ".join(["%s"] * len(columns))
                columns_formatted = ", ".join(columns)
                query = f"INSERT INTO {table_name} ({columns_formatted}) VALUES ({
                    placeholders})"
                cursor.execute(query, tuple(data))
        except Exception as e:
            if self.connection and self.connection.closed == 0:
                self.connection.rollback()
            logging.error(f"Failed to insert data into table '{table_name}'.")
            raise e

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                with open(file_path, "r") as f:
                    copy_command = f"COPY {table_name} FROM STDIN WITH CSV"
                    if include_headers:
                        copy_command += " HEADER"
                    cursor.copy_expert(copy_command, f)
            self.connection.commit()
        except Exception as e:
            if self.connection and self.connection.closed == 0:
                self.connection.rollback()
            logging.error(f"Failed to copy data from CSV file to table '{table_name}'.")
            raise e
