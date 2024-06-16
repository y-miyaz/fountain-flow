from generators.dynamodb_types import DynamoDBTypes
from generators.generator import ValueGenerator
from generators.generator_factory import GeneratorFactory


class JsonGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            gf = GeneratorFactory()
            self.items = [gf.get_generator(table_name, item)
                          for item in column['struct']]
        except Exception:
            raise

    def validate(self):
        try:
            errors = []
            if 'struct' not in self.column.keys():
                errors.append("'struct' is missing")
            self.handle_errors(errors)
        except Exception:
            raise

    def generate(self):
        try:
            json_value = {}
            for item in self.items:
                dynamodb_type = DynamoDBTypes.get_dynamodb_type(item)
                value = item.generate()
                if dynamodb_type == 'N':
                    value = str(value)
                json_value[item.column['name']] = {dynamodb_type: value}
            return json_value
        except Exception:
            raise

    def get_start_value(self):
        pass
