from time import sleep

from django.core.management.base import BaseCommand
from django.core.management import call_command

from core.models import Organization, User


class Command(BaseCommand):
    help = 'Create new organization using multi-tenant system'

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str)

    def handle(self, *args, **kwargs):
        schema_name = kwargs['schema_name']

        public_orgs = Organization.objects.filter(schema_name='public')
        if schema_name != 'public' and not public_orgs.exists():
            print(f"[!] Error: 'public' organization must be created first")
            raise

        print(
            f"[+] Creating new Organization (schema_name: {schema_name}) "
            f"in 3s... (press Ctrl+C to cancel)"
        )
        sleep(3)
        org = Organization.objects.filter(schema_name=schema_name).last()
        if org:
            org.save()
            print(
                f"[i] Organization {schema_name} already exists:\n    "
                f"Organization #{org.short_id} ({org.name})"
            )
        else:
            org = Organization(
                id=None,
                schema_name=schema_name,
                name=schema_name,
            )
            org.save()
            print(
                f"[√] New organization {schema_name} created:\n    "
                f"Organization #{org.short_id} ({org.name})"
            )

        # Create tenant superuser
        if schema_name == 'public':
            print(f'[+] Creating global tenant admin tenant superuser...')
        else:
            print(f'[+] Creating {schema_name} tenant superuser...')

        user = (
            User.objects
                .filter(is_superuser=True, organization_id=org.id)
                .order_by('created')
                .last()
        )

        create_superuser = True
        if user:
            print(
                f"[i] Tenant superuser '{user.username}' already exists:\n    "
                f"User #{user.short_id} org: {user.organization}"
            )
            create_superuser =\
                input('Add another superuser? y/[n]: ')[0].lower() == 'y'

        if create_superuser:
            call_command('createsuperuser', schema='public')
            user = User.objects\
                .filter(is_superuser=True).order_by('created').last()
            assert user is not None,\
                'A user did not exist after createsuperuser ran (did it fail?)'
            user.organization_id = org.id
            user.save()
            print(
                f"[√] New tenant superuser {user.username} was created:\n    "
                f"User #{user.short_id} org: {user.organization}"
            )

        orphaned_users = list(User.objects.filter(organization_id=None))
        if orphaned_users:
            print(f"[!] Warning: Users exist without an org: {orphaned_users}")
