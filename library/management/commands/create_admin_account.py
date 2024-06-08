from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create admin account"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the admin account')
        parser.add_argument('--email', type=str, help='Email for the admin account')
        parser.add_argument('--password', type=str, help='Password for the admin account')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if not (username and email and password):
            self.stderr.write(self.style.ERROR('Please provide username, email, and password'))
            return

        try:
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS('Admin account successfully created'))
            else:
                self.stderr.write(self.style.ERROR('Admin account already exists'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to create admin account: {str(e)}'))
