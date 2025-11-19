import json
import logging.config
import pathlib
import os
logger = logging.getLogger("my_app")


def setup_logging():
    config_file = pathlib.Path("logging_configs/common_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
        if (log_filename := config.get("handlers",{}).get("file",{}).get("filename",None)) is not None:
            if not os.path.exists((log_dir:= os.path.dirname(log_filename))):
                os.makedirs(log_dir)
    logging.config.dictConfig(config)


def main():
    setup_logging()
    logger.debug("debug")
    logger.info("info",extra={"x":"some extra info"})
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

if __name__ == '__main__':
    main()
