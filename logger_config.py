import logging
import re


class PrivacyFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = re.sub(
                r'([a-zA-R0-9_.+-])[a-zA-R0-9_.+-]*@([a-zA-R0-9-]+\.[a-zA-R0-9-.]+)',
                r'\1***@\2',
                record.msg
            )
            record.msg = re.sub(
                r'(password|token|secret)\s*=\s*[^\s]+',
                r'\1=[REDACTED]',
                record.msg,
                flags=re.IGNORECASE
            )
        return True


def setup_logger():
    logger = logging.getLogger("privacy_logger")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    handler.addFilter(PrivacyFilter())

    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


privacy_logger = setup_logger()