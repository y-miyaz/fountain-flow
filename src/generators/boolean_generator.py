import logging
import random

from generators.generator import ValueGenerator


class BooleanGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            self.method = self.column['generation']['method']
            self.values = self.column['generation'].get('values', None)
            self.current_value = None
        except Exception:
            logging(
                f"An error has occurred in {self.table}.{self.column['name']}")
            raise

    def generate(self):
        try:
            if self.method == 'sequence':
                if self.values is not None:
                    result = self.values[self.value_index % len(
                        self.values)]
                    self.value_index += 1
                    return result
                else:
                    if self.current_value is None:
                        self.current_value = True
                    else:
                        self.current_value = not self.current_value

            elif self.method == 'random':
                if self.values is not None:
                    self.values[random.randint(
                        0, len(self.values) - 1)]
                else:
                    self.current_value = random.choice([True, False])

            return self.current_value
        except Exception:
            raise

    def validate(self):
        try:
            errors = super().validate()

            self.handle_errors(errors)
        except Exception:
            raise

    def get_start_value(self):
        return True
