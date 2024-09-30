from db.db_connector_factory import db_connector_factory


class ForeignKeyGenerator:
    def __init__(self, db_config, env, table_name, column, base_generator):
        try:
            db_connector = db_connector_factory(db_config, env=env)
            db_connector.connect()
            self.foreign_table = column["generation"]["foreign_table"]
            self.foreign_key = column["generation"]["foreign_key"]
            values = db_connector.get_foreign_key_values(
                self.foreign_table, self.foreign_key
            )
            column["generation"]["values"] = values
            self.base_generator = base_generator(
                table_name, column
            )  # 実際のデータ生成を行うジェネレータ
        except Exception as e:
            raise e

    def generate(self):
        try:
            return self.base_generator.generate()
        except Exception as e:
            raise e
