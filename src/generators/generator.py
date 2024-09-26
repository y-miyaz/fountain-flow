import logging
from abc import ABC, abstractmethod


class ValueGenerator(ABC):
    def __init__(self, table_name, column):
        self.table_name = table_name
        self.column = column
        self.column_name = column["name"]
        self.value_index = 0
        self.current_value = None

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def get_start_value(self):
        pass

    def validate(self):
        """基本バリデーションメソッド。具体的なバリデーションはサブクラスで実装。"""
        errors = []
        generation = self.column.get("generation", {})
        method = generation.get("method")

        if method is None:
            errors.append("'method' is missing")
        elif method not in ("sequence", "random"):
            errors.append(f"No method available for method type: '{method}'")

        return errors

    def handle_errors(self, errors):
        if errors:
            error_message = (
                f"Validation errors in '{self.table_name}.{self.column_name}':\n"
                + "\n".join(errors)
            )
            logging.error(error_message)
            raise ValueError(error_message)
