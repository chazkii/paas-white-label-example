from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from whitelabel.models import Company, CompanyAdmin


class Command(BaseCommand):
    help = "Populate database with test data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=False,
            help="Email to save to all users",
            required=True
        )

    def handle(self, *args, **options):
        email = options['email']
        c, _ = Company.objects.update_or_create(name="Acme")
        u1, _ = User.objects.update_or_create(first_name="Adam",
                                              last_name="Smith",
                                              username='asmith',
                                              is_superuser=True,
                                              is_staff=True,
                                              email=email)
        u1.set_password('password')
        u1.save()
        u1.refresh_from_db()
        u1.profile.company = c
        u1.save()

        CompanyAdmin.objects.update_or_create(user=u1, company=c)

        u2, _ = User.objects.update_or_create(first_name="Bob",
                                              last_name="Smith",
                                              username='bsmith',
                                              is_superuser=False,
                                              is_staff=False,
                                              email=email)
        u2.set_password('password')
        u2.save()
        u2.refresh_from_db()
        u2.profile.company = c
        u2.save()
        print('Added users "asmith" (admin) and "bsmith" with password "password"')

