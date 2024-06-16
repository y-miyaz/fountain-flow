import logging
from abc import ABC, abstractmethod


class ValueGenerator(ABC):
    def __init__(self, table_name, column):
        self.table_name = table_name
        self.column = column
        self.column_name = column['name']
        self.value_index = 0
        self.current_value = None

        logging.basicConfig(level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def get_start_value(self):
        pass

    def validate(self):
        """基本バリデーションメソッド、具体的なバリデーションはサブクラスで実装"""
        errors = []
        if 'method' not in self.column.get('generation', {}):
            errors.append("'method' is missing")
            return errors
        method = self.column['generation']['method']
        if method != 'sequence' and method != 'random':
            errors.append(f"No method available for method type: '{method}'")
            return errors

        return errors

    def handle_errors(self, errors):
        if errors:
            error_message = f"Validation errors in '{self.table_name}.{self.column['name']}':\n" + "\n".join(
                errors)
            logging.error(error_message)
            raise
