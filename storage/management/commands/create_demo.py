from django.core.management.base import BaseCommand

from storage.models import Organization, User


class Command(BaseCommand):
    help = 'Create demo organizations and users'

    def handle(self, *args, **options):
        org1, _ = Organization.objects.get_or_create(name='Org A')
        org2, _ = Organization.objects.get_or_create(name='Org B')

        if not User.objects.filter(username='alice').exists():
            u = User.objects.create_user('alice', password='password')
            u.organization = org1
            u.save()

        if not User.objects.filter(username='bob').exists():
            u = User.objects.create_user('bob', password='password')
            u.organization = org2
            u.save()

        self.stdout.write(self.style.SUCCESS('Demo organizations and users created.'))
