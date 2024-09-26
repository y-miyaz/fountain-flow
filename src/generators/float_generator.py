import logging
import random

from generators.generator import ValueGenerator


class FloatGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        super().__init__(table_name, column)
        self.method = self.column["generation"]["method"]
        self.values = self.column["generation"].get("values")
        self.decimal_places = self.column["generation"].get("decimal_places", 3)
        self.start = float(self.column["generation"].get("start", 0))
        self.end = (
            float(self.column["generation"].get("end"))
            if "end" in self.column["generation"]
            else None
        )
        self.interval = float(self.column["generation"].get("interval", 1.0))
        self.current_value = None
        self.value_index = 0
        self.validate()

    def validate(self):
        errors = super().validate()
        if self.method == "random":
            if self.start is None or self.end is None:
                errors.append("'random' method needs 'start' and 'end'.")
        self.handle_errors(errors)

    def generate(self):
        if self.method == "sequence":
            if self.values:
                result = round(
                    self.values[self.value_index % len(self.values)],
                    self.decimal_places,
                )
                self.value_index += 1
                return result
            else:
                if self.current_value is None:
                    self.current_value = self.start
                else:
                    self.current_value += self.interval
                    if self.end is not None and self.current_value > self.end:
                        self.current_value = self.start
                self.current_value = round(self.current_value, self.decimal_places)
                return self.current_value
        elif self.method == "random":
            if self.values:
                return round(random.choice(self.values), self.decimal_places)
            else:
                return round(random.uniform(self.start, self.end), self.decimal_places)
        else:
            logging.error(
                f"Unknown generation method '{self.method}' in {self.table}.{self.column['name']}"
            )
            raise ValueError(f"Unknown generation method '{self.method}'")

    def get_start_value(self):
        if self.start is not None:
            return self.start
        else:
            logging.error(f'{self.column['name']} cannot get start value.')
            raise ValueError(
                f"Start value is not defined for column '{self.column['name']}'"
            )
