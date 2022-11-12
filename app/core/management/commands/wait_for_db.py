# wait for database availability
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """ Command to make Django wait for the database """

    def handle(self, *args, **options):
        """ Entry point for command. """
        self.stdout.write('Waiting for database...')
        db_ready = False
        while db_ready is False:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, retrying...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS(
            'Database connection successful!'))
