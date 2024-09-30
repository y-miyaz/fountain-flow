import logging
import time
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from db.db_connector_factory import db_connector_factory
from generators.generator_factory import GeneratorFactory
from generators.io.csv_writer import CSVWriter
from generators.io.json_writer import JSONWriter


class DataGenerator:
    def __init__(self, config, db_config, data_config, env):
        self.config = config
        # database or csv
        data_gen_settings = config["settings"]["data_generation"]
        self.generation_method = data_gen_settings["method"]
        self.database_config = data_gen_settings.get("database", {})
        self.csv_config = data_gen_settings.get("csv", {})
        self.json_config = data_gen_settings.get("json", {})
        self.database_batch_size = self.database_config.get("batch_size", 100)
        self.csv_batch_size = self.csv_config.get("batch_size", 100_000)
        self.json_batch_size = self.json_config.get("batch_size", 100_000)
        self.commit_interval = self.database_config.get("commit_interval", 100)
        self.db_config = db_config
        self.env = env
        self.db_type = self.db_config.get(self.env, {}).get("type")
        self.data_config = data_config
        self.generator_factory = GeneratorFactory(self.db_config, self.env)

    def generate_data(self, table_name):
        if self.generation_method == "database":
            response = input(
                "\x1b[33mStart data generation and insertion (y/N): \x1b[0m"
            )
            if response.lower() == "y":
                self.generate_data_to_table(table_name)
        elif self.generation_method == "csv":
            self.generate_data_to_csv(table_name)
        elif self.generation_method == "json":
            if self.db_type == "dynamodb":
                self.generate_data_to_json(table_name)
            else:
                logging.error("JSON format is not supported except for DynamoDB.")
        else:
            logging.error(f"Unknown generation method '{
                          self.generation_method}'.")

    def generate_data_to_table(self, table_name):
        db_connector = db_connector_factory(self.db_config, env=self.env)
        table_config = next(
            (t for t in self.data_config["tables"] if t["name"] == table_name), None
        )
        if not table_config:
            logging.error(f"Table '{table_name}' is not defined in data.yaml.")
            return

        row_count = table_config["row_count"]
        generators = [
            self.generator_factory.get_generator(table_name, column)
            for column in table_config["columns"]
        ]
        columns = [col["name"] for col in table_config["columns"]]
        insert_size = 0

        try:
            with tqdm(
                total=row_count,
                desc="Inserting data",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            ) as pbar:
                for index in range(row_count):
                    record = [generator.generate() for generator in generators]
                    db_connector.insert_data(table_name, columns, record)
                    insert_size += 1
                    if (
                        index + 1
                    ) % self.database_batch_size == 0 or index == row_count - 1:
                        db_connector.commit()
                        time.sleep(self.commit_interval / 1000)
                        pbar.update(insert_size)
                        insert_size = 0
            logging.info(
                f"Data insertion completed: '{
                    row_count}' records were inserted into the table '{table_name}'."
            )
        except Exception as e:
            logging.error(
                f"An error occurred during data generation for table '{table_name}'."
            )
            raise e
        finally:
            db_connector.close()

    def generate_data_to_csv(self, table_name):
        table_config = next(
            (t for t in self.data_config["tables"] if t["name"] == table_name), None
        )
        if not table_config:
            logging.error(f"Table '{table_name}' is not defined in data.yaml.")
            return

        row_count = table_config["row_count"]
        response = input(
            f"\x1b[33mStart data generation and file output\n"
            f"Table name: '{table_name}'\n"
            f"Row count: '{row_count}'\n(y/N): \x1b[0m"
        )
        if response.lower() != "y":
            return

        generators = [
            self.generator_factory.get_generator(table_name, column)
            for column in table_config["columns"]
        ]
        csv_writer = CSVWriter(self.config, table_config)
        records = []

        try:
            for index in range(row_count):
                record = [generator.generate() for generator in generators]
                records.append(record)
                if (index + 1) % self.csv_batch_size == 0 or index == row_count - 1:
                    csv_writer.save_to_csv(records)
                    records = []
            abs_path = Path(csv_writer.file_path).resolve(strict=True)
            logging.info(
                f"Data generation completed: '{
                    row_count}' records were written to the file '{abs_path}'."
            )
        except Exception as e:
            logging.error(f"Failed to write data to CSV file for table '{table_name}'.")
            raise e

    def load_csv_data(self, table_name, file_path, include_headers: bool):
        db_connector = db_connector_factory(self.db_config, env=self.env)
        try:
            db_connector.copy_data_from_csv(table_name, file_path, include_headers)
            abs_path = Path(file_path).resolve(strict=True)
            logging.info(f"Successfully loaded '{
                         abs_path}' into '{table_name}'.")
        except Exception as e:
            logging.error(f"Failed to load CSV data into table '{table_name}'.")
            raise e
        finally:
            db_connector.close()

    def generate_data_to_json(self, table_name):
        from generators.dynamodb_types import DynamoDBTypes

        table_config = next(
            (t for t in self.data_config["tables"] if t["name"] == table_name), None
        )
        if not table_config:
            logging.error(f"Table '{table_name}' is not defined in data.yaml.")
            return

        row_count = table_config["row_count"]
        response = input(
            f"\x1b[33mStart data generation and file writing process\n"
            f"Table name: '{table_name}'\n"
            f"Row count: '{row_count}'\n(y/N): \x1b[0m"
        )
        if response.lower() != "y":
            return

        generators = [
            {
                "generator": self.generator_factory.get_generator(table_name, column),
                "dynamodb_type": DynamoDBTypes.get_dynamodb_type(
                    self.generator_factory.get_generator(table_name, column)
                ),
            }
            for column in table_config["columns"]
        ]
        json_writer = JSONWriter(self.config, table_config)
        records = []

        try:
            for index in range(row_count):
                json_data = {}
                for gen in generators:
                    data = gen["generator"].generate()
                    if isinstance(data, datetime):
                        data = data.isoformat()
                    key = gen["generator"].column_name
                    dynamodb_type = gen["dynamodb_type"]
                    if dynamodb_type == "N":
                        data = str(data)
                    json_data[key] = {dynamodb_type: data}
                records.append({"Item": json_data})
                if (index + 1) % self.json_batch_size == 0 or index == row_count - 1:
                    json_writer.save_to_json(records)
                    records = []
            abs_path = Path(json_writer.file_path).resolve(strict=True)
            logging.info(
                f"Data generation completed: '{
                    row_count}' records were written to the file '{abs_path}'."
            )
        except Exception as e:
            logging.error(
                f"Failed to write data to JSON file for table '{table_name}'."
            )
            raise e

    def load_json_data(self, table_name, file_path):
        db_connector = db_connector_factory(self.db_config, env=self.env)
        try:
            db_connector.copy_data_from_json(table_name, file_path)
            abs_path = Path(file_path).resolve(strict=True)
            logging.info(f"Successfully loaded '{
                         abs_path}' into '{table_name}'.")
        except Exception as e:
            logging.error(f"Failed to load JSON data into table '{table_name}'.")
            raise e
        finally:
            db_connector.close()
