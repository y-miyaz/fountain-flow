import logging
from abc import ABCMeta, abstractmethod


@abstractmethod
class DBConnector(metaclass=ABCMeta):
    _instance = None
    _initialized = False

    def __new__(cls, config=None, env=None):
        if cls._instance is None:
            cls._instance = super(DBConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self, config=None, env=None):
        if not self._initialized and config and env:
            if env not in config.keys():
                logging.error(
                    f"No database environments available in database.yaml for env: '{env}'")
                raise
            self.config = config[env]
            self.connection = None
            self.connect()
            self._initialized = True

    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def get_foreign_key_values(self, table_name, key_name):
        raise NotImplementedError

    @abstractmethod
    def truncate_table(self, table_name):
        raise NotImplementedError

    @abstractmethod
    def insert_data(self, table_name, columns, data):
        raise NotImplementedError

    @abstractmethod
    def copy_data_from_csv(self, table_name, file_path, include_headers):
        raise NotImplementedError

    def __del__(self):
        self.close()
