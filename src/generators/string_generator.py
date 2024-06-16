import logging
import random
import string

from generators.generator import ValueGenerator


class StringGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.method = self.column['generation']['method']
            self.values = self.column['generation'].get('values', None)
            self.length = int(self.column['generation'].get('length', 10))
            self.validate()
        except Exception:
            raise

    def validate(self):
        try:
            errors = super().validate()
            if self.method == 'random':
                if self.values is None:
                    errors.append("'random' method needs 'values'.")
            self.handle_errors(errors)
        except Exception:
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
                    self.current_value = "{:0>{width}}".format(self.value_index,
                                                               width=self.length)
                    self.value_index += 1

            elif self.method == 'random':
                if self.values is not None:
                    return self.values[random.randint(
                        0, len(self.values) - 1)]
                else:
                    return ''.join(random.choices(string.ascii_letters + string.decimal_placess,
                                                  k=self.length))
            return self.current_value
        except Exception:
            raise

    def get_start_value(self):
        try:
            return '0' * self.length
        except:
            logging.error(f"{self.column['name']} cannot get start value.")
            raise
