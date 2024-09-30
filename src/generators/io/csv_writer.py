import csv
import logging
import os
from datetime import datetime


class CSVWriter:
    def __init__(self, config, data_config) -> None:
        csv_settings = config["settings"]["data_generation"]["csv"]
        self.headers = [column["name"] for column in data_config["columns"]]
        self.dir = csv_settings.get("file_path", "data")
        self.delimiter = csv_settings.get("delimiter", ",")
        self.include_headers = csv_settings.get("include_headers", False)
        self.filename = self._generate_filename(data_config["name"])
        # スクリプトの場所を取得
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # data ディレクトリの絶対パスを構築
        data_dir = os.path.join(script_dir, "../../../data")
        self.file_path = os.path.join(data_dir, self.filename)

    def _generate_filename(self, table_name: str):
        # 現在の日時を取得してファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}_{table_name}.csv"

    def save_to_csv(self, data):
        # 出力ディレクトリが存在するか確認し、なければ作成
        try:
            os.makedirs(self.dir, exist_ok=True)

            with open(self.file_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter)
                if self.include_headers and self.headers:
                    writer.writerow(self.headers)
                    self.include_headers = False
                writer.writerows(data)
        except Exception as e:
            logging.error("Error saving to CSV.")
            raise e
