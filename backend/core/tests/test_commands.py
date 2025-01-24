"""
Test suit for custom Django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpErr

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class MgmtCmdTest(SimpleTestCase):
    """Test management commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test wait_for_db if database is ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test wit_for_db when getting operational error (db not ready yet)."""
        # The 6th time we call the db, we get True (i.e, db is ready)
        # Before that it raises various exceptions.
        patched_check.side_effect = [Psycopg2OpErr] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)

        patched_check.assert_called_with(databases=['default'])
