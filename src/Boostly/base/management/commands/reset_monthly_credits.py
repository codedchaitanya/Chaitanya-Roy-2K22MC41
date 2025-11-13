from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.models import CreditBalance
from datetime import datetime, timedelta
import calendar


class Command(BaseCommand):
    help = 'Reset monthly credits for all students. Carries forward up to 50 unused credits.'

    def handle(self, *args, **options):
        current_date = datetime.now().date()
        reset_count = 0
        carried_forward_count = 0

        # Get all students with credit balances
        for balance in CreditBalance.objects.all():
            # Check if we need to reset (based on last reset date)
            last_reset = balance.last_reset_date
            
            # Check if we're in a new month
            if last_reset.month != current_date.month or last_reset.year != current_date.year:
                # Calculate carry-forward (up to 50 unused credits)
                unused_credits = balance.available_credits - balance.monthly_sent
                carry_forward = min(unused_credits, 50) if unused_credits > 0 else 0
                
                # Reset
                balance.available_credits = 100 + carry_forward
                balance.monthly_sent = 0
                balance.last_reset_date = current_date
                balance.save()
                
                reset_count += 1
                if carry_forward > 0:
                    carried_forward_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Reset {balance.student.username}: '
                            f'100 credits + {carry_forward} carried forward'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Reset {balance.student.username}: 100 credits')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal reset: {reset_count} students, '
                f'{carried_forward_count} had carry-forwards'
            )
        )
