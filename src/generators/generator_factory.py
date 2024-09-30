import logging


class GeneratorFactory:
    _instance = None
    _initialized = False

    def __new__(cls, db_config=None, env=None):
        if cls._instance is None:
            cls._instance = super(GeneratorFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_config=None, env=None):
        if not self._initialized:
            self.db_config = db_config
            self.env = env
            self._initialized = True

    def get_generator(self, table_name, column):
        from generators.boolean_generator import BooleanGenerator
        from generators.float_generator import FloatGenerator
        from generators.foreign_key_generator import ForeignKeyGenerator
        from generators.integer_generator import IntegerGenerator
        from generators.json_generator import JsonGenerator
        from generators.list_generator import ListGenerator
        from generators.string_generator import StringGenerator
        from generators.timestamp_generator import TimestampGenerator

        generators = {
            "integer": IntegerGenerator,
            "float": FloatGenerator,
            "string": StringGenerator,
            "boolean": BooleanGenerator,
            "timestamp": TimestampGenerator,
            "json": JsonGenerator,
            "list": ListGenerator,
        }

        try:
            if "type" not in column:
                logging.error(
                    f"Validation errors in '{table_name}.{column['name']}': Column configuration error: 'type' is required"
                )
                raise ValueError(f"Column configuration error: 'type' is required")

            data_type = column["type"]
            if data_type not in generators.keys():
                logging.error(
                    f"Validation errors in '{table_name}.{column['name']}': No generator available for data type: '{data_type}'"
                )
                raise ValueError(f"No generator available for data type: '{data_type}'")

            generator_class = generators[data_type]
            if "generation" in column.keys():
                if (
                    column["generation"].get("foreign_table", None) is not None
                    and column["generation"].get("foreign_key", None) is not None
                ):
                    generator = ForeignKeyGenerator(
                        self.db_config, self.env, table_name, column, generator_class
                    )
                else:
                    generator = generator_class(table_name, column)
            else:
                generator = generator_class(table_name, column)
            return generator
        except Exception as e:
            raise e
