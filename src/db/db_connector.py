import logging
from abc import ABC, abstractmethod


class DBConnector(ABC):
    def __init__(self, config: dict = None, env: str = None):
        if not config or not env:
            logging.error("Config and environment must be provided.")
            raise

        if env not in config:
            logging.error(
                f"No database environments available in config for env: '{env}'"
            )
            raise

        self.config = config[env]
        self.connection = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_foreign_key_values(self, table_name, key_name):
        pass

    @abstractmethod
    def truncate_table(self, table_name):
        pass

    @abstractmethod
    def insert_data(self, table_name, columns, data):
        pass

    @abstractmethod
    def copy_data_from_csv(self, table_name, file_path, include_headers):
        pass
