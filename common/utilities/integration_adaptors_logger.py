import contextvars
import datetime as dt
import logging
import sys
from logging import LogRecord
from typing import Optional, Any

from utilities import config

AUDIT = 25
LOG_FORMAT_STRING = "%(asctime)sZ | %(levelname)s | %(process)d | %(interaction_id)s | %(message_id)s " \
                    "| %(correlation_id)s | %(inbound_message_id)s | %(name)s | %(message)s"

message_id: contextvars.ContextVar[str] = contextvars.ContextVar('message_id', default='')
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='')
inbound_message_id: contextvars.ContextVar[str] = contextvars.ContextVar('inbound_message_id', default='')
interaction_id: contextvars.ContextVar[str] = contextvars.ContextVar('interaction_id', default='')


def _check_for_insecure_log_level(log_level: str):
    integer_level = logging.getLevelName(log_level)
    if integer_level < logging.INFO:
        logger = IntegrationAdaptorsLogger(__name__)
        logger.critical('The current log level (%s) is set below INFO level, it is known that libraries used '
                        'by this application sometimes log out clinical patient data at DEBUG level. '
                        'The log level provided MUST NOT be used in a production environment.',
                        log_level)


class IntegrationAdaptorsLogger(logging.LoggerAdapter):
    """
    Allows using dictonaries to format message
    """
    def __init__(self, name: str):
        super().__init__(logging.getLogger(name), extra=None)

    def log(self, level: int, msg: Any, *args: Any, **kwargs: Any) -> None:
        msg = self._format_using_custom_params(msg, kwargs)
        super().log(level, msg, *args, **kwargs)

    def audit(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(AUDIT):
            self.log(AUDIT, msg, *args, **kwargs)

    def _format_using_custom_params(self, msg: str, kwargs: dict) -> str:
        if "fparams" in kwargs:
            msg = self._formatted_string(msg, kwargs["fparams"])
            del kwargs["fparams"]
        return msg

    def _format_values_in_map(self, dict_values: dict) -> dict:
        """
        Replaces the values in the map with key=value so that the key in a string can be replaced with the correct
        log format, also surrounds the value with quotes if it contains spaces and removes spaces from the key
        """
        new_map = {}
        for key, value in dict_values.items():
            value = str(value)
            if ' ' in value:
                value = f'"{value}"'

            new_map[key] = f"{key.replace(' ', '')}={value}"
        return new_map

    def _formatted_string(self, message: str, dict_values: dict) -> str:
        """
        Populates the string with the correctly formatted dictionary values
        """
        formatted_values = self._format_values_in_map(dict_values)
        return message.format(**formatted_values)


class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt=LOG_FORMAT_STRING, datefmt='%Y-%m-%dT%H:%M:%S.%f')

    def format(self, record: LogRecord) -> str:
        record.message_id = message_id.get()
        record.correlation_id = correlation_id.get()
        record.inbound_message_id = inbound_message_id.get()
        record.interaction_id = interaction_id.get()
        return super().format(record)

    def formatTime(self, record: LogRecord, datefmt: Optional[str] = ...) -> str:
        converter = dt.datetime.utcfromtimestamp
        ct = converter(record.created)
        s = ct.strftime(datefmt)
        return s


def configure_logging():
    """
    A general method to load the overall config of the system, specifically it modifies the root handler to output
    to stdout and sets the default log levels and format. This is expected to be called once at the start of a
    application.
    """
    logging.addLevelName(AUDIT, "AUDIT")
    logger = logging.getLogger()
    log_level = config.get_config('LOG_LEVEL')
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)

    formatter = CustomFormatter()

    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    _check_for_insecure_log_level(log_level)
