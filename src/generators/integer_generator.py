import logging
import random

from generators.generator import ValueGenerator


class IntegerGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            self.method = self.column['generation']['method']
            self.values = self.column['generation'].get('values', None)
            self.start = int(self.column['generation'].get('start', 0))
            self.end = int(self.column['generation']['end']
                           ) if 'end' in column['generation'] else None
            self.interval = int(self.column['generation'].get('interval', 1))
            self.current_value = None
        except Exception:
            raise

    def validate(self):
        try:
            errors = super().validate()
            if self.column['generation']['method'] == 'random':
                start = self.column['generation'].get('start', None)
                end = self.column['generation'].get('end', None)
                if start is None or end is None:
                    errors.append("'random' method needs 'start' and 'end'.")
            self.handle_errors(errors)
        except Exception:
            raise

    def generate(self):
        try:
            if self.method == 'sequence':
                if self.values is not None:
                    result = self.values[self.value_index % len(
                        self.values)]
                    if len(self.values) > self.value_index + 1:
                        self.value_index += 1
                    else:
                        self.value_index = 0
                    return result
                if self.current_value is None:
                    self.current_value = int(self.start)
                else:
                    if self.end is not None:
                        if self.current_value + self.interval > self.end:
                            self.current_value = self.start
                        else:
                            self.current_value += self.interval
                    else:
                        self.current_value += self.interval

            elif self.method == 'random':
                if self.values is not None:
                    return self.values[random.randint(
                        0, len(self.values) - 1)]
                else:
                    return random.randint(
                        self.start, self.end)

            return self.current_value
        except Exception:
            raise

    def get_start_value(self):
        if self.start is not None:
            return self.start
        else:
            logging.error(f"{self.column['name']} cannot get start value.")
            raise
