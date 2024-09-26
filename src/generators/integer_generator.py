import logging
import random

from generators.generator import ValueGenerator


class IntegerGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        super().__init__(table_name, column)
        self.method = self.column["generation"]["method"]
        self.values = self.column["generation"].get("values")
        self.start = int(self.column["generation"].get("start", 0))
        self.end = (
            int(self.column["generation"].get("end"))
            if "end" in self.column["generation"]
            else None
        )
        self.interval = int(self.column["generation"].get("interval", 1))
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
                result = self.values[self.value_index % len(self.values)]
                self.value_index += 1
                return result
            else:
                if self.current_value is None:
                    self.current_value = self.start
                else:
                    self.current_value += self.interval
                    if self.end is not None and self.current_value > self.end:
                        self.current_value = self.start
                return self.current_value
        elif self.method == "random":
            if self.values:
                return random.choice(self.values)
            else:
                return random.randint(self.start, self.end)
        else:
            logging.error(
                f"Unknown generation method '{self.method}' in {self.table_name}.{self.column_name}"
            )
            raise ValueError(f"Unknown generation method '{self.method}'")

    def get_start_value(self):
        if self.start is not None:
            return self.start
        else:
            logging.error(f"{self.column_name} cannot get start value.")
            raise ValueError(
                f"Start value is not defined for column '{self.column_name}'"
            )
