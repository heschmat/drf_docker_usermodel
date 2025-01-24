"""
Django custom command to make sure app waits till the DB is ready.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2OpErr


class Command(BaseCommand):
    """Wait for DB till it's up and running."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpErr, OperationalError):
                self.stdout.write('Database unavailable, waiting for 1 second...')
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS('+++ Database Available! +++'))
