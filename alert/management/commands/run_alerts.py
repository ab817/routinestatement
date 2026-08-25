from django.core.management.base import BaseCommand
from alert.services import process_pending_alerts

class Command(BaseCommand):
    help = 'Checks database for unalerted transactions and sends emails.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Alert Routine...'))
        process_pending_alerts()
        self.stdout.write(self.style.SUCCESS('Alert Routine Completed.'))