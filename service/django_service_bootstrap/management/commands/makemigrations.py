# coding: utf-8
# Original source from: https://gist.github.com/r3m0t/f4e1388f8412404a990f2c776fb48b44
"""Cause git to detect a merge conflict when two branches have migrations."""
from __future__ import absolute_import, unicode_literals

import io
import os

from django.conf import settings
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.db.migrations.loader import MigrationLoader


# note: if you use django-migrate-sql, you will want to use:
# from migrate_sql.management.commands.makemigrations import Command as MakeMigrationsCommand
# note: for this to work, 'myapp' must be *above* 'migrate-sql' in settings.INSTALLED_APPS


class Command(MakeMigrationsCommand):
    """Cause git to detect a merge conflict when two branches have migrations."""

    def handle(self, *app_labels, **options):
        super(Command, self).handle(*app_labels, **options)
        loader = MigrationLoader(None, ignore_no_migrations=True)

        latest_migration_by_app = {}
        for migration in loader.disk_migrations.values():
            name = migration.name
            app_label = migration.app_label
            latest_migration_by_app[app_label] = max(latest_migration_by_app.get(app_label, ""), name)

        result = "# File generated by myapp.management.commands.makemigrations.Command#handle\n"
        result += "\n".join(
            "{}: {}".format(app_label, name) for app_label, name in sorted(latest_migration_by_app.items())
        )

        with io.open(os.path.join(settings.BASE_DIR, "latest_migrations.txt"), "w") as f:
            f.write(result)