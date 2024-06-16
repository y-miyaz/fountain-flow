import logging

import psycopg2
from db.db_connector import DBConnector


class PGConnector(DBConnector):
    def __init__(self, config=None, env=None):
        if not self._initialized:
            super().__init__(config, env)

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                dbname=self.config['dbname'],
                user=self.config['user'],
                password=self.config['password']
            )
        except Exception:
            logging.exception("Failed to connect to database.")
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
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;')
            self.connection.commit()
            logging.info(f"Table '{table_name}' has been truncated.")
        except Exception:
            logging.exception(
                f"Failed to truncate table '{table_name}'.")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def insert_data(self, table_name, columns, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                tuple(data)
            )
        except Exception:
            logging.exception(
                f"Failed to insert data into table '{table_name}'.")
            raise
        finally:
            cursor.close()

    def copy_data_from_csv(self, table_name, file_path, include_headers):
        cursor = self.connection.cursor()
        try:
            with open(file_path, 'r') as f:
                if include_headers:
                    cursor.copy_expert(
                        f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
                else:
                    cursor.copy_expert(
                        f"COPY {table_name} FROM STDIN WITH CSV", f)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logging.exception(
                f"Failed to copy data from CSV file to table '{table_name}'.")
            raise
        finally:
            cursor.close()
