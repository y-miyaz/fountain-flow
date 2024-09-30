import logging


def get_log_level(level_name):
    level = getattr(logging, level_name.upper(), None)
    if isinstance(level, int):
        return level
    else:
        raise ValueError(f"Invalid log level: {level_name}")


def setup_logging(level_name):
    class CustomFormatter(logging.Formatter):
        # カラーコードの定義
        grey = "\x1b[38;21m"
        green = "\x1b[32;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        def __init__(self):
            super().__init__()
            # レベルごとのフォーマットを定義
            format_strings = {
                logging.DEBUG: self.grey
                + "%(asctime)s - %(levelname)s - %(message)s"
                + self.reset,
                logging.INFO: self.green
                + "%(asctime)s - %(levelname)s - %(message)s"
                + self.reset,
                logging.WARNING: self.yellow
                + "%(asctime)s - %(levelname)s - %(message)s"
                + self.reset,
                logging.ERROR: self.red
                + "%(asctime)s - %(levelname)s - %(message)s"
                + self.reset,
                logging.CRITICAL: self.bold_red
                + "%(asctime)s - %(levelname)s - %(message)s"
                + self.reset,
            }
            self.formatters = {}
            for level, fmt in format_strings.items():
                # 各レベルのフォーマッタを作成
                formatter = logging.Formatter(fmt)
                # formatExceptionメソッドをカスタマイズ
                formatter.formatException = self.formatException
                self.formatters[level] = formatter

        def formatException(self, ei):
            import traceback

            # 例外のメッセージ部分のみを取得
            exception_only = traceback.format_exception_only(ei[0], ei[1])
            return "".join(exception_only).strip()

        def format(self, record):
            # 該当のログレベルのフォーマッタを取得
            formatter = self.formatters.get(record.levelno)
            if formatter is None:
                # デフォルトのフォーマッタを使用
                formatter = self.formatters[logging.INFO]
            # レコードをフォーマット
            return formatter.format(record)

    # ログハンドラの設定
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    # ロガーの設定
    logger = logging.getLogger()
    level = get_log_level(level_name)
    logger.setLevel(level)
    logger.handlers.clear()  # 既存のハンドラをクリア
    logger.addHandler(handler)
