import logging
import random
import string

from generators.generator import ValueGenerator


class StringGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        super().__init__(table_name, column)
        self.method = self.column["generation"]["method"]
        self.values = self.column["generation"].get("values")
        self.length = int(self.column["generation"].get("length", 10))
        self.validate()

    def validate(self):
        errors = super().validate()
        # 'random' メソッドで 'values' が指定されていない場合でも、デフォルトで文字列を生成するためエラーは不要
        self.handle_errors(errors)

    def generate(self):
        if self.method == "sequence":
            if self.values:
                result = self.values[self.value_index % len(self.values)]
                self.value_index += 1
                return result
            else:
                result = "{:0>{width}}".format(self.value_index, width=self.length)
                self.value_index += 1
                return result
        elif self.method == "random":
            if self.values:
                return random.choice(self.values)
            else:
                return "".join(
                    random.choices(string.ascii_letters + string.digits, k=self.length)
                )
        else:
            logging.error(
                f"Unknown generation method '{self.method}' in {self.table_name}.{self.column_name}"
            )
            raise ValueError(f"Unknown generation method '{self.method}'")

    def get_start_value(self):
        return "0" * self.length
