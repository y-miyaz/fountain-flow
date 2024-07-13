import logging
import time
from datetime import datetime

from db.db_connector_factory import db_connector_factory
from generators.generator_factory import GeneratorFactory
from generators.io.csv_writer import CSVWriter
from generators.io.json_writer import JSONWriter
from tqdm import tqdm


class DataGenerator:
    def __init__(self, config, db_config, data_config, env):
        try:
            self.config = config
            # database or csv
            self.database_config = config['settings']['data_generation']['database']
            self.csv_config = config['settings']['data_generation']['csv']
            self.json_config = config['settings']['data_generation']['json']
            self.database_batch_size = self.database_config.get(
                'batch_size', 100)
            self.csv_batch_size = self.csv_config.get('batch_size', 100000)
            self.json_batch_size = self.json_config.get('batch_size', 100000)
            self.commit_interval = self.database_config.get(
                'commit_interval', 100)
            self.generation_method = config['settings']['data_generation']['method']
            self.db_config = db_config
            self.env = env
            self.db_type = self.db_config.get(self.env)['type']
            self.data_config = data_config
            self.generator_factory = GeneratorFactory(self.db_config, self.env)
        except Exception:
            raise

    def generate_data(self):
        try:
            if self.generation_method == 'database':
                response = input(
                    "\x1b[33mStart data generation and insersion (y/N): \x1b[0m")
                if response.lower() == 'y':
                    self.generate_data_database()
            elif self.generation_method == 'csv':
                self.generate_data_csv()
            elif self.generation_method == 'json':
                if self.db_type == 'dynamodb':
                    self.generate_data_json()
                else:
                    logging.error(
                        'json format is not supported except for dynamodb.')
        except Exception:
            raise

    def generate_data_database(self):
        try:
            db_connector = db_connector_factory(self.db_config, env=self.env)
            for table_config in self.data_config['tables']:
                row_count = table_config['row_count']
                try:
                    table_name = table_config['name']
                    generators = [self.generator_factory.get_generator(table_name,
                                                                       column) for column in table_config['columns']]
                    insert_size = 0
                    with tqdm(total=row_count, desc="Inserting data", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
                        for index in range(row_count):
                            record = []
                            for generator in generators:
                                data = generator.generate()
                                record.append(data)
                            db_connector.insert_data(
                                table_name, [col['name'] for col in table_config['columns']], record)
                            insert_size += 1
                            if (index + 1) % self.database_batch_size == 0 or index == table_config['row_count'] - 1:
                                try:
                                    db_connector.commit()
                                    time.sleep(self.commit_interval / 1000)
                                    pbar.update(insert_size)
                                    insert_size = 0
                                except Exception:
                                    logging.error(
                                        f"Transaction rolled back for table '{table_name}' after insert batch.")
                                    logging.error(f'... {record}')
                    logging.info(
                        f"Data insertion completed: '{table_config['row_count']}' records were inserted into the table '{table_name}'.")
                except Exception:
                    raise
        except Exception:
            raise

    def generate_data_csv(self):
        try:
            for table_config in self.data_config['tables']:
                row_count = table_config['row_count']
                table_name = table_config['name']
                is_error = False
                response = input((
                            f'\x1b[33mStart data generation and file output\n'
                            f"table name: '{table_name}\n"
                            f"row count: '{row_count}'\n"
                            f"(y/N): \x1b[0m"
                        )
                    )
                if response.lower() == 'y':

                    generators = [self.generator_factory.get_generator(table_name,
                                                                       column) for column in table_config['columns']]
                    records = []
                    csv_writer = CSVWriter(self.config, table_config)
                    for index in range(row_count):
                        record = []
                        for generator in generators:
                            data = generator.generate()
                            record.append(data)
                        records.append(record)
                        if (index + 1) % self.csv_batch_size == 0 or index == table_config['row_count'] - 1:
                            try:
                                csv_writer.save_to_csv(records)
                                records = []
                            except Exception:
                                logging.error((
                                        f"Failed to write data to csv file: \n"
                                        f"table name: '{table_name}'\n"
                                        f"row count: '{index + 1}'"
                                    )
                                )
                                is_error = True
                                break
                    logging.info(
                        f"Data generation completed: '{table_config['row_count']}' records were written to the file '{csv_writer.file_path}'.")
            if is_error is True:
                raise
        except Exception:
            raise

    def load_csv_data(self, table_name, file_path, include_headers: bool):
        try:
            db_connector = db_connector_factory(self.db_config, env=self.env)
            db_connector.copy_data_from_csv(
                table_name, file_path, include_headers)
            logging.info(
                f"Successfully load '{file_path}' into '{table_name}'.")
        except Exception:
            raise
        finally:
            db_connector.close()

    # dynamodb用
    def generate_data_json(self):
        from generators.dynamodb_types import DynamoDBTypes
        try:
            for table_config in self.data_config['tables']:
                row_count = table_config['row_count']
                table_name = table_config['name']
                is_error = False
                response = input(
                    f"\x1b[33mStart data generation and file writing process\ntable name: '{table_name}'\nrow count: '{row_count}'\n(y/N): \x1b[0m")
                if response.lower() == 'y':

                    generators = [{'generator': self.generator_factory.get_generator(
                        table_name, column)} for column in table_config['columns']]
                    for generator in generators:
                        generator['dynamodb_type'] = DynamoDBTypes.get_dynamodb_type(
                            generator['generator'])
                    records = []
                    json_writer = JSONWriter(self.config, table_config)
                    for index in range(row_count):
                        json_data = {}
                        for generator in generators:
                            data = generator['generator'].generate()
                            if isinstance(data, datetime):
                                data = data.isoformat()
                            key = generator['generator'].column_name
                            dynamodb_type = generator['dynamodb_type']
                            if dynamodb_type == 'N':
                                data = str(data)
                            json_data[key] = {dynamodb_type: data}
                        records.append({'Item': json_data})

                        if (index + 1) % self.csv_batch_size == 0 or index == table_config['row_count'] - 1:
                            try:
                                json_writer.save_to_json(records)
                                records = []
                            except Exception:
                                logging.error(
                                    f"Failed to write data to json file: \ntable name: '{table_name}'\nrow count: '{index + 1}'")
                                is_error = True
                                break
                    logging.info(
                        f"Data generation completed: '{table_config['row_count']}' records were written to the file '{json_writer.file_path}'.")
                    response = input(
                        "\x1b[33mDo you want to load the data into Database? (y/N): \x1b[0m")
                    if response.lower() == 'y':
                        self.load_json_data(table_name, json_writer.file_path)
            if is_error is True:
                raise
        except Exception:
            raise

    def load_json_data(self, table_name, file_path):
        try:
            db_connector = db_connector_factory(self.db_config, env=self.env)
            db_connector.copy_data_from_json(table_name, file_path)
            logging.info(
                f"Successfully load '{file_path}' into '{table_name}'.")
        except Exception:
            raise
        finally:
            db_connector.close()
