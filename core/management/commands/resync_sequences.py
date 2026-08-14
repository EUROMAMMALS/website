from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = (
        "Reset PostgreSQL sequences to the next available value for every table, "
        "including auto-created ManyToMany through tables. Use this when an "
        "INSERT in the admin fails with a duplicate key because a sequence got "
        "out of sync with the max id of the table."
    )

    def handle(self, *args, **options):
        tables = {}
        for model in apps.get_models():
            tables[model._meta.db_table] = model._meta.pk
            for field in model._meta.many_to_many:
                through = field.remote_field.through
                if through is not None and through._meta.db_table not in tables:
                    tables[through._meta.db_table] = through._meta.pk

        resynced = []
        with connection.cursor() as cursor:
            for table, pk in tables.items():
                cursor.execute(
                    "SELECT pg_get_serial_sequence(%s, %s)",
                    [table, pk.column],
                )
                sequence = cursor.fetchone()[0]
                if not sequence:
                    continue
                column = connection.ops.quote_name(pk.column)
                quote_table = connection.ops.quote_name(table)
                cursor.execute(
                    "SELECT setval(%s, GREATEST((SELECT COALESCE(MAX({column}), 0) "
                    "FROM {table}) + 1, 1), false)".format(
                        column=column, table=quote_table
                    ),
                    [sequence],
                )
                resynced.append((table, sequence))

        self.stdout.write(self.style.SUCCESS("Resynced {} sequences.".format(len(resynced))))
        for table, sequence in sorted(resynced):
            self.stdout.write("  {} -> {}".format(table, sequence))
