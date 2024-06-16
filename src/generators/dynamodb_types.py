class DynamoDBTypes:
    @classmethod
    def get_dynamodb_type(cls, value) -> str:
        from generators.boolean_generator import BooleanGenerator
        from generators.float_generator import FloatGenerator
        from generators.integer_generator import IntegerGenerator
        from generators.json_generator import JsonGenerator
        from generators.list_generator import ListGenerator
        from generators.string_generator import StringGenerator
        from generators.timestamp_generator import TimestampGenerator
        dynamodb_types = {
            IntegerGenerator: 'N',
            FloatGenerator: 'N',
            StringGenerator: 'S',
            BooleanGenerator: 'BOOL',
            TimestampGenerator: 'S',
            JsonGenerator: 'M',
            ListGenerator: 'L',
        }
        return dynamodb_types.get(type(value), 'S')
