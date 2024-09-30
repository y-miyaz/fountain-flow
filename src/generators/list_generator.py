from generators.dynamodb_types import DynamoDBTypes
from generators.generator import ValueGenerator
from generators.generator_factory import GeneratorFactory


class ListGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            gf = GeneratorFactory()
            self.size = column.get("size", 1)
            inner_column = {
                "name": "_",
                "type": column["inner_type"],
                "generation": column["generation"],
            }
            self.inner_generator = gf.get_generator(table_name, inner_column)
        except Exception as e:
            raise e

    def validate(self):
        try:
            errors = []
            if "inner_type" not in self.column.keys():
                errors.append("'inner_type' is missing")
            self.handle_errors(errors)
        except Exception as e:
            raise e

    def generate(self):
        try:
            list_value = []
            for _ in range(self.size):
                dynamodb_type = DynamoDBTypes.get_dynamodb_type(self.inner_generator)
                value = self.inner_generator.generate()
                if dynamodb_type == "N":
                    value = str(value)
                list_value.append({dynamodb_type: value})
            return list_value
        except Exception as e:
            raise e

    def get_start_value(self):
        pass
