import logging
import os

import fire
import inquirer
import yaml

from db.db_connector_factory import db_connector_factory
from format.custom_fomatter import setup_logging
from util.validate import (
    validate_db_config,
    validate_settings,
    validate_data_definition,
)

from generators.data_generator import DataGenerator


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


class FountainFlowCLI:
    def __init__(self):
        self.cdir = os.path.dirname(__file__)
        self.config = load_config(os.path.join(self.cdir, "../config/settings.yaml"))
        self.db_config = load_config(os.path.join(self.cdir, "../config/database.yaml"))
        self.data_config_file = None
        self.data_config = None

        # ロギングのセットアップ
        log_level = self.config["settings"]["logging"].get("level", "INFO")
        setup_logging(log_level)

        db_config_errors = validate_db_config(self.db_config)
        if db_config_errors:
            for error in db_config_errors:
                logging.error(error)
        settings_errors = validate_settings(self.config)
        if settings_errors:
            for error in settings_errors:
                logging.error(error)

    def truncate_table(self, env, table_name):
        """指定したテーブルをトランケートします。"""
        try:
            db_connector = db_connector_factory(self.db_config, env=env)
            response = input(f"\x1b[33mDo you want to truncate table '{
                             table_name}'? (y/N): \x1b[0m")
            if response.lower() == "y":
                db_connector.truncate_table(table_name)
            else:
                logging.info("Truncate operation was canceled by the user.")
        except NotImplementedError:
            logging.warning(
                "Truncate operation is not implemented for this database type."
            )
        except Exception:
            logging.exception("Operation Failed: tuncate table.")

    def generate_and_insert(self, env, table_name):
        """データを生成してレコードを挿入します。"""
        try:
            self.config["settings"]["data_generation"]["method"] = "database"
            data_generator = DataGenerator(
                self.config, self.db_config, self.data_config, env
            )
            data_generator.generate_data(table_name)
        except NotImplementedError:
            logging.warning("Generate and insert operation is not implemented.")
        except Exception:
            logging.exception("Operation Failed: generate and insert.")

    def generate_and_output(self, env, table_name):
        """データを生成してファイルに出力します。"""
        try:
            db_type = self.db_config[env].get("type")
            if db_type != "dynamodb":
                self.config["settings"]["data_generation"]["method"] = "csv"
            else:
                self.config["settings"]["data_generation"]["method"] = "json"

            data_generator = DataGenerator(
                self.config, self.db_config, self.data_config, env
            )
            data_generator.generate_data(table_name)
        except NotImplementedError:
            logging.warning("Generate and output operation is not implemented.")
        except Exception:
            logging.exception("Operation Failed: generate and output.")

    def load_file(self, env, table_name, file_path):
        """ファイルをデータベースにロードします。"""
        try:
            db_type = self.db_config[env].get("type")
            if db_type != "dynamodb":
                self.config["settings"]["data_generation"]["method"] = "csv"
            else:
                self.config["settings"]["data_generation"]["method"] = "json"

            data_generator = DataGenerator(
                self.config, self.db_config, self.data_config, env
            )
            if db_type == "dynamodb":
                data_generator.load_json_data(table_name, file_path)
            else:
                response = input("Does the CSV file include headers? (y/N): ")
                include_headers = response.lower() == "y"
                data_generator.load_csv_data(table_name, file_path, include_headers)
        except NotImplementedError:
            logging.warning("Load file operation is not implemented.")
        except Exception:
            logging.error(f"Failed to load file '{
                              file_path}' into table '{table_name}'.")
            logging.exception("Operation Failed: generate and output.")

    def switch_env(self):
        """接続環境を切り替えます。"""
        try:
            envs = list(self.db_config.keys())
            questions = [
                inquirer.List(
                    "action",
                    message="Please select the connection environment (database.yaml)",
                    choices=envs,
                ),
            ]
            answers = inquirer.prompt(questions)
            selected_env = answers["action"]
            return selected_env
        except Exception:
            logging.exception("Operation Failed: switch env.")

    def switch_data_config(self):
        """データ設定を切り替えます。"""
        try:
            data_config_dir = os.path.join(self.cdir, "../def")
            files = [f for f in os.listdir(data_config_dir) if f.endswith(".yaml")]
            if not files:
                logging.error("No YAML files found in the /def directory.")
                exit(1)
            questions = [
                inquirer.List(
                    "action",
                    message="Please select the data config (/def)",
                    choices=files,
                ),
            ]
            answers = inquirer.prompt(questions)
            self.data_config_file = answers["action"]
            self.data_config = load_config(
                os.path.join(self.cdir, f"../def/{self.data_config_file}")
            )
            errors = validate_data_definition(self.data_config)
            if errors:
                for error in errors:
                    logging.error(error)
        except Exception:
            logging.exception("Operation Failed: switch data config.")


def main():
    cli = FountainFlowCLI()
    env = cli.switch_env()
    cli.switch_data_config()

    while True:
        try:
            questions = [
                inquirer.List(
                    "action",
                    message=f"Please select an option (env={env}, data_config={
                        cli.data_config_file})",
                    choices=[
                        ("Truncate Table", "truncate_table"),
                        ("Generate Data & Insert Records", "generate_and_insert"),
                        ("Generate Data & File Output", "generate_and_output"),
                        ("Load File", "load_file"),
                        ("Switch Env", "switch_env"),
                        ("Switch Data Config", "switch_data_config"),
                        ("Exit", "exit"),
                    ],
                ),
            ]
            answers = inquirer.prompt(questions)
            action = answers["action"]

            if action == "truncate_table":
                table_names = [table["name"] for table in cli.data_config["tables"]] + [
                    "Exit"
                ]
                questions = [
                    inquirer.List(
                        "action",
                        message=f"Please select the table name to truncate ({
                            cli.data_config_file}):",
                        choices=table_names,
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers["action"]
                if table_name == "Exit":
                    continue
                cli.truncate_table(env, table_name)

            elif action == "generate_and_insert":
                table_names = [table["name"] for table in cli.data_config["tables"]] + [
                    "Exit"
                ]
                questions = [
                    inquirer.List(
                        "action",
                        message="Please select the table name for the INSERT operation",
                        choices=table_names,
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers["action"]
                if table_name == "Exit":
                    continue
                cli.generate_and_insert(env, table_name)

            elif action == "generate_and_output":
                table_names = [table["name"] for table in cli.data_config["tables"]] + [
                    "Exit"
                ]
                questions = [
                    inquirer.List(
                        "action",
                        message="Please select the table name for file creation",
                        choices=table_names,
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers["action"]
                if table_name == "Exit":
                    continue
                cli.generate_and_output(env, table_name)

            elif action == "load_file":
                table_names = [table["name"] for table in cli.data_config["tables"]] + [
                    "Exit"
                ]
                questions = [
                    inquirer.List(
                        "action",
                        message="Please select the table name to load into the database",
                        choices=table_names,
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers["action"]
                if table_name == "Exit":
                    continue

                data_dir = os.path.join(cli.cdir, "../data")
                files = os.listdir(data_dir)
                db_type = cli.db_config[env].get("type")
                if db_type != "dynamodb":
                    files = [f for f in files if f.endswith(".csv")] + ["Exit"]
                else:
                    files = [f for f in files if f.endswith(".json")] + ["Exit"]

                if not files:
                    logging.error("No data files found in the /data directory.")
                    continue

                questions = [
                    inquirer.List(
                        "action",
                        message="Please select the file to load into the database (/data)",
                        choices=files,
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers["action"] == "Exit":
                    continue
                file_path = os.path.join(data_dir, answers["action"])
                cli.load_file(env, table_name, file_path)

            elif action == "switch_env":
                env = cli.switch_env()

            elif action == "switch_data_config":
                cli.switch_data_config()

            elif action == "exit":
                logging.info("Exiting fountain-flow.")
                break

        except Exception:
            logging.exception("The operation failed.")


if __name__ == "__main__":
    fire.Fire(main)
