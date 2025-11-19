from mylogger import logger


def main():
    logger.debug("debug")
    logger.info("info", extra={"x": "some extra info"})
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")


if __name__ == '__main__':
    main()
