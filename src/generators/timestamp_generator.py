import logging
import random
from datetime import datetime, timedelta, timezone

from generators.generator import ValueGenerator


class TimestampGenerator(ValueGenerator):
    def __init__(self, table_name, column):
        try:
            super().__init__(table_name, column)
            self.validate()
            # スタートとエンドの時間を初期化
            self.method = self.column["generation"]["method"]
            self.values = self.column["generation"].get("values", None)
            self.start = self.parse_datetime(self.column["generation"]["start"])
            self.end = (
                self.parse_datetime(self.column["generation"]["end"])
                if "end" in self.column["generation"]
                else None
            )
            self.current_value = None
            self.interval = timedelta(
                seconds=self.column["generation"].get("interval", 10)
            )
        except Exception as e:
            raise e

    def validate(self):
        try:
            errors = super().validate()
            generation = self.column.get("generation", {})
            start = generation.get("start", None)
            end = generation.get("end", None)
            method = generation.get("method", None)

            if "values" not in generation and not start:
                errors.append("'values' or 'start' is required for timestamp type")

            if method == "random":
                if not start or not end:
                    errors.append("'random' method needs 'start' and 'end'.")

            if method == "sequence" and not start:
                errors.append("'sequence' method needs 'start'.")

            if start and end:
                start_dt = self.parse_datetime(start)
                end_dt = self.parse_datetime(end)
                if start_dt.tzinfo != end_dt.tzinfo:
                    errors.append("'start' and 'end' must have the same timezone.")

            self.handle_errors(errors)
        except Exception as e:
            raise e

    def parse_datetime(self, datetime_str):
        try:
            if datetime_str.endswith("Z"):
                return datetime.fromisoformat(datetime_str.rstrip("Z")).replace(
                    tzinfo=timezone.utc
                )
            else:
                dt = datetime.fromisoformat(datetime_str)
                return dt if dt.tzinfo else dt.replace(tzinfo=None)
        except Exception as e:
            logging.error(f"Error parsing datetime string '{datetime_str}': {e}")
            raise e

    def generate(self):
        try:
            if self.method == "sequence":
                if self.values is not None:
                    result = self.values[self.value_index % len(self.values)]
                    self.value_index += 1
                    return result
                if self.current_value is None:
                    self.current_value = self.get_start_value()
                else:
                    if self.end and self.current_value + self.interval > self.end:
                        self.current_value = (
                            self.start
                        )  # エンドに達したらスタートにリセット
                    else:
                        self.current_value += self.interval
                next_value = self.current_value

            elif self.method == "random":
                if self.values is not None:
                    self.current_value = self.values[
                        random.randint(0, len(self.values) - 1)
                    ]
                else:
                    delta_seconds = int((self.end - self.start).total_seconds())
                    random_seconds = random.randint(0, delta_seconds)
                    self.current_value = self.start + timedelta(seconds=random_seconds)
                next_value = self.current_value
            return next_value
        except Exception as e:
            logging.error(f"Error generating timestamp: {e}")
            raise e

    def get_start_value(self):
        if self.start is not None:
            return self.start
        else:
            logging.error(f"{self.column['name']} cannot get start value.")
            raise
