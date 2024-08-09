import logging
import os

import yaml
from db.db_connector_factory import db_connector_factory
from format.custom_fomatter import setup_logging
from generators.data_generator import DataGenerator

import inquirer
import fire

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

class FountainFlowCLI:
    def truncate_table(self, db_config, env, table_name):
       # ユーザにtruncateの確認を求める
        if db_config[env].get('type') != 'dynamodb':
            try:
                db_connector = db_connector_factory(
                    db_config, env=env)
                response = input(
                    f"\x1b[33mDo you want to truncate table '{table_name}'? (y/N): \x1b[0m")
                if response.lower() == 'y':
                    # truncateするテーブル名を指定
                    db_connector.truncate_table(table_name)
            except NotImplementedError:
                pass
            except:
                raise
        else:
            try:
                db_connector = db_connector_factory(
                    db_config, env=env)
                db_connector.truncate_table('')
            except:
                raise


    def generate_and_insert(self, config, db_config, data_config, env, table_name):
        """データを生成してレコードを挿入します。"""
        try:
            config['settings']['data_generation']['method'] = 'database'

            data_generator = DataGenerator(
                config, db_config, data_config, env)
            data_generator.generate_data(table_name)
        except NotImplementedError:
            pass

    def generate_and_output(self, config, db_config, data_config, env, table_name):
        """データを生成してファイルに出力します。"""
        try:
            if db_config[env].get('type') != 'dynamodb':
                config['settings']['data_generation']['method'] = 'csv'
            else:
                config['settings']['data_generation']['method'] = 'json'
            data_generator = DataGenerator(
                config, db_config, data_config, env)
            data_generator.generate_data(table_name)
        except NotImplementedError:
            pass

    def load_file(self, config, db_config, data_config, env, table_name, file_path):
        """ファイルを読み込みます。"""
        try:
            if db_config[env].get('type') != 'dynamodb':
                config['settings']['data_generation']['method'] = 'csv'
            else:
                config['settings']['data_generation']['method'] = 'json'
            data_generator = DataGenerator(
                config, db_config, data_config, env)
            if db_config.get(env)['type'] == 'dynamodb':
                data_generator.load_json_data(table_name, file_path)
            else:
                response = input("Does the CSV file include headers? (y/N): ")
                if response.lower() == 'y':
                    include_headers = True
                else:
                    include_headers = False
                data_generator.load_csv_data(table_name, file_path, include_headers)
        except NotImplementedError:
            pass

    def switch_env(self, db_config):
        """ファイルを読み込みます。"""
        envs = db_config.keys()
        questions = [
            inquirer.List(
                'action',
                message="Please select the connection environment.(database.yaml)",
                choices=envs
            ),
        ]
        answers = inquirer.prompt(questions)
        selected_env = answers['action']
        return selected_env

cdir = os.path.dirname(__file__)
config = load_config(cdir + '/../config/settings.yaml')
db_config = load_config(cdir + '/../config/database.yaml')
data_config = load_config(cdir + '/../def/data.yaml')
log_level = config['settings']['logging'].get('level', 'INFO')
setup_logging(log_level)

cli = FountainFlowCLI()

def main():
    
    env = cli.switch_env(db_config)

    while True:
        try:
            questions = [
                inquirer.List(
                    'action',
                    message=f"Please select an option.(env={env})",
                    choices=[
                        ('Truncate Table', 'truncate_table'),
                        ('Generate Data & Insert Records', 'generate_and_insert'),
                        ('Generate Data & File Output', 'generate_and_output'),
                        ('Load File', 'load_file'),
                        ('Switch Env', 'switch_env'),                    
                        ('Exit', 'exit')
                    ]
                ),
            ]

            answers = inquirer.prompt(questions)

            if answers['action'] == 'truncate_table':
                table_names = [table['name'] for table in data_config['tables']] + ['Exit']
                questions = [
                    inquirer.List(
                        'action',
                        message="Please select the table name to truncate.(data.yaml)",
                        choices=table_names
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers['action']
                if table_name == 'Exit':
                    continue
                cli.truncate_table(db_config, env, table_name)
            elif answers['action'] == 'generate_and_insert':
                table_names = [table['name'] for table in data_config['tables']] + ['Exit']
                questions = [
                    inquirer.List(
                        'action',
                        message="Please select the table name for the INSERT operation.(data.yaml)",
                        choices=table_names
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers['action']
                if table_name == 'Exit':
                    continue
                cli.generate_and_insert(config, db_config, data_config, env, table_name)
            elif answers['action'] == 'generate_and_output':
                table_names = [table['name'] for table in data_config['tables']] + ['Exit']
                questions = [
                    inquirer.List(
                        'action',
                        message="Please select the table name for file creation.(data.yaml)",
                        choices=table_names
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers['action']
                if table_name == 'Exit':
                    continue
                cli.generate_and_output(config, db_config, data_config, env, table_name)
            elif answers['action'] == 'load_file':
                table_names = [table['name'] for table in data_config['tables']] + ['Exit']
                questions = [
                    inquirer.List(
                        'action',
                        message="Please select the table name to load into the database.(data.yaml)",
                        choices=table_names
                    ),
                ]
                answers = inquirer.prompt(questions)
                table_name = answers['action']
                if table_name == 'Exit':
                    continue
                # スクリプトの場所を取得
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # data ディレクトリの絶対パスを構築
                data_dir = os.path.join(script_dir, '../data')
                # ディレクトリ内のファイル名一覧を取得
                files = os.listdir(data_dir)
                # csvとjsonファイルのみにフィルタリング
                if db_config[env].get('type') != 'dynamodb':
                    files = [f for f in files if f.endswith('.csv')] + ['Exit']
                else:
                    files = [f for f in files if f.endswith('.json')] + ['Exit']

                questions = [
                    inquirer.List(
                        'action',
                        message="Please select the file to load into the database.(/data)",
                        choices=files
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers['action'] == 'Exit':
                    continue
                file_path = data_dir + '/' + answers['action']
                cli.load_file(config, db_config, data_config, env, table_name, file_path)
            elif answers['action'] == 'switch_env':
                env = cli.switch_env(db_config)
            elif answers['action'] == 'exit':
                logging.info("exit fountain-flow.")
                break
        except Exception:
            logging.exception('The operation failed.')

            
if __name__ == '__main__':
    fire.Fire(main)
