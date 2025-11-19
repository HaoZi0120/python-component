import atexit
import datetime as dt
import json
import logging
import logging.config
import os
import pathlib
from typing import override

LOG_RECORD_BUILTIN_ATTRS = {"args",
                            "asctime",
                            "created",
                            "exc_info",
                            "exc_text",
                            "filename",
                            "funcName",
                            "levelname",
                            "levelno",
                            "lineno",
                            "module",
                            "msecs",
                            "message",
                            "msg",
                            "name",
                            "pathname",
                            "process",
                            "processName",
                            "relativeCreated",
                            "stack_info",
                            "thread",
                            "threadName",
                            "taskName"}


class MyJSONFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None, ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)
        message = {
            key: msg_val if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val) for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val
        return message

class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


class AppLogger:
    _instance = None
    _config_path = None  # 类变量存储配置路径

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 设置配置路径（如果提供了参数）
            if config_path is not None:
                cls._config_path = pathlib.Path(config_path)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        self.logger = logging.getLogger('my_app')
        # 使用类变量中的配置路径
        if self._config_path is None:
            # 默认配置路径
            config_file = pathlib.Path("logging_configs/queue_config.json")
        else:
            config_file = self._config_path
        with open(config_file) as f_in:
            config = json.load(f_in)
            if (log_filename := config.get("handlers", {}).get("file", {}).get("filename", None)) is not None:
                if not os.path.exists((log_dir := os.path.dirname(log_filename))):
                    os.makedirs(log_dir)
        logging.config.dictConfig(config)

        queue_handler = logging.getHandlerByName("queue")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)

    def get_logger(self):
        return self.logger


# 创建单例实例
# 默认使用QueueHandler
# 可通过更改配置文件路径替换日志记录方案
logger = AppLogger("logging_configs/queue_config.json").get_logger()
# logger = AppLogger("../logging_configs/common_config.json").get_logger()