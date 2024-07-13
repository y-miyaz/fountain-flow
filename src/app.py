import argparse
import logging
import os

import yaml
from db.db_connector_factory import db_connector_factory
from format.custom_fomatter import setup_logging
from generators.data_generator import DataGenerator


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def main():
    try:
        parser = argparse.ArgumentParser(description="Run the application.")

        parser.add_argument('--env', type=str, default='default',
                            help='Environment to use for database connections.')
        args = parser.parse_args()
        cdir = os.path.dirname(__file__)
        config = load_config(cdir + '/../config/settings.yaml')
        db_config = load_config(cdir + '/../config/database.yaml')
        data_config = load_config(cdir + '/../def/data.yaml')
        log_level = config['settings']['logging'].get('level', 'INFO')

        setup_logging(log_level)

        # ユーザにtruncateの確認を求める
        if db_config[args.env].get('type') != 'dynamodb':
            try:
                db_connector = db_connector_factory(
                    db_config, env=args.env)
                for table in data_config['tables']:
                    response = input(
                        f"\x1b[33mDo you want to truncate table '{table['name']}' before generating data? (y/N): \x1b[0m")
                    if response.lower() == 'y':
                        # truncateするテーブル名を指定
                        db_connector.truncate_table(table['name'])
            except:
                raise
        else:
            try:
                db_connector = db_connector_factory(
                    db_config, env=args.env)
                for idx, table in enumerate(data_config['tables']):
                    # truncateするテーブル名を指定
                    table_name = table['name']
                    if db_connector.check_table_exists(table_name):
                        response = input(
                            (f"\x1b[33mTable name '{table_name}' already exists.\n"
                             'Do you allow to drop the table before generating data? (y/N): \x1b[0m'))
                        if response.lower() == 'y':
                            if table_name == db_config[args.env].get('source_table'):
                                response = input(
                                    (f"\x1b[33mTable name '{table_name}' is the same table as source table.\n"
                                     'Do you really allow to drop the table? (y/N): \x1b[0m'))
                                if response.lower() == 'y':
                                    db_connector.drop_table(table_name)
                                else:
                                    logging.exception(
                                        f"Skip data generation for table '{table_name}'.")
                            else:
                                db_connector.drop_table(table_name)
                        else:
                            logging.info(
                                f"Skip data generation for table '{table_name}'.")
                            del data_config['tables'][idx]
            except:
                raise
        data_generator = DataGenerator(
            config, db_config, data_config, args.env)
        data_generator.generate_data()
        logging.info('Application successfully finished.')
    except Exception as error:
        logging.error(f'Application finished with errors: {error}')


if __name__ == "__main__":
    main()
