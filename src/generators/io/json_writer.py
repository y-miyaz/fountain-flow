import json
import logging
import os
from datetime import datetime


class JSONWriter:
    def __init__(self, config, data_config) -> None:
        try:
            json_settings = config['settings']['data_generation']['json']
            self.headers = [column['name']
                            for column in data_config['columns']]
            self.dir = json_settings.get('file_path', 'data')
            self.filename = self._generate_filename(data_config['name'])
            self.file_path = os.path.join(self.dir, self.filename)
        except Exception:
            raise

    def _generate_filename(self, table_name: str):
        # 現在の日時を取得してファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}_{table_name}.json"

    def save_to_json(self, data):
        # 出力ディレクトリが存在するか確認し、なければ作成
        try:
            os.makedirs(self.dir, exist_ok=True)
            # 'a'モードでファイルを開いて追記
            with open(self.file_path, 'a', encoding='utf-8') as json_file:
                for item in data:
                    json_line = json.dumps(item, ensure_ascii=False) + '\n'
                    json_file.write(json_line)
        except Exception as error:
            logging.error(f"Error saving to JSON: {error}")
            raise
