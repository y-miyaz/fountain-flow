import logging
import random

from generators.generator import ValueGenerator


class FloatGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            self.method = self.column['generation']['method']
            self.values = self.column['generation'].get('values', None)
            self.decimal_places = self.column['generation'].get(
                'decimal_places', 3)
            self.start = float(self.column['generation'].get('start', 0))
            self.end = float(self.column['generation']['end']
                             ) if 'end' in column['generation'] else None
            self.interval = float(
                self.column['generation'].get('interval', 1.0))
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
                    result = round(self.startself.values[self.value_index % len(
                        self.values)], self.decimal_places)
                    self.value_index += 1
                    return result
                if self.current_value is None:
                    self.current_value = round(self.start, self.decimal_places)
                else:
                    if self.end is not None:
                        if self.current_value + self.interval > self.end:
                            self.current_value = round(
                                self.start, self.decimal_places)
                        else:
                            self.current_value = round(
                                self.interval + self.current_value, self.decimal_places)
                    else:
                        self.current_value = round(
                            self.interval + self.current_value, self.decimal_places)

            elif self.method == 'random':
                if self.values is not None:
                    return round(self.values[random.randint(
                        0, len(self.values) - 1)], self.decimal_places)
                else:
                    return round(random.uniform(
                        self.start, self.end), self.decimal_places)
            return self.current_value
        except Exception:
            raise

    def get_start_value(self):
        if self.start is not None:
            return self.start
        else:
            logging.error(f"{self.column['name']} cannot get start value.")
            raise
