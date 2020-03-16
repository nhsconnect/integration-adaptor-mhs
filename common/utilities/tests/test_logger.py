import io
import logging
import time
from unittest import TestCase
from unittest.mock import patch

from utilities import integration_adaptors_logger as log, config


@patch("utilities.config.config", new={'LOG_LEVEL': 'INFO'})
class TestLogger(TestCase):

    def tearDown(self) -> None:
        logging.getLogger().handlers = []
        log.message_id.set(None)
        log.correlation_id.set(None)
        log.interaction_id.set(None)
        log.inbound_message_id.set(None)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_custom_audit_level(self, mock_stdout):
        mock_stdout.truncate(0)

        log.configure_logging()
        log.correlation_id.set('2')
        log.IntegrationAdaptorsLogger('TES').audit('Some audit message with %s %s', 'additional', 'parameters')

        output = mock_stdout.getvalue()
        log_entry = LogEntry(output)
        self.assertEqual('2', log_entry.correlation_id)
        self.assertEqual('AUDIT', log_entry.level)
        self.assertIn('Some audit message with additional parameters', log_entry.message)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_log_level_threshold(self, mock_stdout):
        mock_stdout.truncate(0)

        config.config['LOG_LEVEL'] = 'AUDIT'
        log.configure_logging()
        log.IntegrationAdaptorsLogger('TES').info('Test message')
        config.config['LOG_LEVEL'] = 'INFO'

        output = mock_stdout.getvalue()
        self.assertEqual("", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_name_can_be_empty(self, mock_stdout):
        mock_stdout.truncate(0)

        log.configure_logging()

        log.IntegrationAdaptorsLogger('SYS').info('%s %s', 'yes', 'no')

        log_entry = LogEntry(mock_stdout.getvalue())
        self.assertEqual('SYS', log_entry.name)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_message_format_and_log_entry_parts(self, mock_stdout):
        mock_stdout.truncate(0)

        log.configure_logging('TEST')
        log.message_id.set('10')
        log.correlation_id.set('15')
        log.inbound_message_id.set('20')
        log.interaction_id.set('25')

        log.IntegrationAdaptorsLogger('SYS').info('%s %s', 'yes', 'no')

        log_entry = LogEntry(mock_stdout.getvalue())

        self.assertEqual('10', log_entry.message_id)
        self.assertEqual('15', log_entry.correlation_id)
        self.assertEqual('20', log_entry.inbound_message_id)
        self.assertEqual('25', log_entry.interaction_id)
        self.assertEqual('TEST.SYS', log_entry.name)
        self.assertEqual('INFO', log_entry.level)
        self.assertEqual('yes no', log_entry.message)
        time.strptime(log_entry.time, '%Y-%m-%dT%H:%M:%S.%fZ')

    @patch('utilities.config.get_config')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_should_log_critical_message_if_log_level_is_below_info(self, mock_stdout, mock_config):
        unsafe_log_levels = ['NOTSET', 'DEBUG']
        for level in unsafe_log_levels:
            mock_stdout.truncate(0)
            with self.subTest(f'Log level {level} should result in critical log message being logged out'):
                mock_config.return_value = level
                log.configure_logging()
                output = mock_stdout.getvalue()
                log_entry = LogEntry(output)
                self.assertEqual('CRITICAL', log_entry.level)
                self.assertEqual(f'The current log level ({level}) is set below INFO level,'
                                 f' it is known that libraries used '
                                 'by this application sometimes log out clinical patient data at DEBUG level. '
                                 'The log level provided MUST NOT be used in a production environment.',
                                 log_entry.message)

    @patch('utilities.config.get_config')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_should_not_log_critical_message_if_log_level_is_above_debug(self, mock_stdout, mock_config):
        safe_log_levels = ['INFO', 'AUDIT', 'WARNING', 'ERROR', 'CRITICAL']
        for level in safe_log_levels:
            with self.subTest(f'Log level {level} should not result in critical log message being logged out'):
                mock_config.return_value = level
                log.configure_logging()
                output = mock_stdout.getvalue()
                self.assertEqual('', output)


class LogEntry:
    def __init__(self, log_line: str):
        super().__init__()
        log_elements = log_line.split(' | ')
        (
            self.time,
            self.level,
            self.process_id,
            self.interaction_id,
            self.message_id,
            self.correlation_id,
            self.inbound_message_id,
            self.name,
            self.message
        ) = log_elements
        self.message = self.message[:-1]
