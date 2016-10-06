#!/usr/bin/env python
import os
import django
from os import path
from django.conf import settings
from django.core.management import call_command

def main():
    if not settings.configured:
        module_root = path.dirname(path.realpath(__file__))

        settings.configure(
            DEBUG = False,
            INSTALLED_APPS = (
                'private_storage',
            ),
        )

    if django.VERSION >= (1,7):
        django.setup()

    makemessages()

def makemessages():
    os.chdir('private_storage')
    call_command('makemessages', locale=('en', 'nl'), verbosity=1)

if __name__ == '__main__':
    main()
