import logging


def get_log_level(level_name):
    level = getattr(logging, level_name.upper(), None)
    if isinstance(level, int):
        return level
    else:
        raise ValueError(f"Invalid log level: {level_name}")


def setup_logging(level_name):
    class CustomFormatter(logging.Formatter):
        grey = "\x1b[38;21m"
        green = "\x1b[32;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        FORMATS = {
            logging.DEBUG: grey + "%(asctime)s - %(levelname)s - %(message)s" + reset,
            logging.INFO: green + "%(asctime)s - %(levelname)s - %(message)s" + reset,
            logging.WARNING: yellow
            + "%(asctime)s - %(levelname)s - %(message)s"
            + reset,
            logging.ERROR: red + "%(asctime)s - %(levelname)s - %(message)s" + reset,
            logging.CRITICAL: bold_red
            + "%(asctime)s - %(levelname)s - %(message)s"
            + reset,
        }

        def format(self, record):
            # ログフォーマットを設定
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            # メッセージをフォーマット
            formatted = formatter.format(record)
            # 例外情報を追加しない
            return formatted

    # ログハンドラの設定
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    # ロガーの設定
    logger = logging.getLogger()
    level = get_log_level(level_name)
    logger.setLevel(level)
    logger.handlers.clear()  # 重複を避けるため既存のハンドラをクリア
    logger.addHandler(handler)
