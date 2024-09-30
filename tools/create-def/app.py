import logging
import os
import sys
import traceback

from definition_generator import (
    classify_type,
    create_data_definitions,
    get_ddl_definition,
)
from format.custom_fomatter import setup_logging

# ログ設定
# logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')
setup_logging('INFO')
# app.py のあるディレクトリを絶対パスで取得
base_dir = os.path.dirname(os.path.abspath(__file__))

# カレントディレクトリを app.py のディレクトリに変更
os.chdir(base_dir)


def main():
    try:
        # コマンドライン引数を取得（最初の引数はスクリプトのファイル名なので除外）
        file_pathes = sys.argv[1:]
        if not file_pathes:
            raise e ValueError('No file specified.')
        table_names = []
        tables = []
        for file_path in file_pathes:
            table_info = get_ddl_definition(file_path)
            table_info = classify_type(table_info)
            if table_info['name'] not in table_names:
                table_names.append(table_info['name'])
                tables.append(table_info)
            else:
                logging.error(
                    f"The table definition is duplicated: \ntable_name: {table_info['name']}\nfile_path: {file_path}")
                raise e ValueError()
        create_data_definitions(tables)
        logging.info(
            'Create data definition successfully.\nfile_path: def/data.yaml')
    except Exception as error:
        logging.error(f'Application finished with errors: {error}')


if __name__ == "__main__":
    main()
