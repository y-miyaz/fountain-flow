import logging
import random

from generators.generator import ValueGenerator


class BooleanGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        super().__init__(table_name, column)
        self.method = self.column["generation"]["method"]
        self.values = self.column["generation"].get("values")
        self.current_value = None
        self.value_index = 0
        self.validate()

    def generate(self):
        if self.method == "sequence":
            if self.values:
                result = self.values[self.value_index % len(self.values)]
                self.value_index += 1
                return result
            else:
                self.current_value = (
                    not self.current_value if self.current_value is not None else True
                )
        elif self.method == "random":
            if self.values:
                self.current_value = random.choice(self.values)
            else:
                self.current_value = random.choice([True, False])
        else:
            logging.warning(f"Unknown generation method '{self.method}' in {
                          self.table}.{self.column['name']}")
            raise ValueError(f"Unknown generation method '{self.method}'")
        return self.current_value

    def validate(self):
        errors = super().validate()
        # 追加のバリデーションがあればここに記述
        self.handle_errors(errors)

    def get_start_value(self):
        return True
